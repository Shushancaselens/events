import streamlit as st
import pandas as pd
import numpy as np
import re
import os
from io import StringIO
import base64
from datetime import datetime
import docx2txt
import PyPDF2
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
import json
import zipfile
import io
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

# Download required NLTK packages
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Add domain-specific stopwords
legal_stopwords = {'court', 'case', 'appeal', 'defendant', 'plaintiff', 'appellant', 'respondent', 
                   'exhibit', 'document', 'evidence', 'witness', 'testimony', 'judge', 'tribunal', 
                   'arbitration', 'arbitrator', 'law', 'legal', 'paragraph', 'submission'}
stop_words.update(legal_stopwords)

# Initialize session state for document storage
if 'documents' not in st.session_state:
    st.session_state['documents'] = {}
if 'current_case' not in st.session_state:
    st.session_state['current_case'] = None
if 'cases' not in st.session_state:
    st.session_state['cases'] = []
if 'search_history' not in st.session_state:
    st.session_state['search_history'] = []

# Document processing functions
def preprocess_text(text):
    """Clean and preprocess text for better search"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    # Tokenize
    tokens = word_tokenize(text)
    # Remove stopwords and lemmatize
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words and len(word) > 2]
    return ' '.join(tokens)

def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    return docx2txt.process(file)

def extract_text(file):
    """Extract text from various file formats"""
    file_extension = file.name.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(file)
    elif file_extension in ['docx', 'doc']:
        return extract_text_from_docx(file)
    elif file_extension in ['txt', 'text']:
        return file.getvalue().decode('utf-8')
    else:
        st.error(f"Unsupported file format: {file_extension}")
        return None

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
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    # Add the last chunk if it's not empty
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def add_document(file, doc_type=None, party=None, date=None, language=None, case_name=None):
    """Add document to the session state"""
    text = extract_text(file)
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
                # Basic highlighting (can be improved)
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
    """Display page header with logo and title"""
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://img.icons8.com/color/96/000000/scales--v1.png", width=80)
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
    2. Upload your documents
    3. Use the search functionality to find relevant information
    4. Export your findings
    
    ### Supported File Formats:
    - PDF (.pdf)
    - Word Documents (.docx, .doc)
    - Text files (.txt)
    """)
    
    # Display sample workflow
    st.subheader("Sample Workflow")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("#### 1. Create Case")
        st.image("https://img.icons8.com/color/96/000000/add-folder.png", width=50)
        st.markdown("Set up a new case file")
    with col2:
        st.markdown("#### 2. Upload Documents")
        st.image("https://img.icons8.com/color/96/000000/upload.png", width=50)
        st.markdown("Add submissions and exhibits")
    with col3:
        st.markdown("#### 3. Search")
        st.image("https://img.icons8.com/color/96/000000/search.png", width=50)
        st.markdown("Find relevant content")
    with col4:
        st.markdown("#### 4. Export")
        st.image("https://img.icons8.com/color/96/000000/export.png", width=50)
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
    uploaded_file = st.file_uploader("Upload Document", type=['pdf', 'docx', 'doc', 'txt'])
    
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
    
    batch_files = st.file_uploader("Upload Multiple Documents", type=['pdf', 'docx', 'doc', 'txt'], accept_multiple_files=True)
    
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

def search_page():
    """Search page"""
    st.header("Document Search")
    
    if not st.session_state['current_case']:
        st.warning("Please create or select a case from the sidebar first.")
        return
    
    if not st.session_state['documents']:
        st.warning("No documents found. Please upload documents first.")
        return
    
    st.subheader(f"Search in: {st.session_state['current_case']}")
    
    # Search input and filters
    query = st.text_input("Search Query", placeholder="Enter search terms...")
    
    with st.expander("Advanced Filters", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            # Get unique document types for this case
            case_docs = [doc for doc in st.session_state['documents'].values() 
                        if doc['case'] == st.session_state['current_case']]
            doc_types = ['All'] + list(set([doc['type'] for doc in case_docs]))
            doc_type_filter = st.selectbox("Document Type", doc_types)
            
            # Date range filter
            use_date_filter = st.checkbox("Filter by Date")
            if use_date_filter:
                date_range = st.date_input(
                    "Date Range",
                    value=[
                        datetime.strptime(min([doc['date'] for doc in case_docs]), "%Y-%m-%d"),
                        datetime.strptime(max([doc['date'] for doc in case_docs]), "%Y-%m-%d")
                    ]
                )
            else:
                date_range = None
        
        with col2:
            # Get unique parties for this case
            parties = ['All'] + list(set([doc['party'] for doc in case_docs]))
            party_filter = st.selectbox("Party", parties)
            
            # Exact phrase matching
            exact_match = st.checkbox("Exact Phrase Match")
    
    # Apply filters
    case_filter = st.session_state['current_case']
    if doc_type_filter == 'All':
        doc_type_filter = None
    if party_filter == 'All':
        party_filter = None
    
    # Search button
    col1, col2 = st.columns([1, 5])
    with col1:
        search_button = st.button("Search")
    with col2:
        st.markdown("#### Recent Searches:")
        if st.session_state['search_history']:
            recent_searches = st.session_state['search_history'][-3:]
            for i, search in enumerate(reversed(recent_searches)):
                if st.button(f"{search['query']} ({search['results_count']} results)", key=f"recent_{i}"):
                    query = search['query']
                    search_button = True
    
    # Execute search
    if search_button and query:
        # Modify the query if exact match is checked
        search_query = f'"{query}"' if exact_match else query
        
        with st.spinner("Searching..."):
            results = search_documents(
                search_query,
                case_filter=case_filter,
                doc_type_filter=doc_type_filter,
                party_filter=party_filter,
                date_range=date_range
            )
        
        # Display results
        st.subheader(f"Search Results: {len(results)} matches found")
        
        if results:
            # Results summary
            doc_count = len(set([r['doc_id'] for r in results]))
            st.markdown(f"Found matches in {doc_count} documents")
            
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
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Type:** {doc['type']}")
                    with col2:
                        st.markdown(f"**Party:** {doc['party']}")
                    with col3:
                        st.markdown(f"**Date:** {doc['date']}")
                    
                    # Display each match within the document
                    for i, result in enumerate(doc_results):
                        st.markdown(f"#### Match {i+1}:")
                        st.markdown(result['highlighted_chunk'], unsafe_allow_html=True)
                        st.markdown("---")
            
            # Export options
            st.subheader("Export Results")
            col1, col2 = st.columns(2)
            with col1:
                export_format = st.selectbox("Export Format", ["Markdown", "CSV"])
            with col2:
                if st.button("Export"):
                    if export_format == "Markdown":
                        export_data = export_results(results, "markdown")
                        mime_type = "text/markdown"
                        filename = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    else:  # CSV
                        export_data = export_results(results, "csv")
                        mime_type = "text/csv"
                        filename = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    
                    b64 = base64.b64encode(export_data.encode()).decode()
                    href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Download {export_format} file</a>'
                    st.markdown(href, unsafe_allow_html=True)
        else:
            st.info("No results found. Try modifying your search query or filters.")
    
    # Search tips
    with st.expander("Search Tips", expanded=False):
        st.markdown("""
        ### Effective Search Strategies
        
        - **Use specific terms** from legal or sports contexts
        - **Combine terms** to narrow results (e.g., "contract termination sporting results")
        - **Use quotes** for exact phrase matching (e.g., "without just cause")
        - **Filter by document type** to focus on submissions or exhibits
        - **Search for case references** to find precedents (e.g., "CAS 2011/A/2596")
        
        ### Example Searches
        
        - Contract termination without just cause
        - Sporting results poor performance
        - Compensation calculation
        - FIFA regulations coaches
        - Swiss law employment contract
        """)

def analytics_page():
    """Analytics and insights page"""
    st.header("Analytics & Insights")
    
    if not st.session_state['current_case']:
        st.warning("Please create or select a case from the sidebar first.")
        return
    
    if not st.session_state['documents']:
        st.warning("No documents found. Please upload documents first.")
        return
    
    # Get documents for current case
    case_docs = [doc for doc in st.session_state['documents'].values() 
                if doc['case'] == st.session_state['current_case']]
    
    st.subheader(f"Case Analysis: {st.session_state['current_case']}")
    
    # Document composition
    st.markdown("### Document Composition")
    
    # Document types pie chart
    doc_types = Counter([doc['type'] for doc in case_docs])
    fig1 = px.pie(
        names=list(doc_types.keys()),
        values=list(doc_types.values()),
        title="Documents by Type"
    )
    st.plotly_chart(fig1)
    
    # Document timeline
    st.markdown("### Document Timeline")
    
    # Prepare timeline data
    timeline_data = []
    for doc in case_docs:
        timeline_data.append({
            'date': doc['date'],
            'type': doc['type'],
            'party': doc['party'],
            'filename': doc['filename']
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    timeline_df['date'] = pd.to_datetime(timeline_df['date'])
    timeline_df = timeline_df.sort_values('date')
    
    # Plot timeline
    fig2 = px.scatter(
        timeline_df,
        x='date',
        y='type',
        color='party',
        hover_name='filename',
        title="Document Timeline"
    )
    st.plotly_chart(fig2)
    
    # Term frequency analysis
    st.markdown("### Key Terms Analysis")
    
    # Extract and count terms
    all_terms = []
    for doc in case_docs:
        terms = doc['processed_text'].split()
        all_terms.extend(terms)
    
    term_counts = Counter(all_terms).most_common(20)
    term_df = pd.DataFrame(term_counts, columns=['term', 'count'])
    
    # Plot term frequency
    fig3 = px.bar(
        term_df,
        x='count',
        y='term',
        orientation='h',
        title="Most Frequent Terms",
        color='count',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig3)
    
    # Key term search
    st.markdown("### Key Term Explorer")
    selected_term = st.selectbox("Select a term to explore", term_df['term'].tolist())
    
    if selected_term and st.button("Find Occurrences"):
        # Auto-execute a search for this term
        with st.spinner(f"Finding occurrences of '{selected_term}'..."):
            results = search_documents(selected_term, case_filter=st.session_state['current_case'])
            
            if results:
                st.subheader(f"Found {len(results)} occurrences of '{selected_term}'")
                
                # Display each occurrence with context
                for i, result in enumerate(results[:10]):  # Limit to first 10 for performance
                    with st.expander(f"Occurrence {i+1} in {result['filename']}", expanded=i==0):
                        st.markdown(result['highlighted_chunk'], unsafe_allow_html=True)
            else:
                st.info(f"No occurrences of '{selected_term}' found.")
