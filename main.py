import streamlit as st
import pandas as pd
import numpy as np
import re
import os
from io import StringIO, BytesIO
from datetime import datetime
import base64
import io
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

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
stop_words = {
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
legal_stopwords = {
    'court', 'case', 'appeal', 'defendant', 'plaintiff', 'appellant', 'respondent', 
    'exhibit', 'document', 'evidence', 'witness', 'testimony', 'judge', 'tribunal', 
    'arbitration', 'arbitrator', 'law', 'legal', 'paragraph', 'submission'
}
stop_words.update(legal_stopwords)

# Document processing functions
def preprocess_text(text):
    """Clean and preprocess text for better search"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    # Tokenize by splitting on whitespace
    tokens = text.split()
    # Remove stopwords and short words
    tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    return ' '.join(tokens)

def extract_text_from_txt(file):
    """Extract text from TXT file"""
    return file.getvalue().decode('utf-8')

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
    # Simple sentence splitting based on periods followed by space
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

def add_document(file, doc_type=None, party=None, date=None, language=None, case_name=None):
    """Add document to the session state"""
    try:
        text = extract_text_from_txt(file)
        if text:
            # Auto-detect document type and party if not provided
            detected_doc_type = doc_type or get_document_type(file.name)
            detected_party = party or get_party(file.name)
            
            # Create document chunks for better search
            chunks = create_document_chunks(text)
            
            # Create document entry
            doc_id = f"doc_{len(st.session_state['documents']) + 1}"
            doc_data = {
                'id': doc_id,
                'filename': file.name,
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
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
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
        if date_range:
            doc_date = datetime.strptime(doc['date'], "%Y-%m-%d")
            if not (date_range[0] <= doc_date <= date_range[1]):
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
                # Basic highlighting by wrapping terms in markdown bold tags
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

# UI Components
def page_header():
    """Display page header with title"""
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("⚖️", font="60px")
    with col2:
        st.title("Sports Arbitration Document Search")
        st.markdown("A specialized search system for sports arbitration cases")

def sidebar_navigation():
    """Sidebar navigation menu"""
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Home", "Case Management", "Document Upload", "Search", "Analytics"])
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Current Case")
    
    # Case selection or creation
    if st.session_state['cases']:
        current_case = st.sidebar.selectbox(
            "Select Case", 
            st.session_state['cases'],
            index=st.session_state['cases'].index(st.session_state['current_case']) 
                  if st.session_state['current_case'] in st.session_state['cases'] else 0
        )
        if current_case != st.session_state['current_case']:
            st.session_state['current_case'] = current_case
            st.experimental_rerun()
    
    new_case = st.sidebar.text_input("Create New Case")
    if st.sidebar.button("Add Case") and new_case:
        if new_case not in st.session_state['cases']:
            st.session_state['cases'].append(new_case)
            st.session_state['current_case'] = new_case
            st.experimental_rerun()
    
    # Document statistics
    st.sidebar.markdown("---")
    st.sidebar.subheader("Document Statistics")
    
    if st.session_state['documents']:
        case_docs = [doc for doc in st.session_state['documents'].values() 
                    if doc['case'] == st.session_state['current_case']]
        
        st.sidebar.markdown(f"**Total Documents:** {len(case_docs)}")
        
        # Count by document type
        doc_types = Counter([doc['type'] for doc in case_docs])
        if doc_types:
            st.sidebar.markdown("**By Document Type:**")
            for doc_type, count in doc_types.items():
                st.sidebar.markdown(f"- {doc_type}: {count}")
    
    return page

def home_page():
    """Home page with overview and instructions"""
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
    2. Upload your documents (text files)
    3. Use the search functionality to find relevant information
    4. Export your findings
    
    ### Supported File Formats:
    - Text files (.txt)
    """)
    
    # Display sample workflow
    st.subheader("Sample Workflow")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("#### 1. Create Case")
        st.markdown("📁")
        st.markdown("Set up a new case file")
    with col2:
        st.markdown("#### 2. Upload Documents")
        st.markdown("📤")
        st.markdown("Add submissions and exhibits")
    with col3:
        st.markdown("#### 3. Search")
        st.markdown("🔍")
        st.markdown("Find relevant content")
    with col4:
        st.markdown("#### 4. Export")
        st.markdown("📊")
        st.markdown("Create reports")

def case_management_page():
    """Case management page"""
    st.header("Case Management")
    
    # Case details section
    if st.session_state['current_case']:
        st.subheader(f"Case: {st.session_state['current_case']}")
        
        # Case metadata form
        with st.expander("Edit Case Details", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Case Number", key="case_number")
                st.selectbox("Jurisdiction", [
                    "Court of Arbitration for Sport (CAS)",
                    "FIFA Dispute Resolution Chamber",
                    "FIFA Players' Status Committee",
                    "UEFA Control, Ethics and Disciplinary Body",
                    "National Sports Arbitration",
                    "Other"
                ], key="jurisdiction")
            with col2:
                st.date_input("Filing Date", key="filing_date")
                st.selectbox("Status", [
                    "Active",
                    "Pending",
                    "Hearing Scheduled",
                    "Decision Pending",
                    "Closed",
                    "Appealed"
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
                    'Date': doc['date'],
                    'Language': doc['language']
                })
            
            df = pd.DataFrame(doc_list)
            
            # Display as a table with filters
            doc_types = ['All'] + list(set(df['Type'].tolist()))
            parties = ['All'] + list(set(df['Party'].tolist()))
            
            col1, col2 = st.columns(2)
            with col1:
                filter_type = st.selectbox("Filter by Type", doc_types)
            with col2:
                filter_party = st.selectbox("Filter by Party", parties)
            
            # Apply filters
            filtered_df = df.copy()
            if filter_type != 'All':
                filtered_df = filtered_df[filtered_df['Type'] == filter_type]
            if filter_party != 'All':
                filtered_df = filtered_df[filtered_df['Party'] == filter_party]
            
            # Display table
            st.dataframe(filtered_df)
            
            # Document preview
            selected_doc_id = st.selectbox("Select document to preview", filtered_df['ID'].tolist())
            
            if selected_doc_id:
                doc = st.session_state['documents'][selected_doc_id]
                
                st.subheader(f"Preview: {doc['filename']}")
                
                # Document metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Type:** {doc['type']}")
                with col2:
                    st.markdown(f"**Party:** {doc['party']}")
                with col3:
                    st.markdown(f"**Date:** {doc['date']}")
                
                # Text preview (first 500 characters)
                st.text_area("Document Preview", value=doc['text'][:1000] + "...", height=200)
        else:
            st.info("No documents found for this case. Please upload documents from the Document Upload page.")
    else:
        st.warning("Please create or select a case from the sidebar.")

def document_upload_page():
    """Document upload page"""
    st.header("Document Upload")
    
    if not st.session_state['current_case']:
        st.warning("Please create or select a case from the sidebar first.")
        return
    
    st.subheader(f"Upload Documents for: {st.session_state['current_case']}")
    
    # Single file upload with metadata
    uploaded_file = st.file_uploader("Upload Document", type=['txt'])
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        with col1:
            doc_type = st.selectbox("Document Type", [
                "Submission",
                "Exhibit",
                "Decision",
                "Transcript",
                "Contract",
                "Correspondence",
                "Expert Report",
                "Witness Statement",
                "Other"
            ])
            party = st.selectbox("Party", [
                "Appellant/Claimant",
                "Respondent/Defendant",
                "Arbitrator/Tribunal",
                "Expert",
                "Witness",
                "Third Party",
                "Unknown"
            ])
        with col2:
            date = st.date_input("Document Date")
            language = st.selectbox("Language", [
                "English",
                "French",
                "Spanish",
                "German",
                "Italian",
                "Portuguese",
                "Other"
            ])
        
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                doc_id = add_document(
                    uploaded_file, 
                    doc_type=doc_type,
                    party=party,
                    date=date.strftime("%Y-%m-%d"),
                    language=language,
                    case_name=st.session_state['current_case']
                )
                
                if doc_id:
                    st.success(f"Document {uploaded_file.name} processed successfully!")
                else:
                    st.error("Failed to process document. Please try again.")
    
    # Batch upload option
    st.subheader("Batch Upload")
    st.markdown("Upload multiple documents at once (metadata will be auto-detected)")
    
    batch_files = st.file_uploader("Upload Multiple Documents", type=['txt'], accept_multiple_files=True)
    
    if batch_files and st.button("Process All Documents"):
        progress_bar = st.progress(0)
        for i, file in enumerate(batch_files):
            with st.spinner(f"Processing {file.name}..."):
                doc_id = add_document(file, case_name=st.session_state['current_case'])
                if doc_id:
                    st.write(f"✅ {file.name} processed successfully")
                else:
                    st.write(f"❌ Failed to process {file.name}")
            progress_bar.progress((i + 1) / len(batch_files))
        
        st.success(f"Processed {len(batch_files)} documents")

    # Sample document generator
    st.subheader("Create Sample Document")
    st.markdown("Generate a sample document for testing")
    
    with st.expander("Sample Document Generator"):
        sample_type = st.selectbox("Sample Document Type", [
            "Claimant Submission",
            "Respondent Submission",
            "Arbitral Award",
            "Contract Exhibit"
        ])
        
        if st.button("Generate Sample"):
            sample_text = ""
            filename = ""
            
            if sample_type == "Claimant Submission":
                filename = "claimant_submission_sample.txt"
                sample_text = """CLAIMANT SUBMISSION
                
Court of Arbitration for Sport
Case Reference: CAS 2023/A/0001

APPELLANT'S SUBMISSION

I. INTRODUCTION

1. The Appellant, FC United, submits this brief in support of its appeal against the decision rendered by the FIFA Players' Status Committee on 15 January 2023 (the "Decision").

2. This case concerns the unilateral termination of the employment contract between the Appellant and Coach John Smith without just cause.

II. FACTS OF THE CASE

3. On 1 June 2022, the Appellant and Coach Smith entered into an employment contract valid until 31 May 2023 (the "Contract").

4. According to the Contract, Coach Smith was entitled to receive a monthly salary of EUR 10,000.

5. On 15 October 2022, following a series of poor results, the Appellant terminated the Contract with immediate effect.

6. The Appellant submits that Coach Smith failed to fulfill his contractual obligations by demonstrating unprofessional behavior and failing to maintain team discipline.

III. LEGAL ARGUMENTS

7. The Appellant respectfully submits that the termination of the Contract was with just cause due to the following reasons:

   a) Coach Smith repeatedly arrived late to training sessions;
   b) Coach Smith failed to implement the agreed-upon tactical approach;
   c) The team's performance significantly deteriorated under Coach Smith's leadership.

8. According to Article 14 of the Contract, the Appellant had the right to terminate the Contract in case of serious breach by Coach Smith.

9. The FIFA Players' Status Committee erred in its assessment of what constitutes just cause under Swiss law.

IV. CONCLUSION

10. For the foregoing reasons, the Appellant respectfully requests the Court of Arbitration for Sport to:

    a) Set aside the Decision;
    b) Establish that the Contract was terminated with just cause;
    c) Reject Coach Smith's claim for compensation.

Respectfully submitted,
FC United
Date: 15 February 2023"""
                
            elif sample_type == "Respondent Submission":
                filename = "respondent_submission_sample.txt"
                sample_text = """RESPONDENT SUBMISSION
                
Court of Arbitration for Sport
Case Reference: CAS 2023/A/0001

RESPONDENT'S ANSWER

I. INTRODUCTION

1. The Respondent, Coach John Smith, submits this answer in response to the appeal filed by FC United against the decision rendered by the FIFA Players' Status Committee on 15 January 2023 (the "Decision").

2. The Respondent maintains that FC United terminated his employment contract without just cause and therefore must pay compensation.

II. FACTS OF THE CASE

3. On 1 June 2022, the Respondent and FC United entered into an employment contract valid until 31 May 2023 (the "Contract").

4. According to the Contract, the Respondent was entitled to receive a monthly salary of EUR 10,000.

5. On 15 October 2022, FC United terminated the Contract with immediate effect, citing poor sports results as the reason.

6. The Respondent contests the allegations of unprofessional behavior and submits that he fully complied with his contractual obligations.

III. LEGAL ARGUMENTS

7. The Respondent respectfully submits that the termination of the Contract was without just cause for the following reasons:

   a) Poor sporting results do not constitute just cause under well-established CAS jurisprudence;
   b) No warning was given to the Respondent prior to termination;
   c) The allegations of unprofessional behavior are unsubstantiated.

8. According to CAS jurisprudence, specifically CAS 2011/A/2596, the absence of sporting results cannot constitute just cause for termination of a coaching contract.

9. The FIFA Players' Status Committee correctly applied Swiss law in determining that the termination was without just cause.

IV. CONCLUSION

10. For the foregoing reasons, the Respondent respectfully requests the Court of Arbitration for Sport to:

    a) Dismiss the appeal;
    b) Confirm that the Contract was terminated without just cause;
    c) Order FC United to pay the remaining value of the Contract (EUR 70,000) with interest.

Respectfully submitted,
Coach John Smith
Date: 1 March 2023"""
                
            elif sample_type == "Arbitral Award":
                filename = "arbitral_award_sample.txt"
                sample_text = """ARBITRAL AWARD
                
Court of Arbitration for Sport
Case Reference: CAS 2023/A/0001

ARBITRAL AWARD

delivered by the
COURT OF ARBITRATION FOR SPORT

sitting in the following composition:

President: Ms. Jane Doe
Arbitrators: Mr. John Richards, Prof. Maria Rodriguez

in the arbitration between

FC United, Appellant

and

Coach John Smith, Respondent

I. PARTIES

1. FC United (the "Appellant") is a professional football club based in Switzerland.

2. Coach John Smith (the "Respondent") is a professional football coach of German nationality.

II. FACTUAL BACKGROUND

3. On 1 June 2022, the Parties signed an employment contract valid until 31 May 2023 (the "Contract").

4. On 15 October 2022, following several defeats, the Appellant terminated the Contract with immediate effect.

5. On 20 October 2022, the Respondent filed a claim with FIFA claiming compensation for breach of contract.

III. PROCEEDINGS BEFORE FIFA

6. On 15 January 2023, the FIFA Players' Status Committee (the "PSC") ruled that the Appellant had terminated the Contract without just cause and ordered payment of EUR 70,000 as compensation.

7. On 15 February 2023, the Appellant filed an appeal with the Court of Arbitration for Sport.

IV. LEGAL ANALYSIS

8. The Panel has carefully considered the submissions and evidence presented by both Parties.

9. The central issue in this case is whether the Appellant had just cause to terminate the Contract.

10. According to established CAS jurisprudence, poor sporting results do not constitute just cause for termination of a coaching contract (CAS 2011/A/2596).

11. The Panel finds that the Appellant has not proven that the Respondent breached his contractual obligations in a manner that would justify immediate termination.

V. DECISION

12. The Panel dismisses the appeal and confirms the decision of the FIFA Players' Status Committee.

13. FC United shall pay Coach John Smith EUR 70,000 as compensation for breach of contract, plus 5% interest from 15 January 2023.

14. The arbitration costs shall be borne by the Appellant.

Seat of arbitration: Lausanne, Switzerland
Date: 15 May 2023

The President of the Panel
Jane Doe"""
                
            elif sample_type == "Contract Exhibit":
                filename = "contract_exhibit_sample.txt"
                sample_text = """CONTRACT EXHIBIT
                
EMPLOYMENT CONTRACT

between

FC United
Sportweg 1, 8001 Zurich, Switzerland
(hereinafter referred to as the "Club")

and

Coach John Smith
Hauptstrasse 123, 10115 Berlin, Germany
(hereinafter referred to as the "Coach")

1. DURATION

1.1 This contract is valid from 1 June 2022 until 31 May 2023.

2. REMUNERATION

2.1 The Coach shall receive a monthly salary of EUR 10,000 (ten thousand euros), payable on the last day of each month.

2.2 The Coach shall be entitled to the following bonuses:
   - EUR 50,000 for winning the national championship
   - EUR 25,000 for winning the national cup
   - EUR 100,000 for qualification to the UEFA Champions League

3. DUTIES

3.1 The Coach shall be responsible for:
   a) Training and managing the first team
   b) Match preparation and tactical decisions
   c) Player development
   d) Attending official Club events

4. TERMINATION

4.1 This contract may be terminated by mutual agreement of the Parties.

4.2 Either Party may terminate this contract with just cause according to Swiss law.

4.3 "Just cause" shall include any serious breach of the terms and conditions of this contract, the disciplinary rules of the Club, or constant wrongful behavior by either Party.

5. APPLICABLE LAW AND JURISDICTION

5.1 This contract is governed by Swiss law.

5.2 Any dispute arising from or related to this contract shall be submitted to the FIFA Players' Status Committee.

Signed on 1 June 2022 in Zurich, Switzerland.

For FC United:                        Coach:
[Signature]                           [Signature]
Peter Johnson                         John Smith
President                             Head Coach"""
            
            # Create temporary file
            if sample_text and filename:
                # Convert string to bytes
                sample_bytes = sample_text.encode('utf-8')
                
                # Create a BytesIO object
                bytes_io = BytesIO(sample_bytes)
                
                # Create a fake file-like object
                class FakeFile:
                    def __init__(self, name, content):
                        self.name = name
                        self.content = content
                    
                    def getvalue(self):
                        return self.content
                
                fake_file = FakeFile(filename, bytes_io)
                
                # Process the sample document
                doc_id = add_document(
                    fake_file, 
                    doc_type=sample_type.split()[0],
                    party="Appellant/Claimant" if "
