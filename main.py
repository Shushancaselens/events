import streamlit as st
import pandas as pd
import os
import re
from pathlib import Path
import difflib
from io import BytesIO
import base64
import PyPDF2
import docx

# Set up page configuration
st.set_page_config(page_title="Sports Arbitration Smart Search", layout="wide")

# Initialize session state for documents and search results
if 'documents' not in st.session_state:
    st.session_state.documents = {}
if 'document_content' not in st.session_state:
    st.session_state.document_content = {}
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'compare_results' not in st.session_state:
    st.session_state.compare_results = []
if 'summary' not in st.session_state:
    st.session_state.summary = None

# Document processing functions
def extract_text_from_pdf(file_content):
    """Extract text from PDF file"""
    try:
        reader = PyPDF2.PdfReader(BytesIO(file_content))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:  # Check if text extraction was successful
                text += page_text + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_content):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(BytesIO(file_content))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return ""

def extract_text_from_txt(file_content):
    """Extract text from TXT file"""
    try:
        return file_content.decode('utf-8')
    except Exception as e:
        st.error(f"Error extracting text from TXT: {e}")
        return ""

def process_uploaded_file(uploaded_file):
    """Process uploaded file based on file type"""
    file_content = uploaded_file.read()
    file_extension = Path(uploaded_file.name).suffix.lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(file_content)
    elif file_extension == '.docx':
        return extract_text_from_docx(file_content)
    elif file_extension == '.txt':
        return extract_text_from_txt(file_content)
    else:
        st.warning(f"Unsupported file type: {file_extension}")
        return ""

def preprocess_text(text):
    """Simple text preprocessing without NLTK"""
    if not text:
        return ""
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation (simplified approach)
    text = re.sub(r'[^\w\s]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_common_words(text):
    """Get a set of words from text, excluding very common English words"""
    if not text:
        return set()
        
    # Simple list of common English stop words
    stop_words = set(['the', 'and', 'a', 'an', 'in', 'on', 'at', 'of', 'to', 'for', 
                     'with', 'by', 'as', 'this', 'that', 'it', 'is', 'are', 'was', 
                     'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 
                     'does', 'did', 'but', 'or', 'if', 'then', 'else', 'when', 
                     'so', 'than', 'that', 'such', 'can', 'may', 'might', 'will', 
                     'would', 'should', 'could', 'i', 'you', 'he', 'she', 'we', 
                     'they', 'their', 'his', 'her', 'our', 'its', 'my', 'your'])
    
    # Split into words and remove stop words
    words = set()
    for word in preprocess_text(text).split():
        if len(word) > 2 and word not in stop_words:  # Skip very short words and stop words
            words.add(word)
    
    return words

def simple_similarity(text1, text2):
    """Calculate simple similarity between two texts based on word overlap"""
    if not text1 or not text2:
        return 0.0
        
    words1 = get_common_words(text1)
    words2 = get_common_words(text2)
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity (intersection over union)
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    if union == 0:
        return 0.0
        
    return intersection / union

def search_documents(query, doc_contents, threshold=0.2):
    """Search documents using simple text similarity"""
    if not doc_contents or not query:
        return []
    
    # Get query words
    query_words = get_common_words(query)
    if not query_words:
        return []
    
    # Results list
    results = []
    
    # For each document
    for doc_id, content in doc_contents.items():
        # Split content into paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        
        # For each paragraph
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) < 20:  # Skip very short paragraphs
                continue
                
            # Calculate similarity with query
            similarity = simple_similarity(query, paragraph)
            
            # Check if it meets threshold
            if similarity >= threshold:
                results.append({
                    'doc_id': doc_id,
                    'paragraph_index': i,
                    'text': paragraph,
                    'similarity': round(similarity, 3),
                    'start_pos': content.find(paragraph)
                })
    
    # Sort by similarity score (highest first)
    return sorted(results, key=lambda x: x['similarity'], reverse=True)

def compare_documents(doc1_id, doc2_id):
    """Compare two documents and highlight differences"""
    if doc1_id not in st.session_state.document_content or doc2_id not in st.session_state.document_content:
        return []
    
    doc1 = st.session_state.document_content[doc1_id]
    doc2 = st.session_state.document_content[doc2_id]
    
    # Split into paragraphs
    doc1_paras = re.split(r'\n\s*\n', doc1)
    doc2_paras = re.split(r'\n\s*\n', doc2)
    
    # Filter out very short paragraphs
    doc1_paras = [p for p in doc1_paras if len(p.strip()) > 20]
    doc2_paras = [p for p in doc2_paras if len(p.strip()) > 20]
    
    results = []
    
    # Compare each paragraph from doc1 with each paragraph from doc2
    for i, para1 in enumerate(doc1_paras):
        para1_words = get_common_words(para1)
        
        for j, para2 in enumerate(doc2_paras):
            para2_words = get_common_words(para2)
            
            # Calculate similarity
            similarity = simple_similarity(para1, para2)
            
            # Only consider paragraphs that are somewhat similar
            if similarity > 0.5:
                # Use difflib to find differences
                d = difflib.Differ()
                diff = list(d.compare(para1.splitlines(), para2.splitlines()))
                
                # Format the differences
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
                
                # Determine if differences are substantial
                unique_words1 = para1_words - para2_words
                unique_words2 = para2_words - para1_words
                total_words = len(para1_words.union(para2_words))
                
                # Consider substantial if more than 20% of unique words
                is_substantial = total_words > 0 and (len(unique_words1) + len(unique_words2)) / total_words > 0.2
                
                results.append({
                    'doc1_id': doc1_id,
                    'doc2_id': doc2_id,
                    'doc1_para_index': i,
                    'doc2_para_index': j,
                    'doc1_text': para1,
                    'doc2_text': para2,
                    'doc1_formatted': doc1_formatted,
                    'doc2_formatted': doc2_formatted,
                    'similarity': similarity,
                    'is_substantial': is_substantial
                })
    
    # Sort by similarity (least similar first)
    return sorted(results, key=lambda x: x['similarity'])

def create_summary(doc_id, doc_type="submission"):
    """Create a summary of arguments from a document"""
    if doc_id not in st.session_state.document_content:
        return None
    
    content = st.session_state.document_content[doc_id]
    
    # Extract arguments and evidence based on document type
    arguments = []
    
    # Simple pattern matching for arguments
    if doc_type == "submission":
        # Look for typical argument patterns
        arg_patterns = [
            r'(?i)(?:contends?|submits?|argues?|claims?|asserts?)\s+that\s+([^.]+\.)',
            r'(?i)(?:according to|in the view of)\s+.{1,30}?[,\s]\s*([^.]+\.)',
            r'(?i)(?:firstly|secondly|thirdly|finally|moreover|furthermore),\s+([^.]+\.)',
            r'(?i)(?:concludes?|maintains?|alleges?)\s+that\s+([^.]+\.)',
            r'(?i)(?:points? out|notes?|observes?)\s+that\s+([^.]+\.)',
            r'(?i)The (?:claimant|respondent|appellant|defendant).{1,30}?(?:contends?|submits?|argues?|claims?|asserts?)\s+that\s+([^.]+\.)'
        ]
        
        for pattern in arg_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                argument = match.group(1).strip()
                context = content[max(0, match.start() - 100):min(len(content), match.end() + 100)]
                
                # Look for evidence near the argument
                evidence = []
                evidence_patterns = [
                    r'(?i)(?:exhibit|document|evidence|proof)\s+([A-Z0-9-]+)',
                    r'(?i)(?:refer(?:s|ring)?|cite(?:s|d)?)\s+to\s+([^.]{3,50}?)\.',
                    r'(?i)(?:as shown in|as demonstrated by|as evidenced by)\s+([^.]{3,50}?)\.'
                ]
                
                for ev_pattern in evidence_patterns:
                    ev_matches = re.finditer(ev_pattern, context)
                    for ev_match in ev_matches:
                        evidence.append(ev_match.group(1).strip())
                
                arguments.append({
                    'text': argument,
                    'position': match.start(),
                    'evidence': evidence,
                    'context': context
                })
    
    # Create summary structure
    return {
        'doc_id': doc_id,
        'doc_type': doc_type,
        'arguments': arguments,
        'argument_count': len(arguments)
    }

def create_downloadable_report(search_results=None, compare_results=None, summary=None):
    """Create a downloadable report with the results"""
    report = []
    
    if search_results:
        report.append("# SEARCH RESULTS\n")
        for i, result in enumerate(search_results, 1):
            report.append(f"## Result {i} (Similarity: {result['similarity']})\n")
            report.append(f"Document: {result['doc_id']}\n")
            report.append(f"Text: {result['text']}\n\n")
    
    if compare_results:
        report.append("# DOCUMENT COMPARISON\n")
        for i, result in enumerate(compare_results, 1):
            report.append(f"## Difference {i} (Similarity: {result['similarity']})\n")
            report.append(f"Document 1: {result['doc1_id']}\n")
            report.append(f"Document 2: {result['doc2_id']}\n")
            report.append(f"Is substantial difference: {'Yes' if result['is_substantial'] else 'No'}\n")
            report.append(f"Document 1 text: {result['doc1_text']}\n")
            report.append(f"Document 2 text: {result['doc2_text']}\n\n")
    
    if summary:
        report.append("# ARGUMENT SUMMARY\n")
        report.append(f"Document: {summary['doc_id']}\n")
        report.append(f"Document type: {summary['doc_type']}\n")
        report.append(f"Total arguments found: {summary['argument_count']}\n\n")
        
        for i, arg in enumerate(summary['arguments'], 1):
            report.append(f"## Argument {i}\n")
            report.append(f"Text: {arg['text']}\n")
            if arg['evidence']:
                report.append("Evidence:\n")
                for ev in arg['evidence']:
                    report.append(f"- {ev}\n")
            report.append("\n")
    
    return "\n".join(report)

# UI Components
st.title("Sports Arbitration Smart Search")

# Sidebar for document management
with st.sidebar:
    st.header("Document Management")
    
    # File uploader
    uploaded_files = st.file_uploader("Upload Documents", accept_multiple_files=True, type=["pdf", "docx", "txt"])
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Check if file is already processed
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
        docs_to_remove = st.multiselect("Select documents to remove", 
                                        options=list(st.session_state.documents.keys()))
        
        if st.button("Remove Selected"):
            for doc in docs_to_remove:
                if doc in st.session_state.documents:
                    del st.session_state.documents[doc]
                if doc in st.session_state.document_content:
                    del st.session_state.document_content[doc]
            st.success("Selected documents removed")
            st.rerun()
    
    # Show document stats
    if st.session_state.documents:
        st.subheader("Document Statistics")
        for doc_id, content in st.session_state.document_content.items():
            paragraphs = re.split(r'\n\s*\n', content)
            paragraphs = [p for p in paragraphs if len(p.strip()) > 20]
            st.write(f"**{doc_id}**: {len(paragraphs)} paragraphs, {len(content)} characters")

# Main area tabs
tab1, tab2, tab3, tab4 = st.tabs(["Smart Search", "Document Compare", "Argument Summary", "Document Viewer"])

# Tab 1: Smart Search
with tab1:
    st.header("Smart Search")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_area("Enter your search query", 
                                    placeholder="Enter legal concept, argument, or issue to search for...")
    
    with col2:
        search_threshold = st.slider("Similarity Threshold", 
                                    min_value=0.1, max_value=0.9, value=0.2, step=0.05,
                                    help="Lower values return more results but may be less relevant")
        search_button = st.button("Search Documents", type="primary")
    
    if search_button and search_query:
        with st.spinner("Searching documents..."):
            search_results = search_documents(search_query, st.session_state.document_content, search_threshold)
            st.session_state.search_results = search_results
    
    if st.session_state.search_results:
        st.subheader(f"Search Results ({len(st.session_state.search_results)} matches)")
        
        # No results message
        if len(st.session_state.search_results) == 0:
            st.info("No matching results found. Try lowering the similarity threshold or using different search terms.")
        
        # Display results
        for i, result in enumerate(st.session_state.search_results):
            with st.expander(f"Result {i+1} - {result['doc_id']} (Similarity: {result['similarity']})"):
                # Display the paragraph with context
                st.markdown(f"**Document:** {result['doc_id']}")
                st.markdown(f"**Paragraph {result['paragraph_index']}:**")
                
                # Highlight the matching text
                highlighted_text = result['text']
                for term in search_query.lower().split():
                    if len(term) > 3:  # Only highlight meaningful terms
                        pattern = re.compile(re.escape(term), re.IGNORECASE)
                        highlighted_text = pattern.sub(f"<mark>{term}</mark>", highlighted_text)
                
                st.markdown(highlighted_text, unsafe_allow_html=True)
        
        # Download results button
        if st.button("Download Search Results", key="download_search"):
            report = create_downloadable_report(search_results=st.session_state.search_results)
            b64 = base64.b64encode(report.encode()).decode()
            href = f'<a href="data:text/plain;base64,{b64}" download="search_results.txt">Download search results</a>'
            st.markdown(href, unsafe_allow_html=True)

# Tab 2: Document Compare
with tab2:
    st.header("Document Compare")
    
    if not st.session_state.documents or len(st.session_state.documents) < 2:
        st.warning("Please upload at least two documents to compare.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            doc1_id = st.selectbox("Select first document", 
                                  options=list(st.session_state.documents.keys()),
                                  key="compare_doc1")
        
        with col2:
            doc2_options = [doc for doc in st.session_state.documents.keys() if doc != doc1_id]
            doc2_id = st.selectbox("Select second document", 
                                 options=doc2_options,
                                 key="compare_doc2")
        
        compare_button = st.button("Compare Documents", type="primary", key="compare_button")
        
        if compare_button:
            if doc1_id == doc2_id:
                st.warning("Please select different documents to compare.")
            else:
                with st.spinner("Comparing documents..."):
                    compare_results = compare_documents(doc1_id, doc2_id)
                    st.session_state.compare_results = compare_results
        
        if st.session_state.compare_results:
            st.subheader(f"Comparison Results ({len(st.session_state.compare_results)} differences)")
            
            # Filter options
            show_substantial_only = st.checkbox("Show substantial differences only", value=True)
            
            # Filter results if needed
            filtered_results = [r for r in st.session_state.compare_results 
                              if not show_substantial_only or r['is_substantial']]
            
            if not filtered_results:
                st.info("No substantial differences found. Uncheck 'Show substantial differences only' to see all differences.")
            
            for i, result in enumerate(filtered_results):
                with st.expander(f"Difference {i+1} - " + 
                               f"{'Substantial' if result['is_substantial'] else 'Minor'} " +
                               f"(Similarity: {result['similarity']:.2f})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Document: {result['doc1_id']}**")
                        st.markdown(result['doc1_formatted'], unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"**Document: {result['doc2_id']}**")
                        st.markdown(result['doc2_formatted'], unsafe_allow_html=True)
            
            # Download results button
            if st.button("Download Comparison Results", key="download_compare"):
                report = create_downloadable_report(compare_results=st.session_state.compare_results)
                b64 = base64.b64encode(report.encode()).decode()
                href = f'<a href="data:text/plain;base64,{b64}" download="comparison_results.txt">Download comparison results</a>'
                st.markdown(href, unsafe_allow_html=True)

# Tab 3: Argument Summary
with tab3:
    st.header("Argument Summary")
    
    if not st.session_state.documents:
        st.warning("Please upload documents to summarize.")
    else:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            doc_id = st.selectbox("Select document to summarize", 
                                options=list(st.session_state.documents.keys()),
                                key="summary_doc")
        
        with col2:
            doc_type = st.selectbox("Document type", 
                                   options=["submission", "exhibit"],
                                   key="summary_type")
            summarize_button = st.button("Generate Summary", type="primary", key="summarize_button")
        
        if summarize_button:
            with st.spinner("Generating argument summary..."):
                summary = create_summary(doc_id, doc_type)
                st.session_state.summary = summary
        
        if st.session_state.summary:
            st.subheader(f"Argument Summary ({st.session_state.summary['argument_count']} arguments)")
            
            if st.session_state.summary['argument_count'] == 0:
                st.info("No clear arguments found in this document. This could be because the document doesn't contain typical argument patterns or uses different phrasing.")
                st.write("You can try:")
                st.write("1. Selecting a different document type")
                st.write("2. Using the Smart Search tab to search for specific legal terms")
            
            for i, arg in enumerate(st.session_state.summary['arguments']):
                with st.expander(f"Argument {i+1}"):
                    st.markdown(f"**Text:** {arg['text']}")
                    
                    if arg['evidence']:
                        st.markdown("**Evidence cited:**")
                        for ev in arg['evidence']:
                            st.markdown(f"- {ev}")
                    
                    st.markdown("**Context:**")
                    st.text(arg['context'])
            
            # Download results button
            if st.button("Download Argument Summary", key="download_summary"):
                report = create_downloadable_report(summary=st.session_state.summary)
                b64 = base64.b64encode(report.encode()).decode()
                href = f'<a href="data:text/plain;base64,{b64}" download="argument_summary.txt">Download argument summary</a>'
                st.markdown(href, unsafe_allow_html=True)

# Tab 4: Document Viewer
with tab4:
    st.header("Document Viewer")
    
    if not st.session_state.documents:
        st.warning("Please upload documents to view.")
    else:
        doc_id = st.selectbox("Select document to view", 
                            options=list(st.session_state.documents.keys()),
                            key="view_doc")
        
        if doc_id in st.session_state.document_content:
            content = st.session_state.document_content[doc_id]
            
            # Add search within document feature
            search_term = st.text_input("Search within document", key="doc_search")
            if search_term:
                highlighted_content = content
                for term in search_term.split():
                    if len(term) > 2:  # Only highlight terms with more than 2 characters
                        pattern = re.compile(f'({re.escape(term)})', re.IGNORECASE)
                        highlighted_content = pattern.sub(r'<mark>\1</mark>', highlighted_content)
                
                # Convert newlines to HTML breaks for proper display
                highlighted_content = highlighted_content.replace('\n', '<br>')
                st.markdown(highlighted_content, unsafe_allow_html=True)
            else:
                # Show plain text with a scrollable area
                st.text_area("Document Content", value=content, height=500, key="doc_content")

# Footer
st.markdown("---")
st.markdown("**Sports Arbitration Smart Search Tool** - Developed to assist legal professionals in analyzing arbitration documents")
