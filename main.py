import streamlit as st
import re
from collections import Counter

def improved_search(query, doc_contents, threshold=0.1):
    """
    A more reliable search function that uses word frequency matching
    
    Parameters:
    - query: The search query string
    - doc_contents: Dictionary of document contents {doc_id: content}
    - threshold: Minimum similarity score (0.0-1.0)
    
    Returns:
    - List of search results
    """
    if not query or not doc_contents:
        return []
    
    # Normalize and tokenize query
    query = query.lower()
    query_words = re.findall(r'\b\w+\b', query)
    
    # Remove common words that might dilute search effectiveness
    stop_words = {'the', 'a', 'an', 'in', 'on', 'at', 'of', 'to', 'for', 'with', 'by', 'as', 
                 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had'}
    
    query_words = [w for w in query_words if w not in stop_words and len(w) > 2]
    
    if not query_words:
        return []
    
    # Create a counter for term frequency
    query_counter = Counter(query_words)
    
    results = []
    
    # Process each document
    for doc_id, content in doc_contents.items():
        # Split into paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) < 15:  # Skip very short paragraphs
                continue
            
            # Normalize and tokenize paragraph
            paragraph_lower = paragraph.lower()
            paragraph_words = re.findall(r'\b\w+\b', paragraph_lower)
            paragraph_words = [w for w in paragraph_words if w not in stop_words and len(w) > 2]
            
            if not paragraph_words:
                continue
                
            # Count matching words
            paragraph_counter = Counter(paragraph_words)
            matches = sum((query_counter & paragraph_counter).values())
            
            # Calculate similarity score - multiple approaches for robustness
            # 1. Word overlap ratio
            overlap_ratio = matches / len(query_words) if query_words else 0
            
            # 2. Check for phrase matches
            phrase_bonus = 0
            for i in range(len(query_words)-1):
                if i+1 < len(query_words):
                    phrase = f"{query_words[i]} {query_words[i+1]}"
                    if phrase in paragraph_lower:
                        phrase_bonus += 0.25  # Bonus for phrase matches
            
            # 3. Word density - matches relative to paragraph length
            density = matches / len(paragraph_words) if paragraph_words else 0
            
            # Combine scores
            similarity = (overlap_ratio * 0.5) + (phrase_bonus * 0.3) + (density * 0.2)
            
            if similarity >= threshold:
                # Create highlighted version of the paragraph
                highlighted = paragraph
                for word in set(query_words):
                    if len(word) > 2:  # Only highlight meaningful words
                        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
                        highlighted = pattern.sub(f"<mark>\\g<0></mark>", highlighted)
                
                results.append({
                    'doc_id': doc_id,
                    'paragraph_index': i,
                    'text': paragraph,
                    'highlighted_text': highlighted,
                    'similarity': round(similarity, 3),
                    'matches': matches
                })
    
    # Sort by similarity (highest first)
    return sorted(results, key=lambda x: x['similarity'], reverse=True)

# Example usage in app
def search_tab():
    st.header("Improved Smart Search")
    
    if not st.session_state.get('document_content', {}):
        st.warning("No documents have been uploaded. Please upload text files or load sample data first.")
        if st.button("Load Sample Data"):
            # Your sample data loading code here
            st.success("Sample data loaded successfully!")
            st.rerun()
        return
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_area("Enter your search query", 
                                   placeholder="Enter legal concept, argument, or issue to search for...")
    
    with col2:
        search_threshold = st.slider("Match Threshold", 
                                    min_value=0.05, max_value=0.5, value=0.1, step=0.05,
                                    help="Lower values return more results but may be less relevant")
        search_button = st.button("Search Documents", type="primary")
    
    if search_button and search_query:
        with st.spinner("Searching documents..."):
            doc_contents = st.session_state.get('document_content', {})
            search_results = improved_search(search_query, doc_contents, search_threshold)
            
            if search_results:
                st.subheader(f"Search Results ({len(search_results)} matches)")
                for i, result in enumerate(search_results):
                    with st.expander(f"Result {i+1} - {result['doc_id']} (Score: {result['similarity']})"):
                        st.markdown(f"**Document:** {result['doc_id']}")
                        st.markdown(f"**Matching words:** {result['matches']}")
                        st.markdown(result['highlighted_text'], unsafe_allow_html=True)
            else:
                st.info("No matching results found. Try lowering the threshold or using different search terms.")
                st.markdown("**Search tips:**")
                st.markdown("- Use specific legal terms rather than general words")
                st.markdown("- Try searching for phrases like 'contract breach' or 'force majeure'")
                st.markdown("- Search for specific article numbers mentioned in documents")
                st.markdown("- Look for evidence references like 'Exhibit' or 'evidence'")
