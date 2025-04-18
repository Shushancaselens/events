import streamlit as st
import re
import difflib
import base64
from pathlib import Path
import json
import PyPDF2
import docx
from collections import Counter

# Set up page configuration
st.set_page_config(page_title="Sports Arbitration Smart Search", layout="wide")

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = {}
if 'document_content' not in st.session_state:
    st.session_state.document_content = {}
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'compare_results' not in st.session_state:
    st.session_state.compare_results = []
if 'legal_concepts' not in st.session_state:
    # Pre-populated with common legal terms and their variations
    st.session_state.legal_concepts = {
        "sporting succession": ["sport succession", "sporting rights", "club identity", 
                              "transfer of membership", "succession of sporting rights"],
        "force majeure": ["act of god", "unforeseen circumstances", "unavoidable accident", 
                        "superior force", "exceptional circumstance"],
        "contractual breach": ["breach of contract", "contractual violation", 
                             "non-performance", "contract infringement"]
    }

# Document processing functions
def extract_text_from_pdf(file_content):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file_content)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_content):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(file_content)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return ""

def process_uploaded_file(uploaded_file):
    """Process uploaded file and extract text"""
    try:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        if file_extension == "pdf":
            return extract_text_from_pdf(uploaded_file)
        elif file_extension in ["docx", "doc"]:
            return extract_text_from_docx(uploaded_file)
        elif file_extension == "txt":
            return uploaded_file.read().decode("utf-8")
        else:
            st.error(f"Unsupported file format: {file_extension}")
            return ""
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return ""

def extract_citations(text):
    """Extract exhibit references and citations from text"""
    citations = []
    
    # Pattern for exhibit references
    exhibit_pattern = r'(?i)(?:exhibit|exh\.|ex\.)?\s*([A-Z0-9-]+)'
    exhibits = re.finditer(exhibit_pattern, text)
    for match in exhibits:
        citations.append({
            'type': 'exhibit',
            'id': match.group(1),
            'text': match.group(0),
            'position': match.start(),
            'context': text[max(0, match.start()-50):min(len(text), match.end()+50)]
        })
    
    # Pattern for article references
    article_pattern = r'(?i)(?:article|section|clause|art\.|§)\s+(\d+(?:\.\d+)*)'
    articles = re.finditer(article_pattern, text)
    for match in articles:
        citations.append({
            'type': 'article',
            'id': match.group(1),
            'text': match.group(0),
            'position': match.start(),
            'context': text[max(0, match.start()-50):min(len(text), match.end()+50)]
        })
    
    return citations

def extract_paragraphs(text):
    """Split text into paragraphs and analyze each"""
    paragraphs = re.split(r'\n\s*\n', text)
    processed_paragraphs = []
    
    for i, para in enumerate(paragraphs):
        if len(para.strip()) < 20:  # Skip very short paragraphs
            continue
            
        # Extract citations
        citations = extract_citations(para)
        
        # Extract legal concepts
        concepts = []
        for concept, variations in st.session_state.legal_concepts.items():
            if any(var.lower() in para.lower() for var in [concept] + variations):
                concepts.append(concept)
        
        processed_paragraphs.append({
            'index': i,
            'text': para.strip(),
            'citations': citations,
            'concepts': concepts,
            'word_count': len(para.split())
        })
    
    return processed_paragraphs

def semantic_search(query, documents, threshold=0.3):
    """Enhanced semantic search that understands concept variations"""
    results = []
    
    # Expand query with related concepts
    expanded_terms = [query.lower()]
    
    # Add concept variations if query contains known concepts
    for concept, variations in st.session_state.legal_concepts.items():
        if concept.lower() in query.lower() or any(var.lower() in query.lower() for var in variations):
            expanded_terms.extend([concept.lower()] + [v.lower() for v in variations])
    
    # Search in documents
    for doc_id, content in documents.items():
        paragraphs = extract_paragraphs(content)
        
        for para in paragraphs:
            # Score based on term overlap and concept matching
            score = 0
            para_text = para['text'].lower()
            
            # Check for direct term matches
            for term in expanded_terms:
                if term in para_text:
                    score += 0.2  # Direct match bonus
            
            # Check for sentence similarity using word overlap
            query_words = set(query.lower().split())
            para_words = set(para_text.split())
            if query_words and para_words:
                overlap = len(query_words.intersection(para_words)) / len(query_words.union(para_words))
                score += overlap
            
            # Boost score for paragraphs with citations
            if para['citations']:
                score += 0.1
                
            # Boost score for paragraphs with matching concepts
            if any(concept in para['concepts'] for concept, _ in st.session_state.legal_concepts.items()
                  if concept.lower() in query.lower()):
                score += 0.2
            
            if score >= threshold:
                results.append({
                    'doc_id': doc_id,
                    'paragraph': para,
                    'score': round(score, 3),
                    'context': content[max(0, content.find(para['text'])-100):
                                     min(len(content), content.find(para['text']) + len(para['text'])+100)]
                })
    
    # Sort by score (highest first)
    return sorted(results, key=lambda x: x['score'], reverse=True)

def compare_documents(doc1_id, doc2_id, focus_on_substance=True):
    """Compare two documents with focus on meaningful differences"""
    if doc1_id not in st.session_state.document_content or doc2_id not in st.session_state.document_content:
        return []
    
    doc1 = st.session_state.document_content[doc1_id]
    doc2 = st.session_state.document_content[doc2_id]
    
    # Extract paragraphs
    doc1_paras = extract_paragraphs(doc1)
    doc2_paras = extract_paragraphs(doc2)
    
    results = []
    
    # First, find similar paragraph pairs
    for i, para1 in enumerate(doc1_paras):
        for j, para2 in enumerate(doc2_paras):
            # Calculate similarity
            para1_text = para1['text'].lower()
            para2_text = para2['text'].lower()
            
            # Use difflib to calculate similarity ratio
            similarity = difflib.SequenceMatcher(None, para1_text, para2_text).ratio()
            
            # Only consider paragraphs that are somewhat similar
            if similarity > 0.5:
                # Find detailed differences
                d = difflib.Differ()
                diff = list(d.compare(para1['text'].splitlines(), para2['text'].splitlines()))
                
                # Format differences for display
                doc1_formatted = ""
                doc2_formatted = ""
                
                for line in diff:
                    if line.startswith('  '):  # Common line
                        doc1_formatted += line[2:] + "<br>"
                        doc2_formatted += line[2:] + "<br>"
                    elif line.startswith('- '):  # Line unique to para1
                        doc1_formatted += f"<span style='background-color: #ffcccc'>{line[2:]}</span><br>"
                    elif line.startswith('+ '):  # Line unique to para2
                        doc2_formatted += f"<span style='background-color: #ccffcc'>{line[2:]}</span><br>"
                
                # Analyze substantiveness of differences
                is_substantial = False
                
                # Check for differences in citations
                cite1_ids = set(c['id'] for c in para1['citations'])
                cite2_ids = set(c['id'] for c in para2['citations'])
                different_citations = cite1_ids != cite2_ids
                
                # Check for differences in legal concepts
                concept_diff = set(para1['concepts']) != set(para2['concepts'])
                
                # Check for differences in numbers/dates
                numbers1 = re.findall(r'\b\d+(?:\.\d+)?%?\b', para1['text'])
                numbers2 = re.findall(r'\b\d+(?:\.\d+)?%?\b', para2['text'])
                number_diff = set(numbers1) != set(numbers2)
                
                # Check for negation differences
                negations1 = re.findall(r'\b(?:not|never|no|cannot)\b', para1['text'].lower())
                negations2 = re.findall(r'\b(?:not|never|no|cannot)\b', para2['text'].lower())
                negation_diff = len(negations1) != len(negations2)
                
                # Mark as substantial if any key difference is found
                if different_citations or concept_diff or number_diff or negation_diff:
                    is_substantial = True
                
                # If focusing on substance, only include substantial differences
                if not focus_on_substance or is_substantial:
                    results.append({
                        'doc1_id': doc1_id,
                        'doc2_id': doc2_id,
                        'para1': para1,
                        'para2': para2,
                        'similarity': similarity,
                        'doc1_formatted': doc1_formatted,
                        'doc2_formatted': doc2_formatted,
                        'is_substantial': is_substantial,
                        'different_citations': different_citations,
                        'concept_diff': concept_diff,
                        'number_diff': number_diff,
                        'negation_diff': negation_diff
                    })
    
    # Sort by similarity (lowest first for most different)
    return sorted(results, key=lambda x: x['similarity'])

def extract_arguments(document, doc_id):
    """Extract arguments from document with source verification"""
    text = document
    arguments = []
    
    # Patterns for identifying arguments
    arg_patterns = [
        r'(?i)(?:contends?|submits?|argues?|claims?|asserts?)\s+that\s+([^.]+\.)',
        r'(?i)(?:according to|in the view of)\s+.{1,30}?[,\s]\s*([^.]+\.)',
        r'(?i)(?:firstly|secondly|thirdly|finally|moreover|furthermore),\s+([^.]+\.)',
        r'(?i)(?:concludes?|maintains?|alleges?)\s+that\s+([^.]+\.)',
        r'(?i)(?:points? out|notes?|observes?)\s+that\s+([^.]+\.)',
        r'(?i)The (?:claimant|respondent|appellant|defendant).{1,30}?(?:contends?|submits?|argues?|claims?|asserts?)\s+that\s+([^.]+\.)',
        r'(?i)(?:disagrees?|disputes?|counters?|rebuts?|refutes?|denies?)\s+([^.]+\.)'
    ]
    
    for pattern in arg_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            # Get the argument text
            arg_text = match.group(1).strip()
            
            # Get context (text around the argument)
            start_pos = max(0, match.start() - 100)
            end_pos = min(len(text), match.end() + 100)
            context = text[start_pos:end_pos]
            
            # Extract paragraph number
            para_number = text[:match.start()].count("\n\n") + 1
            
            # Find supporting evidence/citations
            context_citations = extract_citations(context)
            
            # Extract legal concepts
            concepts = []
            for concept, variations in st.session_state.legal_concepts.items():
                if any(var.lower() in arg_text.lower() for var in [concept] + variations):
                    concepts.append(concept)
            
            arguments.append({
                'text': arg_text,
                'context': context,
                'paragraph': para_number,
                'position': match.start(),
                'doc_id': doc_id,
                'pattern_used': pattern,
                'citations': context_citations,
                'concepts': concepts,
                'exact_location': f"Document: {doc_id}, Paragraph: {para_number}, Position: {match.start()}"
            })
    
    return arguments

def create_argument_summary(doc_id, arguments):
    """Create a summary of arguments for a document"""
    if not arguments:
        return {
            'doc_id': doc_id,
            'argument_count': 0,
            'arguments': [],
            'concepts': [],
            'citations': []
        }
    
    # Collect all unique concepts and citations
    all_concepts = set()
    all_citations = []
    
    for arg in arguments:
        all_concepts.update(arg['concepts'])
        all_citations.extend(arg['citations'])
    
    # Group arguments by concept
    concept_groups = {}
    for concept in all_concepts:
        concept_groups[concept] = [arg for arg in arguments if concept in arg['concepts']]
    
    return {
        'doc_id': doc_id,
        'argument_count': len(arguments),
        'arguments': arguments,
        'concepts': list(all_concepts),
        'citations': all_citations,
        'concept_groups': concept_groups
    }

def generate_comparative_table(claimant_summary, respondent_summary):
    """Generate comparison table of arguments"""
    if not claimant_summary or not respondent_summary:
        return []
    
    table_rows = []
    
    # Get all unique concepts
    all_concepts = set(claimant_summary['concepts'] + respondent_summary['concepts'])
    
    for concept in all_concepts:
        claimant_args = [arg for arg in claimant_summary['arguments'] if concept in arg['concepts']]
        respondent_args = [arg for arg in respondent_summary['arguments'] if concept in arg['concepts']]
        
        if claimant_args or respondent_args:
            row = {
                'concept': concept,
                'claimant_arguments': claimant_args,
                'respondent_arguments': respondent_args
            }
            table_rows.append(row)
    
    return table_rows

# UI Components
st.title("Sports Arbitration Smart Search")

# Sidebar for document management
with st.sidebar:
    st.header("Document Management")
    
    # File uploader
    uploaded_files = st.file_uploader("Upload Documents", 
                                    accept_multiple_files=True, 
                                    type=["pdf", "docx", "txt"])
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.documents:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    content = process_uploaded_file(uploaded_file)
                    if content:
                        st.session_state.documents[uploaded_file.name] = uploaded_file
                        st.session_state.document_content[uploaded_file.name] = content
                        st.success(f"Successfully processed {uploaded_file.name}")
    
    # Document management
    if st.session_state.documents:
        st.subheader("Manage Documents")
        
        # Assign roles to documents
        st.write("Assign document roles:")
        for doc_id in st.session_state.documents:
            if 'document_roles' not in st.session_state:
                st.session_state.document_roles = {}
            
            st.session_state.document_roles[doc_id] = st.selectbox(
                f"Role for {doc_id}",
                options=["Unassigned", "Claimant Submission", "Respondent Submission", "Claimant Exhibit", "Respondent Exhibit"],
                key=f"role_{doc_id}",
                index=0 if doc_id not in st.session_state.document_roles else 
                     ["Unassigned", "Claimant Submission", "Respondent Submission", "Claimant Exhibit", "Respondent Exhibit"].index(st.session_state.document_roles[doc_id])
            )

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["Smart Search", "Document Comparison", "Argument Analysis", "Legal Concepts"])

# Tab 1: Smart Search
with tab1:
    st.header("Semantic Smart Search")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_area("Enter search query", 
                                  placeholder="Enter a legal concept, argument or issue...")
    
    with col2:
        search_threshold = st.slider("Relevance Threshold", 
                                   min_value=0.1, max_value=0.9, value=0.3, step=0.05,
                                   help="Lower values return more results but may be less relevant")
        
        include_variations = st.checkbox("Include concept variations", value=True,
                                       help="Search for variations of legal concepts")
        
        search_button = st.button("Search Documents", type="primary")
    
    if search_button and search_query:
        with st.spinner("Searching documents..."):
            search_results = semantic_search(
                search_query, 
                st.session_state.document_content,
                threshold=search_threshold
            )
            st.session_state.search_results = search_results
    
    if st.session_state.search_results:
        st.subheader(f"Search Results ({len(st.session_state.search_results)} matches)")
        
        if not st.session_state.search_results:
            st.info("No matching results found. Try lowering the threshold or using different search terms.")
        
        for i, result in enumerate(st.session_state.search_results):
            with st.expander(f"Result {i+1} - {result['doc_id']} (Score: {result['score']})"):
                # Display paragraph with highlighted search terms
                highlighted_text = result['paragraph']['text']
                
                # Highlight direct matches
                for term in search_query.lower().split():
                    if len(term) > 3:
                        pattern = re.compile(f'({re.escape(term)})', re.IGNORECASE)
                        highlighted_text = pattern.sub(r'<mark>\1</mark>', highlighted_text)
                
                # Display source information
                st.markdown(f"**Source:** {result['doc_id']}, Paragraph {result['paragraph']['index']+1}")
                st.markdown(highlighted_text, unsafe_allow_html=True)
                
                # Display citations if any
                if result['paragraph']['citations']:
                    st.markdown("**References:**")
                    for citation in result['paragraph']['citations']:
                        st.markdown(f"- {citation['type'].capitalize()}: {citation['id']} ({citation['text']})")
                
                # Display concepts if any
                if result['paragraph']['concepts']:
                    st.markdown("**Legal concepts:**")
                    st.markdown(", ".join(result['paragraph']['concepts']))

# Tab 2: Document Comparison
with tab2:
    st.header("Document Comparison")
    
    if len(st.session_state.document_content) < 2:
        st.warning("Please upload at least two documents to compare.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            doc1 = st.selectbox("Select first document", 
                              options=list(st.session_state.document_content.keys()),
                              key="compare_doc1")
        
        with col2:
            doc2_options = [doc for doc in st.session_state.document_content.keys() if doc != doc1]
            doc2 = st.selectbox("Select second document", 
                              options=doc2_options,
                              key="compare_doc2")
        
        comparison_options = st.radio(
            "Comparison focus",
            ["All Differences", "Substantial Differences Only", "Citation Differences", "Legal Concept Differences"],
            horizontal=True
        )
        
        compare_button = st.button("Compare Documents", key="compare_button")
        
        if compare_button:
            with st.spinner("Comparing documents..."):
                focus_on_substance = comparison_options != "All Differences"
                comparison_results = compare_documents(doc1, doc2, focus_on_substance)
                
                # Filter results based on selection
                if comparison_options == "Citation Differences":
                    comparison_results = [r for r in comparison_results if r['different_citations']]
                elif comparison_options == "Legal Concept Differences":
                    comparison_results = [r for r in comparison_results if r['concept_diff']]
                
                st.session_state.compare_results = comparison_results
        
        if 'compare_results' in st.session_state and st.session_state.compare_results:
            st.subheader(f"Comparison Results ({len(st.session_state.compare_results)} differences)")
            
            if not st.session_state.compare_results:
                st.info("No differences found based on your criteria.")
            
            for i, result in enumerate(st.session_state.compare_results):
                # Create expander label with difference details
                label_parts = [f"Difference {i+1}"]
                if result['is_substantial']:
                    label_parts.append("SUBSTANTIAL")
                
                details = []
                if result['different_citations']:
                    details.append("Citations")
                if result['concept_diff']:
                    details.append("Legal Concepts")
                if result['number_diff']:
                    details.append("Numbers/Dates")
                if result['negation_diff']:
                    details.append("Negations")
                
                if details:
                    label_parts.append(f"({', '.join(details)})")
                
                with st.expander(" - ".join(label_parts)):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Document: {result['doc1_id']}**")
                        st.markdown(result['doc1_formatted'], unsafe_allow_html=True)
                        
                        if result['para1']['citations']:
                            st.markdown("**Citations:**")
                            for citation in result['para1']['citations']:
                                st.markdown(f"- {citation['id']}")
                    
                    with col2:
                        st.markdown(f"**Document: {result['doc2_id']}**")
                        st.markdown(result['doc2_formatted'], unsafe_allow_html=True)
                        
                        if result['para2']['citations']:
                            st.markdown("**Citations:**")
                            for citation in result['para2']['citations']:
                                st.markdown(f"- {citation['id']}")

# Tab 3: Argument Analysis
with tab3:
    st.header("Argument Analysis")
    
    if not st.session_state.documents:
        st.warning("Please upload documents to analyze arguments.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            analysis_options = st.multiselect(
                "Select documents to analyze",
                options=list(st.session_state.documents.keys()),
                default=[]
            )
        
        with col2:
            output_format = st.radio(
                "Output format",
                ["Individual Summaries", "Comparative Table"],
                index=0
            )
            
            analyze_button = st.button("Analyze Arguments", type="primary")
        
        if analyze_button and analysis_options:
            claimant_docs = []
            respondent_docs = []
            
            # Group documents by role
            for doc_id in analysis_options:
                role = st.session_state.document_roles.get(doc_id, "Unassigned")
                if "Claimant" in role:
                    claimant_docs.append(doc_id)
                elif "Respondent" in role:
                    respondent_docs.append(doc_id)
            
            with st.spinner("Analyzing arguments..."):
                # Extract arguments from each document
                all_summaries = {}
                
                for doc_id in analysis_options:
                    if doc_id in st.session_state.document_content:
                        arguments = extract_arguments(st.session_state.document_content[doc_id], doc_id)
                        summary = create_argument_summary(doc_id, arguments)
                        all_summaries[doc_id] = summary
                
                st.session_state.argument_summaries = all_summaries
                
                # Create comparative table if needed
                if output_format == "Comparative Table" and claimant_docs and respondent_docs:
                    # Combine arguments from all claimant docs
                    combined_claimant_args = []
                    for doc_id in claimant_docs:
                        if doc_id in all_summaries:
                            combined_claimant_args.extend(all_summaries[doc_id]['arguments'])
                    
                    # Combine arguments from all respondent docs
                    combined_respondent_args = []
                    for doc_id in respondent_docs:
                        if doc_id in all_summaries:
                            combined_respondent_args.extend(all_summaries[doc_id]['arguments'])
                    
                    # Create summaries for the combined arguments
                    claimant_summary = create_argument_summary("Claimant Documents", combined_claimant_args)
                    respondent_summary = create_argument_summary("Respondent Documents", combined_respondent_args)
                    
                    # Generate comparative table
                    table = generate_comparative_table(claimant_summary, respondent_summary)
                    st.session_state.comparative_table = table
        
        # Display argument summaries
        if 'argument_summaries' in st.session_state and st.session_state.argument_summaries:
            if output_format == "Individual Summaries":
                st.subheader("Argument Summaries")
                
                # Display each document's arguments separately
                for doc_id, summary in st.session_state.argument_summaries.items():
                    with st.expander(f"{doc_id} - {summary['argument_count']} arguments"):
                        role = st.session_state.document_roles.get(doc_id, "Unassigned")
                        st.markdown(f"**Document Role:** {role}")
                        
                        # Show concepts if any
                        if summary['concepts']:
                            st.markdown("**Legal concepts found:**")
                            st.markdown(", ".join(summary['concepts']))
                        
                        # Show arguments
                        for i, arg in enumerate(summary['arguments']):
                            st.markdown(f"**Argument {i+1}:**")
                            st.markdown(f"_{arg['text']}_")
                            
                            # Source verification
                            st.markdown(f"**Source:** {arg['exact_location']}")
                            
                            # Show evidence/citations
                            if arg['citations']:
                                st.markdown("**Supporting evidence:**")
                                for citation in arg['citations']:
                                    st.markdown(f"- {citation['type'].capitalize()}: {citation['id']}")
                            
                            st.markdown("---")
            
            elif output_format == "Comparative Table" and 'comparative_table' in st.session_state:
                st.subheader("Comparative Analysis of Arguments")
                
                for row in st.session_state.comparative_table:
                    with st.expander(f"Issue: {row['concept']}"):
                        cols = st.columns(2)
                        
                        with cols[0]:
                            st.markdown("**Claimant Arguments:**")
                            if row['claimant_arguments']:
                                for arg in row['claimant_arguments']:
                                    st.markdown(f"- {arg['text']}")
                                    st.markdown(f"  _Source: {arg['exact_location']}_")
                            else:
                                st.markdown("_No arguments on this issue_")
                        
                        with cols[1]:
                            st.markdown("**Respondent Arguments:**")
                            if row['respondent_arguments']:
                                for arg in row['respondent_arguments']:
                                    st.markdown(f"- {arg['text']}")
                                    st.markdown(f"  _Source: {arg['exact_location']}_")
                            else:
                                st.markdown("_No arguments on this issue_")

# Tab 4: Legal Concepts
with tab4:
    st.header("Legal Concepts Management")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Manage Concepts")
        
        # Edit existing concepts
        st.markdown("**Edit existing concepts:**")
        existing_concept = st.selectbox(
            "Select concept to edit",
            options=[""] + list(st.session_state.legal_concepts.keys())
        )
        
        if existing_concept:
            variations = st.session_state.legal_concepts[existing_concept]
            variations_text = "\n".join(variations)
            
            new_variations = st.text_area(
                "Edit variations (one per line)",
                value=variations_text
            )
            
            if st.button("Update"):
                if new_variations.strip():
                    st.session_state.legal_concepts[existing_concept] = [
                        v.strip() for v in new_variations.split("\n") if v.strip()
                    ]
                    st.success(f"Updated variations for '{existing_concept}'")
                    st.rerun()
        
        # Add new concept
        st.markdown("**Add new concept:**")
        new_concept = st.text_input("Concept name")
        new_variations = st.text_area("Variations (one per line)")
        
        if st.button("Add"):
            if new_concept and new_variations.strip():
                variations_list = [v.strip() for v in new_variations.split("\n") if v.strip()]
                st.session_state.legal_concepts[new_concept] = variations_list
                st.success(f"Added new concept: '{new_concept}'")
                st.rerun()
    
    with col2:
        st.subheader("Current Legal Concepts")
        
        for concept, variations in st.session_state.legal_concepts.items():
            with st.expander(concept):
                st.markdown("**Variations:**")
                for var in variations:
                    st.markdown(f"- {var}")
                
                # Quick search for this concept
                if st.button(f"Search for '{concept}'", key=f"search_{concept}"):
                    with st.spinner(f"Searching for '{concept}'..."):
                        results = semantic_search(concept, st.session_state.document_content, threshold=0.2)
                        if results:
                            st.markdown(f"**Found {len(results)} matches:**")
                            for i, result in enumerate(results[:3]):  # Show top 3
                                st.markdown(f"**{result['doc_id']}:** {result['paragraph']['text'][:100]}...")
                        else:
                            st.info("No matches found.")
