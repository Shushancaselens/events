import streamlit as st
import pandas as pd
import re
from datetime import datetime
from collections import Counter
import base64

# Initialize session state for document storage
if 'documents' not in st.session_state:
    st.session_state['documents'] = {}
if 'current_case' not in st.session_state:
    st.session_state['current_case'] = None
if 'cases' not in st.session_state:
    st.session_state['cases'] = []
if 'search_history' not in st.session_state:
    st.session_state['search_history'] = []

# Common English stopwords
STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
    'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
    'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
    'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
    'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
}

# Add domain-specific stopwords
LEGAL_STOPWORDS = {
    'court', 'case', 'appeal', 'defendant', 'plaintiff', 'appellant', 'respondent', 
    'exhibit', 'document', 'evidence', 'witness', 'testimony', 'judge', 'tribunal', 
    'arbitration', 'arbitrator', 'law', 'legal', 'paragraph', 'submission'
}
STOP_WORDS.update(LEGAL_STOPWORDS)

def preprocess_text(text):
    """Clean and preprocess text for better search"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    # Split on whitespace
    tokens = text.split()
    # Remove stopwords and short words
    tokens = [word for word in tokens if word not in STOP_WORDS and len(word) > 2]
    return ' '.join(tokens)

def get_document_type(filename):
    """Detect document type based on filename patterns"""
    filename = filename.lower()
    
    if any(term in filename for term in ['submission', 'brief', 'memo', 'argument']):
        return 'Submission'
    elif any(term in filename for term in ['exhibit', 'evidence', 'appendix']):
        return 'Exhibit'
    elif any(term in filename for term in ['decision', 'award', 'ruling']):
        return 'Decision'
    elif any(term in filename for term in ['transcript', 'hearing']):
        return 'Transcript'
    elif any(term in filename for term in ['contract', 'agreement']):
        return 'Contract'
    else:
        return 'Other'

def get_party(filename):
    """Detect party based on filename patterns"""
    filename = filename.lower()
    
    if any(term in filename for term in ['appellant', 'claimant', 'plaintiff']):
        return 'Appellant/Claimant'
    elif any(term in filename for term in ['respondent', 'defendant']):
        return 'Respondent/Defendant'
    else:
        return 'Unknown'

def create_document_chunks(text, chunk_size=500):
    """Split document into manageable chunks for better search"""
    # Split on periods followed by whitespace as a basic sentence detection
    sentences = re.split(r'\.(?=\s)', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    # Add the last chunk if it's not empty
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def add_document(text, filename, doc_type=None, party=None, date=None, language=None, case_name=None):
    """Add document to the session state"""
    if text:
        # Auto-detect document type and party if not provided
        detected_doc_type = doc_type or get_document_type(filename)
        detected_party = party or get_party(filename)
        
        # Create document chunks for better search
        chunks = create_document_chunks(text)
        
        # Create document entry
        doc_id = f"doc_{len(st.session_state['documents']) + 1}"
        doc_data = {
            'id': doc_id,
            'filename': filename,
            'type': detected_doc_type,
            'party': detected_party,
            'date': date or datetime.now().strftime("%Y-%m-%d"),
            'language': language or 'English',
            'case': case_name or st.session_state['current_case'],
            'text': text,
            'processed_text': preprocess_text(text),
            'chunks': chunks,
            'processed_chunks': [preprocess_text(chunk) for chunk in chunks]
        }
        
        # Add to session state
        st.session_state['documents'][doc_id] = doc_data
        return doc_id
    return None

def search_documents(query, case_filter=None, doc_type_filter=None, party_filter=None, date_range=None):
    """Search across all documents with filters"""
    results = []
    
    # Preprocess query
    processed_query = preprocess_text(query)
    query_terms = processed_query.split()
    
    for doc_id, doc in st.session_state['documents'].items():
        # Apply filters
        if case_filter and doc['case'] != case_filter:
            continue
        if doc_type_filter and doc['type'] != doc_type_filter:
            continue
        if party_filter and doc['party'] != party_filter:
            continue
        
        # Search in chunks for more precise results
        for i, (chunk, processed_chunk) in enumerate(zip(doc['chunks'], doc['processed_chunks'])):
            score = 0
            for term in query_terms:
                if term in processed_chunk:
                    # Basic term frequency scoring
                    term_count = processed_chunk.count(term)
                    score += term_count
            
            if score > 0:
                # Basic highlighting
                highlighted_chunk = chunk
                for term in query_terms:
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    highlighted_chunk = pattern.sub(f"**{term}**", highlighted_chunk)
                
                results.append({
                    'doc_id': doc_id,
                    'filename': doc['filename'],
                    'type': doc['type'],
                    'party': doc['party'],
                    'case': doc['case'],
                    'chunk_id': i,
                    'chunk': chunk,
                    'highlighted_chunk': highlighted_chunk,
                    'score': score
                })
    
    # Sort by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Add to search history
    if query and len(results) > 0:
        st.session_state['search_history'].append({
            'query': query,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'results_count': len(results)
        })
    
    return results

def export_results(results, format_type="markdown"):
    """Export search results to various formats"""
    if format_type == "markdown":
        output = "# Search Results\n\n"
        for i, result in enumerate(results):
            output += f"## Result {i+1}: {result['filename']}\n"
            output += f"**Document Type:** {result['type']}\n"
            output += f"**Party:** {result['party']}\n"
            output += f"**Case:** {result['case']}\n\n"
            output += f"{result['highlighted_chunk']}\n\n"
            output += "---\n\n"
        
        return output
    
    elif format_type == "csv":
        output = "Result,Filename,Document Type,Party,Case,Text\n"
        for i, result in enumerate(results):
            # Clean the text for CSV
            clean_text = result['chunk'].replace('"', '""')
            output += f"{i+1},\"{result['filename']}\",\"{result['type']}\",\"{result['party']}\",\"{result['case']}\",\"{clean_text}\"\n"
        
        return output
    
    return None

def main():
    st.set_page_config(page_title="Sports Arbitration Search", layout="wide")
    
    # Title
    st.title("Sports Arbitration Document Search")
    st.markdown("A specialized search system for sports arbitration cases")
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Home", "Case Management", "Document Upload", "Search"])
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Current Case")
    
    # Case selection or creation
    if st.session_state['cases']:
        current_case_index = 0
        if st.session_state['current_case'] in st.session_state['cases']:
            current_case_index = st.session_state['cases'].index(st.session_state['current_case'])
            
        current_case = st.sidebar.selectbox(
            "Select Case", 
            st.session_state['cases'],
            index=current_case_index
        )
        if current_case != st.session_state['current_case']:
            st.session_state['current_case'] = current_case
    
    new_case = st.sidebar.text_input("Create New Case")
    if st.sidebar.button("Add Case") and new_case:
        if new_case not in st.session_state['cases']:
            st.session_state['cases'].append(new_case)
            st.session_state['current_case'] = new_case
    
    # Document statistics
    if st.session_state['documents'] and st.session_state['current_case']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Document Statistics")
        
        case_docs = [doc for doc in st.session_state['documents'].values() 
                    if doc['case'] == st.session_state['current_case']]
        
        st.sidebar.markdown(f"**Total Documents:** {len(case_docs)}")
        
        # Count by document type
        doc_types = Counter([doc['type'] for doc in case_docs])
        if doc_types:
            st.sidebar.markdown("**By Document Type:**")
            for doc_type, count in doc_types.items():
                st.sidebar.markdown(f"- {doc_type}: {count}")
    
    # Main content based on selected page
    if page == "Home":
        st.header("Welcome to Sports Arbitration Document Search")
        
        st.markdown("""
        This application helps legal professionals in sports arbitration to efficiently search through case documents.
        
        ### Key Features:
        - **Upload and organize** documents by case
        - **Intelligent search** across submissions, exhibits, and precedents
        - **Filter results** by document type, party, and date
        - **Export findings** for briefs and hearing preparation
        
        ### Getting Started:
        1. Create a case in the sidebar
        2. Upload your documents
        3. Use the search functionality to find relevant information
        4. Export your findings
        """)
        
        # Sample data
        if st.button("Load Sample Data"):
            if 'Sample Case' not in st.session_state['cases']:
                st.session_state['cases'].append('Sample Case')
                st.session_state['current_case'] = 'Sample Case'
                
                # Add sample documents
                sample_docs = [
                    {
                        'filename': 'claimant_submission.txt',
                        'text': """CLAIMANT SUBMISSION
                        
This submission is made on behalf of FC United in the matter of the termination of the employment contract with Coach Smith.

We submit that the termination was with just cause due to the following reasons:
1. Coach Smith repeatedly failed to attend training sessions on time
2. The team's performance severely declined under his leadership
3. Coach Smith failed to maintain proper discipline among the players

According to Article 14 of the FIFA Regulations on the Status and Transfer of Players, a contract may be terminated with just cause when there is a serious breach by either party.

We request that the tribunal find the termination was justified and reject any claims for compensation.""",
                        'type': 'Submission',
                        'party': 'Appellant/Claimant'
                    },
                    {
                        'filename': 'respondent_submission.txt',
                        'text': """RESPONDENT SUBMISSION
                        
This submission is made on behalf of Coach Smith in response to FC United's claim.

We submit that the termination was without just cause for the following reasons:
1. No warning was given prior to termination
2. Poor sporting results do not constitute just cause according to CAS jurisprudence
3. The allegations of unprofessional behavior are unfounded

According to CAS 2011/A/2596, the absence of sporting results cannot, as a general rule, constitute per se a reason to terminate a contractual relationship with just cause.

We request that the tribunal find the termination was without just cause and award compensation for the remaining value of the contract.""",
                        'type': 'Submission',
                        'party': 'Respondent/Defendant'
                    },
                    {
                        'filename': 'employment_contract.txt',
                        'text': """EMPLOYMENT CONTRACT

between FC United ("the Club") and John Smith ("the Coach")

1. DURATION
This contract is valid from 1 June 2022 until 31 May 2023.

2. REMUNERATION
The Coach shall receive a monthly salary of EUR 10,000.

3. DUTIES
The Coach shall be responsible for training and managing the first team.

4. TERMINATION
This contract may be terminated by mutual agreement or with just cause.

5. APPLICABLE LAW
This contract is governed by Swiss law.""",
                        'type': 'Contract',
                        'party': 'Unknown'
                    },
                    {
                        'filename': 'cas_precedent.txt',
                        'text': """CAS PRECEDENT: CAS 2011/A/2596

AWARD EXCERPT:

The absence of sporting results cannot, as a general rule, constitute per se a reason to terminate a contractual relationship with just cause.

Article 337c of the Swiss Code of Obligations provides that in case of termination without just cause of an employment contract of set duration, the employer must, in principle, pay to the employee everything which the employee would have been entitled to receive until the agreed conclusion of the agreement.""",
                        'type': 'Decision',
                        'party': 'Unknown'
                    }
                ]
                
                for doc in sample_docs:
                    add_document(
                        text=doc['text'],
                        filename=doc['filename'],
                        doc_type=doc['type'],
                        party=doc['party'],
                        case_name='Sample Case'
                    )
                
                st.success("Sample data loaded successfully!")
                st.experimental_rerun()
    
    elif page == "Case Management":
        st.header("Case Management")
        
        if not st.session_state['current_case']:
            st.warning("Please create or select a case from the sidebar first.")
        else:
            st.subheader(f"Case: {st.session_state['current_case']}")
            
            # Case details section
            with st.expander("Case Details"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Case Number", key="case_number")
                    st.selectbox("Jurisdiction", [
                        "Court of Arbitration for Sport (CAS)",
                        "FIFA Dispute Resolution Chamber",
                        "FIFA Players' Status Committee",
                        "Other"
                    ], key="jurisdiction")
                with col2:
                    st.date_input("Filing Date", key="filing_date")
                    st.selectbox("Status", [
                        "Active",
                        "Pending",
                        "Closed"
                    ], key="case_status")
            
            # Display documents in this case
            st.subheader("Case Documents")
            
            case_docs = {doc_id: doc for doc_id, doc in st.session_state['documents'].items() 
                        if doc['case'] == st.session_state['current_case']}
            
            if case_docs:
                # Create a DataFrame for display
                doc_list = []
                for doc_id, doc in case_docs.items():
                    doc_list.append({
                        'ID': doc_id,
                        'Filename': doc['filename'],
                        'Type': doc['type'],
                        'Party': doc['party'],
                        'Date': doc['date']
                    })
                
                df = pd.DataFrame(doc_list)
                st.dataframe(df)
                
                # Document preview
                selected_doc_id = st.selectbox("Select document to preview", df['ID'].tolist())
                
                if selected_doc_id:
                    doc = st.session_state['documents'][selected_doc_id]
                    
                    st.subheader(f"Preview: {doc['filename']}")
                    st.text_area("Document Text", value=doc['text'], height=300)
            else:
                st.info("No documents found for this case. Please upload documents from the Document Upload page.")
    
    elif page == "Document Upload":
        st.header("Document Upload")
        
        if not st.session_state['current_case']:
            st.warning("Please create or select a case from the sidebar first.")
        else:
            st.subheader(f"Upload Documents for: {st.session_state['current_case']}")
            
            # Text area for document content
            doc_text = st.text_area("Enter Document Text", height=300)
            
            # Document metadata
            col1, col2 = st.columns(2)
            with col1:
                filename = st.text_input("Filename (e.g., submission.txt)")
                doc_type = st.selectbox("Document Type", [
                    "Submission",
                    "Exhibit",
                    "Decision",
                    "Transcript",
                    "Contract",
                    "Other"
                ])
            with col2:
                party = st.selectbox("Party", [
                    "Appellant/Claimant",
                    "Respondent/Defendant",
                    "Arbitrator/Tribunal",
                    "Unknown"
                ])
                date = st.date_input("Document Date")
            
            if st.button("Add Document") and doc_text and filename:
                doc_id = add_document(
                    text=doc_text,
                    filename=filename,
                    doc_type=doc_type,
                    party=party,
                    date=date.strftime("%Y-%m-%d"),
                    case_name=st.session_state['current_case']
                )
                
                if doc_id:
                    st.success(f"Document {filename} added successfully!")
                else:
                    st.error("Failed to add document.")
    
    elif page == "Search":
        st.header("Document Search")
        
        if not st.session_state['current_case']:
            st.warning("Please create or select a case from the sidebar first.")
        elif not st.session_state['documents']:
            st.warning("No documents found. Please upload documents first.")
        else:
            st.subheader(f"Search in: {st.session_state['current_case']}")
            
            # Search query
            query = st.text_input("Search Query", placeholder="Enter search terms...")
            
            # Advanced filters
            with st.expander("Advanced Filters"):
                # Get unique document types for this case
                case_docs = [doc for doc in st.session_state['documents'].values() 
                            if doc['case'] == st.session_state['current_case']]
                
                doc_types = ['All'] + list(set([doc['type'] for doc in case_docs]))
                parties = ['All'] + list(set([doc['party'] for doc in case_docs]))
                
                col1, col2 = st.columns(2)
                with col1:
                    doc_type_filter = st.selectbox("Document Type", doc_types)
                with col2:
                    party_filter = st.selectbox("Party", parties)
            
            # Search button
            if st.button("Search") and query:
                # Apply filters
                case_filter = st.session_state['current_case']
                type_filter = None if doc_type_filter == 'All' else doc_type_filter
                party_filter = None if party_filter == 'All' else party_filter
                
                # Execute search
                with st.spinner("Searching..."):
                    results = search_documents(
                        query,
                        case_filter=case_filter,
                        doc_type_filter=type_filter,
                        party_filter=party_filter
                    )
                
                # Display results
                st.subheader(f"Search Results: {len(results)} matches found")
                
                if results:
                    # Group results by document
                    docs_with_results = {}
                    for result in results:
                        doc_id = result['doc_id']
                        if doc_id not in docs_with_results:
                            docs_with_results[doc_id] = []
                        docs_with_results[doc_id].append(result)
                    
                    # Display each document with its results
                    for doc_id, doc_results in docs_with_results.items():
                        doc = st.session_state['documents'][doc_id]
                        
                        with st.expander(f"{doc['filename']} ({len(doc_results)} matches)", expanded=True):
                            st.markdown(f"**Type:** {doc['type']} | **Party:** {doc['party']}")
                            
                            # Display each match within the document
                            for i, result in enumerate(doc_results):
                                st.markdown(f"**Match {i+1}:**")
                                st.markdown(result['highlighted_chunk'])
                                st.markdown("---")
                    
                    # Export options
                    st.subheader("Export Results")
                    export_format = st.selectbox("Export Format", ["Markdown", "CSV"])
                    
                    if st.button("Export Results"):
                        if export_format == "Markdown":
                            export_data = export_results(results, "markdown")
                            file_ext = "md"
                        else:  # CSV
                            export_data = export_results(results, "csv")
                            file_ext = "csv"
                        
                        # Create download link
                        b64 = base64.b64encode(export_data.encode()).decode()
                        filename = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M')}.{file_ext}"
                        href = f'<a href="data:text/{file_ext};base64,{b64}" download="{filename}">Download {export_format} file</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        
                else:
                    st.info("No results found. Try modifying your search query or filters.")
            
            # Search tips
            with st.expander("Search Tips"):
                st.markdown("""
                ### Effective Search Strategies
                
                - **Use specific terms** from legal or sports contexts
                - **Search for key concepts** like "just cause", "contract termination", "compensation"
                - **Filter by document type** to focus on submissions or exhibits
                - **Filter by party** to compare appellant vs respondent arguments
                
                ### Example Searches
                
                - just cause termination contract
                - sporting results performance
                - compensation breach contract
                - CAS precedent
                """)

if __name__ == "__main__":
    main()
