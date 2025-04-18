import streamlit as st
import pandas as pd
import re
from io import StringIO
import PyPDF2
import docx
import numpy as np
from collections import Counter
import tempfile
import os

st.set_page_config(page_title="Sports Arbitration Document Assistant", layout="wide")
st.title("Sports Arbitration Document Assistant")

# Function to read PDF files
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text() + "\n--- Page Break ---\n"
    return text

# Function to read DOCX files
def read_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Function to read TXT files
def read_txt(file):
    return file.getvalue().decode("utf-8")

# Function to extract text from uploaded files
def extract_text(uploaded_file):
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        file_extension = uploaded_file.name.split(".")[-1].lower()
        
        if file_extension == "pdf":
            with open(tmp_file_path, "rb") as f:
                text = read_pdf(f)
        elif file_extension in ["docx", "doc"]:
            text = read_docx(tmp_file_path)
        elif file_extension == "txt":
            text = uploaded_file.getvalue().decode("utf-8")
        else:
            text = "Unsupported file type."
            
        return text
    finally:
        # Delete the temporary file
        os.unlink(tmp_file_path)

# Function to analyze document structure
def analyze_document(text):
    # Split text into paragraphs
    paragraphs = text.split("\n")
    paragraphs = [p for p in paragraphs if p.strip()]
    
    # Identify potential section headers
    potential_headers = []
    for i, para in enumerate(paragraphs):
        if len(para.strip()) < 100 and (para.strip().endswith(":") or para.strip().isupper() or re.match(r'^\d+\.', para.strip())):
            potential_headers.append((i, para.strip()))
    
    return {
        "total_paragraphs": len(paragraphs),
        "potential_sections": len(potential_headers),
        "sample_sections": potential_headers[:5] if potential_headers else [],
        "word_count": len(text.split())
    }

# Function to find context around search term
def find_context(text, search_term, context_size=100):
    if not search_term:
        return []
    
    search_pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    matches = list(search_pattern.finditer(text))
    results = []
    
    for match in matches:
        start = max(0, match.start() - context_size)
        end = min(len(text), match.end() + context_size)
        context = text[start:end]
        
        # Highlight the match
        match_start_in_context = match.start() - start
        match_end_in_context = match.end() - start
        highlighted = context[:match_start_in_context] + f"**{context[match_start_in_context:match_end_in_context]}**" + context[match_end_in_context:]
        
        # Find the page if available
        page_match = re.findall(r'--- Page Break ---', text[:match.start()])
        page_number = len(page_match) + 1 if page_match else "N/A"
        
        results.append({
            "context": highlighted,
            "page": page_number
        })
    
    return results

# Function to extract key arguments
def extract_key_arguments(text):
    # Look for argumentative phrases
    arg_phrases = [
        r'(?:submit|argue|allege|claim|assert|contend)(?:s|ed)?(?:\s+that)?',
        r'(?:in (?:our|their) (?:view|opinion|submission))',
        r'(?:maintain(?:s|ed)?)',
        r'(?:position is)',
        r'(?:according to)',
    ]
    
    pattern = '|'.join(arg_phrases)
    matches = re.finditer(pattern, text, re.IGNORECASE)
    
    arguments = []
    for match in matches:
        start = match.start()
        # Find the end of the sentence or next 200 characters
        end_period = text.find('.', start)
        if end_period == -1 or end_period > start + 200:
            end_period = start + 200
        else:
            end_period += 1
        
        argument = text[start:end_period].strip()
        if len(argument) > 20:  # Skip very short matches
            arguments.append(argument)
    
    return arguments[:10]  # Return top 10 arguments

# Function to compare documents
def compare_documents(doc1, doc2):
    # Simple word frequency comparison
    words1 = Counter(re.findall(r'\b[a-zA-Z]{3,}\b', doc1.lower()))
    words2 = Counter(re.findall(r'\b[a-zA-Z]{3,}\b', doc2.lower()))
    
    # Find unique words in each document
    unique_to_doc1 = {word: count for word, count in words1.items() if word not in words2}
    unique_to_doc2 = {word: count for word, count in words2.items() if word not in words1}
    
    # Find common words with different frequencies
    common_words = {word: (words1[word], words2[word]) for word in set(words1) & set(words2)}
    
    # Sort by frequency difference
    sorted_common = sorted(common_words.items(), key=lambda x: abs(x[1][0] - x[1][1]), reverse=True)
    
    return {
        "unique_to_doc1": dict(sorted(unique_to_doc1.items(), key=lambda x: x[1], reverse=True)[:20]),
        "unique_to_doc2": dict(sorted(unique_to_doc2.items(), key=lambda x: x[1], reverse=True)[:20]),
        "different_usage": dict(sorted_common[:20])
    }

# Sidebar for document upload and management
with st.sidebar:
    st.header("Document Management")
    
    uploaded_files = st.file_uploader("Upload documents", accept_multiple_files=True, type=["pdf", "docx", "doc", "txt"])
    
    st.subheader("Document Labels")
    doc_labels = {}
    
    if uploaded_files:
        for i, file in enumerate(uploaded_files):
            default_label = file.name
            if "claim" in file.name.lower() or "appellant" in file.name.lower():
                default_label = "Claimant/Appellant Document"
            elif "respond" in file.name.lower():
                default_label = "Respondent Document"
            elif "exhibit" in file.name.lower() or "evidence" in file.name.lower():
                default_label = "Exhibit"
            
            doc_labels[i] = st.text_input(f"Label for {file.name}", value=default_label, key=f"label_{i}")
    
    st.subheader("Search Options")
    search_term = st.text_input("Search term")
    
    advanced_search = st.checkbox("Advanced Search Options")
    
    if advanced_search:
        search_doc_type = st.multiselect("Search in document types", 
                                      options=["Claimant", "Respondent", "Exhibits", "All"],
                                      default=["All"])
        exact_match = st.checkbox("Exact match")
    else:
        search_doc_type = ["All"]
        exact_match = False

# Main content
if not uploaded_files:
    st.info("Please upload documents to begin analysis")
else:
    # Process uploaded files
    documents = []
    for i, file in enumerate(uploaded_files):
        with st.spinner(f"Processing {file.name}..."):
            text = extract_text(file)
            doc_analysis = analyze_document(text)
            documents.append({
                "id": i,
                "name": file.name,
                "label": doc_labels[i],
                "text": text,
                "analysis": doc_analysis
            })
    
    # Display tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["Document Overview", "Search Results", "Document Comparison", "Argument Analysis"])
    
    with tab1:
        st.header("Document Overview")
        
        for doc in documents:
            with st.expander(f"{doc['label']} ({doc['name']})"):
                st.write(f"**Word count:** {doc['analysis']['word_count']}")
                st.write(f"**Paragraphs:** {doc['analysis']['total_paragraphs']}")
                st.write(f"**Potential sections:** {doc['analysis']['potential_sections']}")
                
                if doc['analysis']['sample_sections']:
                    st.write("**Sample sections:**")
                    for idx, section in doc['analysis']['sample_sections']:
                        st.write(f"- {section}")
                
                # Preview first 500 characters
                st.subheader("Document Preview")
                st.write(doc['text'][:500] + "...")
    
    with tab2:
        st.header("Search Results")
        
        if search_term:
            all_results = []
            
            for doc in documents:
                # Filter by document type if needed
                if "All" not in search_doc_type:
                    doc_type_matches = False
                    for search_type in search_doc_type:
                        if search_type.lower() in doc['label'].lower():
                            doc_type_matches = True
                            break
                    if not doc_type_matches:
                        continue
                
                # Perform search
                if exact_match:
                    results = find_context(doc['text'], search_term)
                else:
                    # Split search term into words for non-exact matching
                    search_words = search_term.split()
                    if len(search_words) == 1:
                        results = find_context(doc['text'], search_term)
                    else:
                        # Search for each word and then find common contexts
                        all_word_results = []
                        for word in search_words:
                            if len(word) > 3:  # Skip short words
                                all_word_results.extend(find_context(doc['text'], word))
                        
                        # Deduplicate results
                        seen_contexts = set()
                        results = []
                        for res in all_word_results:
                            context_key = res['context'][:50]  # Use first 50 chars as key
                            if context_key not in seen_contexts:
                                seen_contexts.add(context_key)
                                results.append(res)
                
                for result in results:
                    all_results.append({
                        "document": doc['label'],
                        "filename": doc['name'],
                        "page": result['page'],
                        "context": result['context']
                    })
            
            if all_results:
                st.write(f"Found {len(all_results)} results for '{search_term}'")
                
                results_df = pd.DataFrame(all_results)
                
                # Group by document
                for doc_name in results_df['document'].unique():
                    doc_results = results_df[results_df['document'] == doc_name]
                    with st.expander(f"{doc_name} ({len(doc_results)} results)"):
                        for i, row in doc_results.iterrows():
                            st.markdown(f"**Page {row['page']}:** {row['context']}")
                            st.markdown("---")
            else:
                st.warning(f"No results found for '{search_term}'")
        else:
            st.info("Enter a search term to find relevant content across documents")
    
    with tab3:
        st.header("Document Comparison")
        
        if len(documents) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                doc1_idx = st.selectbox("Select first document", 
                                     options=range(len(documents)),
                                     format_func=lambda x: f"{documents[x]['label']} ({documents[x]['name']})")
            
            with col2:
                doc2_idx = st.selectbox("Select second document", 
                                     options=range(len(documents)),
                                     format_func=lambda x: f"{documents[x]['label']} ({documents[x]['name']})")
            
            if st.button("Compare Documents"):
                with st.spinner("Comparing documents..."):
                    comparison = compare_documents(documents[doc1_idx]['text'], documents[doc2_idx]['text'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader(f"Unique to {documents[doc1_idx]['label']}")
                        for word, count in comparison['unique_to_doc1'].items():
                            st.write(f"- {word} ({count} occurrences)")
                    
                    with col2:
                        st.subheader(f"Unique to {documents[doc2_idx]['label']}")
                        for word, count in comparison['unique_to_doc2'].items():
                            st.write(f"- {word} ({count} occurrences)")
                    
                    st.subheader("Different Usage of Common Terms")
                    diff_data = []
                    for word, (count1, count2) in comparison['different_usage'].items():
                        diff_data.append({
                            "Term": word,
                            f"{documents[doc1_idx]['label']}": count1,
                            f"{documents[doc2_idx]['label']}": count2,
                            "Difference": abs(count1 - count2)
                        })
                    
                    diff_df = pd.DataFrame(diff_data)
                    st.dataframe(diff_df)
        else:
            st.info("Upload at least two documents to use the comparison feature")
    
    with tab4:
        st.header("Argument Analysis")
        
        selected_doc = st.selectbox("Select document for argument analysis", 
                                  options=range(len(documents)),
                                  format_func=lambda x: f"{documents[x]['label']} ({documents[x]['name']})")
        
        if st.button("Extract Key Arguments"):
            with st.spinner("Analyzing arguments..."):
                arguments = extract_key_arguments(documents[selected_doc]['text'])
                
                if arguments:
                    st.subheader("Key Arguments Identified")
                    for i, arg in enumerate(arguments, 1):
                        st.markdown(f"{i}. {arg}")
                        st.markdown("---")
                else:
                    st.warning("No clear arguments identified. Try a different document.")
