import streamlit as st
import re
from pathlib import Path
import difflib
import base64
from io import StringIO

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
def process_uploaded_file(uploaded_file):
    """Process uploaded text file"""
    try:
        # Only process text files for now
        text_content = uploaded_file.read().decode('utf-8')
        return text_content
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return ""

def preprocess_text(text):
    """Simple text preprocessing"""
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

def improved_search(query, doc_contents, threshold=0.1):
    """Enhanced search functionality with multiple strategies"""
    results = []
    query = query.strip()
    
    if not query or not doc_contents:
        return results
    
    # 1. Direct search (exact phrase matching with highest priority)
    for doc_id, content in doc_contents.items():
        # Split content into paragraphs or sentences
        paragraphs = re.split(r'\n\s*\n', content)
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) < 20:  # Skip very short paragraphs
                continue
            
            # Check for exact phrase match (case insensitive)
            if query.lower() in paragraph.lower():
                results.append({
                    'doc_id': doc_id,
                    'paragraph_index': i,
                    'text': paragraph,
                    'similarity': 0.95,  # High score for exact matches
                    'start_pos': content.find(paragraph),
                    'match_type': 'exact phrase'
                })
    
    # 2. Keyword search (check if all keywords are present)
    query_words = set(preprocess_text(query).split())
    if query_words:
        for doc_id, content in doc_contents.items():
            paragraphs = re.split(r'\n\s*\n', content)
            
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph.strip()) < 20:
                    continue
                
                paragraph_words = set(preprocess_text(paragraph).split())
                if not paragraph_words:
                    continue
                
                # Check how many query words are in the paragraph
                matches = query_words.intersection(paragraph_words)
                if matches:
                    # Calculate score based on % of query words found
                    score = len(matches) / len(query_words)
                    
                    # Only include if score is above threshold and not already included
                    if score >= threshold:
                        # Check if this paragraph is already in results
                        if not any(r['doc_id'] == doc_id and r['paragraph_index'] == i for r in results):
                            results.append({
                                'doc_id': doc_id,
                                'paragraph_index': i,
                                'text': paragraph,
                                'similarity': round(score, 3),
                                'start_pos': content.find(paragraph),
                                'match_type': 'keyword'
                            })
    
    # 3. Semantic search (word overlap)
    for doc_id, content in doc_contents.items():
        paragraphs = re.split(r'\n\s*\n', content)
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) < 20:
                continue
                
            # Skip if already matched exactly
            if any(r['doc_id'] == doc_id and r['paragraph_index'] == i and r['match_type'] == 'exact phrase' for r in results):
                continue
            
            # Get words from query and paragraph
            para_words = get_common_words(paragraph)
            query_words_set = get_common_words(query)
            
            if para_words and query_words_set:
                # Calculate Jaccard similarity
                intersection = len(para_words.intersection(query_words_set))
                union = len(para_words.union(query_words_set))
                
                if union > 0:
                    similarity = intersection / union
                    
                    # Only add if above threshold and better than existing
                    if similarity >= threshold:
                        existing = next((r for r in results if r['doc_id'] == doc_id and r['paragraph_index'] == i), None)
                        
                        if existing is None:
                            results.append({
                                'doc_id': doc_id,
                                'paragraph_index': i,
                                'text': paragraph,
                                'similarity': round(similarity, 3),
                                'start_pos': content.find(paragraph),
                                'match_type': 'semantic'
                            })
                        elif existing['similarity'] < similarity:
                            # Update with better similarity score
                            existing['similarity'] = round(similarity, 3)
                            existing['match_type'] = 'semantic'
    
    # 4. Special patterns search (legal terminology and structures)
    legal_patterns = [
        (r'(?i)(?:article|section|clause)\s+\d+(?:\.\d+)*', 'contract reference'),
        (r'(?i)(?:exhibit|evidence|document)\s+[A-Z0-9\-]+', 'evidence reference'),
        (r'(?i)(?:contends?|submits?|argues?|claims?|asserts?)\s+that', 'legal argument'),
        (r'(?i)(?:claimant|respondent|appellant|defendant)', 'party reference'),
        (r'(?i)(?:tribunal|arbitrator|hearing|proceedings?)', 'procedural reference')
    ]
    
    query_terms = query.lower().split()
    
    # Check if any query terms match special legal terms
    for pattern, pattern_type in legal_patterns:
        if any(re.search(pattern.lower(), term.lower()) for term in query_terms):
            # Search for this pattern in documents
            for doc_id, content in doc_contents.items():
                paragraphs = re.split(r'\n\s*\n', content)
                
                for i, paragraph in enumerate(paragraphs):
                    if len(paragraph.strip()) < 20:
                        continue
                    
                    # Skip if already matched with high score
                    if any(r['doc_id'] == doc_id and r['paragraph_index'] == i and r['similarity'] > 0.7 for r in results):
                        continue
                    
                    if re.search(pattern, paragraph):
                        # Check if paragraph contains any query words
                        if any(term.lower() in paragraph.lower() for term in query_terms):
                            # Only add if not already present with higher score
                            existing = next((r for r in results if r['doc_id'] == doc_id and r['paragraph_index'] == i), None)
                            
                            if existing is None:
                                results.append({
                                    'doc_id': doc_id,
                                    'paragraph_index': i,
                                    'text': paragraph,
                                    'similarity': 0.6,  # Medium-high score for pattern matches
                                    'start_pos': content.find(paragraph),
                                    'match_type': pattern_type
                                })
    
    # Sort by similarity score (highest first)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    # Remove duplicates (keeping the highest scoring version)
    unique_results = []
    seen_paragraphs = set()
    
    for result in results:
        key = (result['doc_id'], result['paragraph_index'])
        if key not in seen_paragraphs:
            seen_paragraphs.add(key)
            unique_results.append(result)
    
    return unique_results

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
            similarity = 0
            if para1_words and para2_words:
                intersection = len(para1_words.intersection(para2_words))
                union = len(para1_words.union(para2_words))
                
                if union > 0:
                    similarity = intersection / union
            
            # Only consider paragraphs that are somewhat similar
            if similarity > 0.4:
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
            report.append(f"Match type: {result.get('match_type', 'similarity')}\n")
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

def highlight_search_terms(text, search_terms):
    """Highlight search terms in text with better accuracy"""
    if not text or not search_terms:
        return text
    
    # First try exact phrase highlighting
    highlighted_text = text
    search_phrase = " ".join(search_terms).strip()
    if len(search_phrase) > 3:
        pattern = re.compile(re.escape(search_phrase), re.IGNORECASE)
        highlighted_text = pattern.sub(f"<mark>{search_phrase}</mark>", highlighted_text)
    
    # Then try individual terms
    for term in search_terms:
        if len(term) > 2:  # Only highlight terms with more than 2 characters
            # Make sure we're highlighting whole words, not parts of words
            pattern = re.compile(r'\b(' + re.escape(term) + r')\b', re.IGNORECASE)
            highlighted_text = pattern.sub(r'<mark>\1</mark>', highlighted_text)
    
    return highlighted_text

# UI Components
st.title("Sports Arbitration Smart Search")

# Sidebar for document management
with st.sidebar:
    st.header("Document Management")
    
    # File uploader (text files only)
    uploaded_files = st.file_uploader("Upload Text Documents", accept_multiple_files=True, type=["txt"])
    
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

# Sample data option
if not st.session_state.documents:
    st.warning("No documents uploaded. You can use the sample data below to try out the application.")
    
    if st.button("Load Sample Data"):
        # Sample legal text
        sample1 = """
        Arbitration Submission by Claimant

        The Claimant submits that the Respondent has breached Article 3.2 of the contract dated January 15, 2023.
        
        Firstly, the Respondent failed to deliver the goods within the agreed timeframe of 30 days, as evidenced by Exhibit A-1.
        
        According to Article 3.2, "the Respondent shall deliver all goods specified in Annex 1 within 30 days of receipt of payment." The Claimant contends that payment was made on February 1, 2023, as shown in the bank statement (Exhibit A-2).
        
        Moreover, the Respondent acknowledged receipt of payment on February 2, 2023, as demonstrated by email correspondence in Exhibit A-3.
        
        The Respondent argues that force majeure conditions apply due to supply chain disruptions. However, the Claimant maintains that no force majeure notice was provided within the 5-day period required by Article 8.3 of the contract.
        
        Furthermore, the Claimant submits that damages are due according to the penalty clause in Article 7.1, which states that "failure to deliver within the agreed timeframe will result in liquidated damages of 0.5% of the contract value per day of delay."
        
        In conclusion, the Claimant requests that the Tribunal:
        1. Declare that the Respondent has breached the contract;
        2. Order the Respondent to pay liquidated damages in the amount of €25,000;
        3. Order the Respondent to pay the costs of this arbitration.
        """
        
        sample2 = """
        Response to Arbitration Claim
        
        The Respondent contends that no breach of Article 3.2 has occurred under the circumstances.
        
        First, while the Respondent acknowledges receipt of payment on February 2, 2023, as referenced in Exhibit A-3, the Respondent submits that the delivery timeline was affected by documented supply chain disruptions.
        
        According to Article 8.2 of the contract, "delivery timelines may be extended in case of supply chain disruptions beyond the reasonable control of the Respondent." The Respondent argues that such disruptions occurred and were communicated to the Claimant on February 15, 2023, as evidenced by Exhibit R-1.
        
        Moreover, the Respondent maintains that the notice provided on February 15 satisfies the requirements of Article 8.3, as it was sent within 5 business days of the Respondent becoming aware of the disruption.
        
        The Claimant asserts that the penalty clause in Article 7.1 applies. However, the Respondent points out that Article 7.2 states that "no liquidated damages shall be due if delivery is delayed due to circumstances covered by Article 8.2."
        
        Furthermore, the Respondent notes that the goods were ultimately delivered on March 10, 2023, with only a 7-day delay beyond the force majeure period.
        
        In conclusion, the Respondent requests that the Tribunal:
        1. Declare that no breach of contract has occurred;
        2. Dismiss all claims for damages;
        3. Order the Claimant to pay the costs of this arbitration.
        """
        
        # Sample sports-specific arbitration text
        sample3 = """
        Appeal to the Court of Arbitration for Sport
        
        The Appellant, FC United, challenges the decision of the FIFA Disciplinary Committee dated October 12, 2024, in which the Committee imposed a transfer ban for two registration periods and a fine of CHF 500,000 for alleged violations of Article 19 of the FIFA Regulations on the Status and Transfer of Players regarding the international transfer of minors.
        
        Firstly, the Appellant contends that no breach of Article 19 has occurred, as all transfers in question fall under the exceptions listed in Article 19.2, specifically that the players' parents moved to the country for reasons not linked to football (Article 19.2.a).
        
        According to the documentation submitted as Exhibit A-5, the parents of Player X moved to the country for employment opportunities unrelated to football. The Disciplinary Committee erred in its assessment that the employment was arranged by the club.
        
        Moreover, the Appellant argues that the Committee failed to properly consider the welfare of the players in question, as mandated by Article 19.1, which states that international transfers are only permitted when "the players' welfare and sporting development are guaranteed."
        
        The Appellant submits that the sanctions imposed are disproportionate to the alleged infringements, especially in light of the jurisprudence established in CAS 2014/A/3793 where significantly more lenient sanctions were imposed for similar violations.
        
        Furthermore, the Appellant maintains that procedural violations occurred during the FIFA disciplinary proceedings, as specified in Exhibit A-12, where it is demonstrated that the Appellant was not granted sufficient time to prepare its defense.
        
        In conclusion, the Appellant requests that the Panel:
        1. Annul the decision of the FIFA Disciplinary Committee;
        2. Determine that no violation of Article 19 has occurred;
        3. Alternatively, reduce the sanctions to a level consistent with CAS jurisprudence;
        4. Order FIFA to pay the costs of the arbitration proceedings.
        """
        
        st.session_state.documents = {
            "Claimant_Submission.txt": None, 
            "Respondent_Reply.txt": None,
            "CAS_Appeal.txt": None
        }
        st.session_state.document_content = {
            "Claimant_Submission.txt": sample1,
            "Respondent_Reply.txt": sample2,
            "CAS_Appeal.txt": sample3
        }
        st.success("Sample data loaded successfully!")
        st.rerun()

# Main area tabs
tab1, tab2, tab3, tab4 = st.tabs(["Smart Search", "Document Compare", "Argument Summary", "Document Viewer"])

# Tab 1: Smart Search
with tab1:
    st.header("Smart Search")
    
    with st.container():
        st.markdown("""
        ### Search Examples:
        - Legal concepts: "force majeure", "liquidated damages", "breach of contract"
        - Document references: "Article 3.2", "Exhibit A-1"
        - Legal arguments: "claimant contends", "respondent argues" 
        - Sports terms: "transfer ban", "FIFA regulations", "player registration"
        """)
    
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
            search_results = improved_search(search_query, st.session_state.document_content, search_threshold)
            st.session_state.search_results = search_results
    
    if st.session_state.search_results:
        st.subheader(f"Search Results ({len(st.session_state.search_results)} matches)")
        
        # No results message
        if len(st.session_state.search_results) == 0:
            st.info("No matching results found. Try lowering the similarity threshold or using different search terms.")
            st.markdown("""
            **Search Tips:**
            - Use more specific legal terminology
            - Try searching for document references (e.g., "Article 8.3", "Exhibit R-1")
            - Use phrases that typically appear in legal documents (e.g., "the claimant submits")
            - Consider searching for dates or specific entities mentioned in the documents
            """)
        else:
            # Display results with grouping by document
            docs = sorted(set(r['doc_id'] for r in st.session_state.search_results))
            
            # Option to filter by document
            selected_docs = st.multiselect("Filter by document", options=docs, default=docs)
            
            # Group results by document and filter
            filtered_results = [r for r in st.session_state.search_results if r['doc_id'] in selected_docs]
            
            if not filtered_results:
                st.info("No results in the selected documents.")
            
            # Display match type distribution
            if filtered_results:
                match_types = {}
                for r in filtered_results:
                    match_type = r.get('match_type', 'other')
                    match_types[match_type] = match_types.get(match_type, 0) + 1
                
                st.write("**Match types found:**")
                for match_type, count in match_types.items():
                    st.write(f"- {match_type.title()}: {count}")
            
            # Organize by document
            for doc in selected_docs:
                doc_results = [r for r in filtered_results if r['doc_id'] == doc]
                if doc_results:
                    with st.expander(f"**{doc}** ({len(doc_results)} matches)", expanded=True):
                        for i, result in enumerate(doc_results):
                            st.markdown(f"#### Match {i+1} - {result.get('match_type', 'similarity match').title()} (Similarity: {result['similarity']})")
                            
                            # Highlight the
