import streamlit as st
import pandas as pd
import re
from collections import Counter

st.set_page_config(page_title="Sports Arbitration Document Assistant (Simple)", layout="wide")
st.title("Sports Arbitration Document Assistant")
st.markdown("### Simplified Version (Text Files Only)")

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
        
        # Find paragraph number
        paragraph_number = len(text[:match.start()].split('\n'))
        
        results.append({
            "context": highlighted,
            "paragraph": paragraph_number
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

# Installation information
st.sidebar.header("Full Version Installation")
st.sidebar.markdown("""
To install the full version with PDF and DOCX support:

```
pip install PyPDF2 python-docx
```

Or download the requirements file:
""")

requirements_content = """
streamlit==1.24.0
pandas==2.0.3
PyPDF2==3.0.1
python-docx==0.8.11
"""

st.sidebar.download_button(
    label="Download requirements.txt",
    data=requirements_content,
    file_name="requirements.txt",
    mime="text/plain",
)

# Option to use text files or direct text input
input_option = st.sidebar.radio(
    "Input Method",
    ["Upload Text Files", "Direct Text Input"]
)

if input_option == "Upload Text Files":
    # Sidebar for document upload and management
    st.sidebar.header("Document Management")
    
    uploaded_files = st.sidebar.file_uploader("Upload text documents", accept_multiple_files=True, type=["txt"])
    
    # Document labels
    st.sidebar.subheader("Document Labels")
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
            
            doc_labels[i] = st.sidebar.text_input(f"Label for {file.name}", value=default_label, key=f"label_{i}")
    
    # Search options
    st.sidebar.subheader("Search Options")
    search_term = st.sidebar.text_input("Search term")
    exact_match = st.sidebar.checkbox("Exact match")
    
    # Main content
    if not uploaded_files:
        st.info("Please upload text documents to begin analysis")
    else:
        # Process uploaded files
        documents = []
        for i, file in enumerate(uploaded_files):
            with st.spinner(f"Processing {file.name}..."):
                text = file.getvalue().decode("utf-8")
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
                            "paragraph": result['paragraph'],
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
                                st.markdown(f"**Paragraph {row['paragraph']}:** {row['context']}")
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
else:
    # Direct text input
    st.sidebar.header("Document Management")
    
    # Setup for direct text input
    document_count = st.sidebar.number_input("Number of documents", min_value=1, max_value=5, value=2)
    
    # Search options
    st.sidebar.subheader("Search Options")
    search_term = st.sidebar.text_input("Search term")
    exact_match = st.sidebar.checkbox("Exact match")
    
    # Create document inputs
    documents = []
    for i in range(document_count):
        st.subheader(f"Document {i+1}")
        doc_label = st.text_input(f"Document {i+1} Label", value=f"Document {i+1}", key=f"label_{i}")
        doc_text = st.text_area(f"Enter text for Document {i+1}", height=200, key=f"text_{i}")
        
        if doc_text:
            doc_analysis = analyze_document(doc_text)
            documents.append({
                "id": i,
                "name": f"Document {i+1}",
                "label": doc_label,
                "text": doc_text,
                "analysis": doc_analysis
            })
    
    # Only show analysis if documents contain text
    if all(doc.get('text', '') for doc in documents):
        # Display tabs for different functionalities
        tab1, tab2, tab3, tab4 = st.tabs(["Document Overview", "Search Results", "Document Comparison", "Argument Analysis"])
        
        with tab1:
            st.header("Document Overview")
            
            for doc in documents:
                with st.expander(f"{doc['label']}"):
                    st.write(f"**Word count:** {doc['analysis']['word_count']}")
                    st.write(f"**Paragraphs:** {doc['analysis']['total_paragraphs']}")
                    st.write(f"**Potential sections:** {doc['analysis']['potential_sections']}")
                    
                    if doc['analysis']['sample_sections']:
                        st.write("**Sample sections:**")
                        for idx, section in doc['analysis']['sample_sections']:
                            st.write(f"- {section}")
        
        with tab2:
            st.header("Search Results")
            
            if search_term:
                all_results = []
                
                for doc in documents:
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
                            "paragraph": result['paragraph'],
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
                                st.markdown(f"**Paragraph {row['paragraph']}:** {row['context']}")
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
                                         format_func=lambda x: f"{documents[x]['label']}")
                
                with col2:
                    doc2_idx = st.selectbox("Select second document", 
                                         options=range(len(documents)),
                                         format_func=lambda x: f"{documents[x]['label']}")
                
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
                st.info("Enter text for at least two documents to use the comparison feature")
        
        with tab4:
            st.header("Argument Analysis")
            
            selected_doc = st.selectbox("Select document for argument analysis", 
                                      options=range(len(documents)),
                                      format_func=lambda x: f"{documents[x]['label']}")
            
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
    else:
        st.info("Please enter text for all documents to start analysis")

# Sample document text for easy testing
st.sidebar.markdown("---")
st.sidebar.header("Sample Document")
if st.sidebar.button("Use Sample Text"):
    sample_text = """ARBITRATION CAS 2011/A/2596 Anorthosis Famagusta FC v. Ernst Middendorp, award of 29 February 2012

The absence of sporting results cannot, as a general rule, constitute per se a reason to terminate a contractual relationship with just cause.

Notwithstanding that the FIFA Regulations on the Status and Transfer of Players (RSTP) is not directly applicable to coaches, the specific provisions of Articles 22 and 23 RSTP are directly applicable to coaches, thanks to the direct and explicit extension of the provisions to include matters relating to coaches. Prima facie, the FIFA Players Status Committee (PSC) is thus competent to deal with employment-related disputes between a club or an association and a coach of an international dimension, unless the exception clause mentioned in Article 22 RSTP is applicable. This exception clause will be applicable only on condition that reference has specifically been made in the contract to a national independent arbitration tribunal.

Article 17 RSTP is not applicable in a dispute concerning a coach (as opposed to a player). Article 1 RSTP ("Scope") provides that the Regulations concern "players", not coaches. Moreover, the FIFA Statutes no longer contain the provision which appeared in Article 33.4 of their 2001 version, which equated coaches with players.

Article 337c of the Swiss Code of Obligations (CO) provides that in case of termination without just cause of an employment contract of set duration, the employer must, in principle, pay to the employee everything which the employee would have been entitled to receive until the agreed conclusion of the agreement. The burden of proof lies on the party requesting compensation. Any amount which the employee saved, earned or intentionally failed to earn further to termination can be deducted in mitigation of the amount of the compensation. This reflects the general principle of damage mitigation."""
    
    if input_option == "Upload Text Files":
        st.experimental_rerun()
    else:
        st.text_area("Document 1", value=sample_text, height=200, key="text_0")
