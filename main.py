import streamlit as st
import re
from pathlib import Path
import difflib
import base64
from io import StringIO
import json
from collections import Counter

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
if 'legal_concepts' not in st.session_state:
    st.session_state.legal_concepts = {
        "sporting succession": ["succession", "sporting rights", "club identity", "transfer of membership"],
        "force majeure": ["act of god", "unforeseen circumstances", "unavoidable accident", "superior force"],
        "pacta sunt servanda": ["agreement must be kept", "sanctity of contracts", "contract binding", "obligations fulfilled"],
        "contra proferentem": ["ambiguity interpreted against drafter", "unclear terms", "interpretation against author"],
        "lex sportiva": ["sports law", "sports regulations", "sporting rules", "sports jurisprudence"],
        # Add more legal concepts and their variations
    }
if 'citations' not in st.session_state:
    st.session_state.citations = {}
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

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

def enhanced_similarity(text1, text2):
    """Enhanced version of simple_similarity that gives more weight to key terms"""
    # Base similarity using Jaccard index
    base_sim = simple_similarity(text1, text2)
    
    # Look for exact phrase matches which would indicate higher similarity
    text1_lower = text1.lower()
    text2_lower = text2.lower()
    
    # Generate a list of phrases (3-5 words) from text1
    words1 = text1_lower.split()
    phrases1 = []
    for i in range(len(words1)):
        for j in range(3, 6):  # phrases of 3-5 words
            if i + j <= len(words1):
                phrases1.append(" ".join(words1[i:i+j]))
    
    # Count how many phrases from text1 appear in text2
    phrase_matches = sum(1 for phrase in phrases1 if phrase in text2_lower)
    
    # Boost factor based on phrase matches (max boost of 0.2)
    boost = min(0.2, phrase_matches * 0.02)
    
    # Check for key legal terms in both texts (boost if they share terms)
    legal_terms = ["force majeure", "contract", "breach", "damages", "liability", 
                  "arbitration", "tribunal", "evidence", "submissions", "legal", 
                  "clause", "article", "exhibit", "award", "proceedings"]
    
    shared_terms = sum(1 for term in legal_terms 
                      if term in text1_lower and term in text2_lower)
    
    legal_boost = min(0.2, shared_terms * 0.04)
    
    # Return enhanced similarity score (capped at 1.0)
    return min(1.0, base_sim + boost + legal_boost)

def expand_query_with_legal_concepts(query):
    """Expand query with related legal concepts"""
    expanded_terms = set([query.lower()])
    
    # Check if query contains any known legal concepts
    for concept, variations in st.session_state.legal_concepts.items():
        # If the concept or a variation is in the query, add all variations
        if concept.lower() in query.lower() or any(var.lower() in query.lower() for var in variations):
            expanded_terms.add(concept.lower())
            expanded_terms.update([var.lower() for var in variations])
    
    return " ".join(expanded_terms)

def search_documents(query, doc_contents, threshold=0.2, use_enhanced=True):
    """Search documents using either simple text similarity or enhanced similarity"""
    if not doc_contents or not query:
        return []
    
    # Expand query with related legal concepts
    expanded_query = expand_query_with_legal_concepts(query)
    
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
            if use_enhanced:
                similarity = enhanced_similarity(expanded_query, paragraph)
            else:
                similarity = simple_similarity(expanded_query, paragraph)
            
            # Check if it meets threshold
            if similarity >= threshold:
                # Find exact location in document
                start_pos = content.find(paragraph)
                # Get surrounding context (more text before and after)
                context_start = max(0, start_pos - 200)
                context_end = min(len(content), start_pos + len(paragraph) + 200)
                context = content[context_start:context_end]
                
                # Extract any citations or references
                citations = extract_citations(paragraph)
                
                # Calculate paragraph number for better reference
                para_number = len(re.findall(r'\n\s*\n', content[:start_pos])) + 1
                
                results.append({
                    'doc_id': doc_id,
                    'paragraph_index': i,
                    'paragraph_number': para_number,
                    'text': paragraph,
                    'similarity': round(similarity, 3),
                    'start_pos': start_pos,
                    'context': context,
                    'citations': citations
                })
    
    # Sort by similarity score (highest first)
    return sorted(results, key=lambda x: x['similarity'], reverse=True)

def extract_citations(text):
    """Extract citations and references from text"""
    citations = []
    
    # Pattern for exhibit references
    exhibit_pattern = r'(?i)(?:exhibit|document|evidence|proof)\s+([A-Z0-9-]+)'
    exhibits = re.finditer(exhibit_pattern, text)
    for match in exhibits:
        citations.append({
            'type': 'exhibit',
            'id': match.group(1),
            'text': match.group(0),
            'position': match.start()
        })
    
    # Pattern for article references
    article_pattern = r'(?i)(?:article|section|clause)\s+(\d+(?:\.\d+)*)'
    articles = re.finditer(article_pattern, text)
    for match in articles:
        citations.append({
            'type': 'article',
            'id': match.group(1),
            'text': match.group(0),
            'position': match.start()
        })
    
    # Pattern for case references
    case_pattern = r'(?i)(?:case|decision|award|ruling)\s+([A-Z0-9/.-]+)'
    cases = re.finditer(case_pattern, text)
    for match in cases:
        citations.append({
            'type': 'case',
            'id': match.group(1),
            'text': match.group(0),
            'position': match.start()
        })
    
    return citations

def sent_tokenize(text):
    """Simple sentence tokenization function using regex"""
    # Split by common sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s for s in sentences if s.strip()]

def compare_documents(doc1_id, doc2_id, focus_on_substance=True):
    """Compare two documents and highlight differences with focus on substantial changes"""
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
        doc1_sentences = sent_tokenize(para1)
        
        for j, para2 in enumerate(doc2_paras):
            para2_words = get_common_words(para2)
            doc2_sentences = sent_tokenize(para2)
            
            # Calculate similarity
            if focus_on_substance:
                similarity = enhanced_similarity(para1, para2)
            else:
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
                
                # Perform sentence-level comparison for more detailed analysis
                sentence_diffs = []
                for s1 in doc1_sentences:
                    best_match = None
                    best_score = 0
                    for s2 in doc2_sentences:
                        score = enhanced_similarity(s1, s2)
                        if score > best_score and score > 0.7:  # Only consider good matches
                            best_score = score
                            best_match = s2
                    
                    if best_match and best_score < 0.95:  # If there's a match but it's not identical
                        # Find the specific changes
                        sentence_diff = {
                            'doc1_sentence': s1,
                            'doc2_sentence': best_match,
                            'similarity': best_score,
                            'changes': highlight_word_differences(s1, best_match)
                        }
                        sentence_diffs.append(sentence_diff)
                
                # Extract key legal terms
                legal_terms1 = extract_legal_terms(para1)
                legal_terms2 = extract_legal_terms(para2)
                
                # Check for changes in numbers
                numbers1 = re.findall(r'\b\d+(?:\.\d+)?%?\b', para1)
                numbers2 = re.findall(r'\b\d+(?:\.\d+)?%?\b', para2)
                
                # Check for negation differences
                negations1 = re.findall(r'\b(?:not|never|no|cannot|isn\'t|aren\'t|wasn\'t|weren\'t)\b', para1.lower())
                negations2 = re.findall(r'\b(?:not|never|no|cannot|isn\'t|aren\'t|wasn\'t|weren\'t)\b', para2.lower())
                
                # Determine if substantial based on these factors
                different_legal_terms = set(legal_terms1) != set(legal_terms2)
                different_numbers = set(numbers1) != set(numbers2)
                different_negations = len(negations1) != len(negations2)
                
                is_substantial = different_legal_terms or different_numbers or different_negations
                
                # If not marked substantial yet, check the proportion of changed words
                if not is_substantial:
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
                    'is_substantial': is_substantial,
                    'sentence_diffs': sentence_diffs,
                    'different_legal_terms': different_legal_terms,
                    'different_numbers': different_numbers,
                    'different_negations': different_negations,
                    'unique_words_doc1': list(para1_words - para2_words),
                    'unique_words_doc2': list(para2_words - para1_words)
                })
    
    # Sort by substantialness first, then by similarity
    return sorted(results, key=lambda x: (not x['is_substantial'], x['similarity']))

def highlight_word_differences(text1, text2):
    """Highlight specific word differences between two texts"""
    words1 = text1.split()
    words2 = text2.split()
    
    matcher = difflib.SequenceMatcher(None, words1, words2)
    diffs = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            diffs.append({
                'type': 'replace',
                'text1': ' '.join(words1[i1:i2]),
                'text2': ' '.join(words2[j1:j2])
            })
        elif tag == 'delete':
            diffs.append({
                'type': 'delete',
                'text1': ' '.join(words1[i1:i2]),
                'text2': ''
            })
        elif tag == 'insert':
            diffs.append({
                'type': 'insert',
                'text1': '',
                'text2': ' '.join(words2[j1:j2])
            })
    
    return diffs

def extract_legal_terms(text):
    """Extract important legal terms from the text"""
    legal_terms = []
    
    # Common legal phrases in arbitration
    legal_phrases = [
        "breach of contract", "force majeure", "pacta sunt servanda", 
        "liquidated damages", "specific performance", "good faith",
        "arbitral tribunal", "applicable law", "jurisdiction", "liability",
        "termination", "damages", "compensation", "injunction", "remedy",
        "penalty clause", "counter-claim", "burden of proof", "evidence",
        "exhibit", "testimony", "witness", "expert", "award", "hearing",
        "sporting succession", "contra proferentem", "lex sportiva"
    ]
    
    for phrase in legal_phrases:
        if phrase.lower() in text.lower():
            legal_terms.append(phrase)
    
    return legal_terms

def create_summary(doc_id, doc_type="submission"):
    """Create a summary of arguments from a document with enhanced extraction"""
    if doc_id not in st.session_state.document_content:
        return None
    
    content = st.session_state.document_content[doc_id]
    
    # Extract arguments and evidence based on document type
    arguments = []
    counterarguments = []
    
    # Simple pattern matching for arguments (keeping this as in the original code)
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
                
                # Extract legal concepts
                legal_concepts = extract_legal_terms(argument)
                
                # Find counter arguments (looking for opponent's position being refuted)
                counter_patterns = [
                    r'(?i)(?:However|Nevertheless|Conversely|In contrast),\s+([^.]+\.)',
                    r'(?i)(?:disagrees?|disputes?|counters?|rebuts?|refutes?|denies?)\s+([^.]+\.)',
                    r'(?i)(?:contrary to|in opposition to|despite|notwithstanding)\s+([^.]+\.)'
                ]
                
                counters = []
                for c_pattern in counter_patterns:
                    c_matches = re.finditer(c_pattern, context)
                    for c_match in c_matches:
                        counters.append(c_match.group(1).strip())
                
                # Get the paragraph number
                paragraph_num = content[:match.start()].count('\n\n') + 1
                
                arguments.append({
                    'text': argument,
                    'position': match.start(),
                    'evidence': evidence,
                    'context': context,
                    'legal_concepts': legal_concepts,
                    'counterarguments': counters,
                    'paragraph': paragraph_num
                })
        
        # Look for explicit counter-arguments
        counter_arg_patterns = [
            r'(?i)(?:disagrees?|disputes?|counters?|rebuts?|refutes?|denies?)\s+([^.]+\.)',
            r'(?i)(?:Unlike|Contrary to) what.{1,50}?(?:claims?|asserts?|argues?|contends?),\s+([^.]+\.)',
            r'(?i)(?:rejects?|dismisses?) the (?:claim|argument|contention) that\s+([^.]+\.)'
        ]
        
        for pattern in counter_arg_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                counterarg = match.group(1).strip()
                context = content[max(0, match.start() - 100):min(len(content), match.end() + 100)]
                
                # Get supporting evidence
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
                
                # Get paragraph number
                paragraph_num = content[:match.start()].count('\n\n') + 1
                
                counterarguments.append({
                    'text': counterarg,
                    'position': match.start(),
                    'evidence': evidence,
                    'context': context,
                    'paragraph': paragraph_num
                })
    
    # Extract quoted content
    quotes = extract_quotes(content)
    
    # Extract key dates for timeline
    dates = extract_dates(content)
    
    # Create enhanced summary structure
    return {
        'doc_id': doc_id,
        'doc_type': doc_type,
        'arguments': arguments,
        'argument_count': len(arguments),
        'counterarguments': counterarguments,
        'counterargument_count': len(counterarguments),
        'quotes': quotes,
        'key_dates': dates,
        'legal_concepts': list(set([concept for arg in arguments for concept in arg.get('legal_concepts', [])]))
    }

def extract_quotes(text):
    """Extract quoted content from text"""
    # Pattern for text in quotation marks
    quotes = []
    
    # Look for text in double quotes
    quote_pattern = r'"([^"]+)"'
    matches = re.finditer(quote_pattern, text)
    for match in matches:
        if len(match.group(1)) > 10:  # Skip very short quotes
            quotes.append({
                'text': match.group(1),
                'position': match.start(),
                'context': text[max(0, match.start() - 50):min(len(text), match.end() + 50)]
            })
    
    return quotes

def extract_dates(text):
    """Extract dates from text for timeline creation"""
    # Pattern for dates in various formats
    date_patterns = [
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b',
        r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        r'\b\d{4}-\d{2}-\d{2}\b'
    ]
    
    dates = []
    for pattern in date_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            # Get sentence containing the date for context
            sentence_start = text.rfind('.', 0, match.start()) + 1
            if sentence_start == 0:  # If no period found before, start from beginning
                sentence_start = max(0, match.start() - 100)
            sentence_end = text.find('.', match.end())
            if sentence_end == -1:  # If no period found after, end at text end
                sentence_end = min(len(text), match.end() + 100)
            
            context = text[sentence_start:sentence_end].strip()
            
            dates.append({
                'date': match.group(0),
                'position': match.start(),
                'context': context
            })
    
    return sorted(dates, key=lambda x: x['position'])

def find_counterarguments(argument, doc_contents):
    """Find potential counterarguments to the given argument"""
    counters = []
    
    # Use similarity search to find relevant paragraphs that might contain counterarguments
    for doc_id, content in doc_contents.items():
        paragraphs = re.split(r'\n\s*\n', content)
        
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph.strip()) < 20:
                continue
            
            # Check if paragraph is semantically similar to the argument
            similarity = enhanced_similarity(argument, paragraph)
            
            if similarity > 0.4:  # Reasonably similar
                # Check if it contains counter-indicators
                counter_indicators = [
                    r'\b(?:however|nevertheless|conversely|in contrast|on the contrary)\b',
                    r'\b(?:disagree|dispute|counter|rebut|refute|deny)\w*\b',
                    r'\b(?:contrary to|in opposition to|despite|notwithstanding)\b',
                    r'\b(?:reject|dismiss)\w*\b',
                    r'\b(?:unlike|opposed to)\b'
                ]
                
                is_counter = False
                for pattern in counter_indicators:
                    if re.search(pattern, paragraph, re.IGNORECASE):
                        is_counter = True
                        break
                
                if is_counter:
                    counters.append({
                        'doc_id': doc_id,
                        'paragraph_index': i,
                        'text': paragraph,
                        'similarity': similarity
                    })
    
    return sorted(counters, key=lambda x: x['similarity'], reverse=True)

def create_downloadable_report(search_results=None, compare_results=None, summary=None):
    """Create a downloadable report with the results"""
    report = []
    
    if search_results:
        report.append("# SEARCH RESULTS\n")
        for i, result in enumerate(search_results, 1):
            report.append(f"## Result {i} (Similarity: {result['similarity']})\n")
            report.append(f"Document: {result['doc_id']}\n")
            report.append(f"Paragraph Number: {result.get('paragraph_number', 'N/A')}\n")
            report.append(f"Text: {result['text']}\n")
            
            if 'citations' in result and result['citations']:
                report.append("\nCitations:\n")
                for citation in result['citations']:
                    report.append(f"- {citation['type'].capitalize()}: {citation['id']} ({citation['text']})\n")
            
            report.append("\n")
    
    if compare_results:
        report.append("# DOCUMENT COMPARISON\n")
        for i, result in enumerate(compare_results, 1):
            report.append(f"## Difference {i} (Similarity: {result['similarity']:.3f})\n")
            report.append(f"Document 1: {result['doc1_id']}\n")
            report.append(f"Document 2: {result['doc2_id']}\n")
            report.append(f"Is substantial difference: {'Yes' if result['is_substantial'] else 'No'}\n")
            
            if result['is_substantial']:
                if result.get('different_legal_terms', False):
                    report.append("Contains differences in legal terminology\n")
                if result.get('different_numbers', False):
                    report.append("Contains differences in numbers or quantities\n")
                if result.get('different_negations', False):
                    report.append("Contains differences in negations (not, never, etc.)\n")
                
                report.append("\nUnique words in Document 1:\n")
                for word in result.get('unique_words_doc1', [])[:10]:  # Limit to first 10 for brevity
                    report.append(f"- {word}\n")
                
                report.append("\nUnique words in Document 2:\n")
                for word in result.get('unique_words_doc2', [])[:10]:
                    report.append(f"- {word}\n")
            
            report.append(f"\nDocument 1 text: {result['doc1_text']}\n")
            report.append(f"Document 2 text: {result['doc2_text']}\n\n")
            
            if 'sentence_diffs' in result and result['sentence_diffs']:
                report.append("Sentence-level differences:\n")
                for diff in result['sentence_diffs']:
                    report.append(f"- Doc1: {diff['doc1_sentence']}\n")
                    report.append(f"- Doc2: {diff['doc2_sentence']}\n\n")
    
    if summary:
        report.append("# ARGUMENT SUMMARY\n")
        report.append(f"Document: {summary['doc_id']}\n")
        report.append(f"Document type: {summary['doc_type']}\n")
        report.append(f"Total arguments found: {summary['argument_count']}\n")
        report.append(f"Total counterarguments found: {summary['counterargument_count']}\n\n")
        
        if summary.get('legal_concepts', []):
            report.append("## Legal Concepts Identified\n")
            for concept in summary['legal_concepts']:
                report.append(f"- {concept}\n")
            report.append("\n")
        
        report.append("## Arguments\n")
        for i, arg in enumerate(summary['arguments'], 1):
            report.append(f"### Argument {i}\n")
            report.append(f"Text: {arg['text']}\n")
            report.append(f"Paragraph: {arg.get('paragraph', 'N/A')}\n")
            
            if arg.get('legal_concepts', []):
                report.append("Legal concepts:\n")
                for concept in arg['legal_concepts']:
                    report.append(f"- {concept}\n")
            
            if arg['evidence']:
                report.append("Evidence:\n")
                for ev in arg['evidence']:
                    report.append(f"- {ev}\n")
            
            if arg.get('counterarguments', []):
                report.append("Related counterarguments:\n")
                for counter in arg['counterarguments']:
                    report.append(f"- {counter}\n")
            
            report.append("\n")
        
        if summary.get('counterarguments', []):
            report.append("## Explicit Counterarguments\n")
            for i, arg in enumerate(summary['counterarguments'], 1):
                report.append(f"### Counterargument {i}\n")
                report.append(f"Text: {arg['text']}\n")
                report.append(f"Paragraph: {arg.get('paragraph', 'N/A')}\n")
                
                if arg['evidence']:
                    report.append("Evidence:\n")
                    for ev in arg['evidence']:
                        report.append(f"- {ev}\n")
                
                report.append("\n")
        
        if summary.get('quotes', []):
            report.append("## Important Quotes\n")
            for i, quote in enumerate(summary['quotes'], 1):
                report.append(f"### Quote {i}\n")
                report.append(f"\"{quote['text']}\"\n\n")
        
        if summary.get('key_dates', []):
            report.append("## Timeline of Key Dates\n")
            for i, date in enumerate(summary['key_dates'], 1):
                report.append(f"### {date['date']}\n")
                report.append(f"Context: {date['context']}\n\n")
    
    return "\n".join(report)

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
    
    # Recent searches
    if st.session_state.search_history:
        st.subheader("Recent Searches")
        for query in st.session_state.search_history[-5:]:  # Show last 5 searches
            if st.button(f"🔍 {query[:30]}...", key=f"history_{query[:10]}"):
                # This will set the search query and trigger a search
                st.session_state.search_query = query
                st.rerun()

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
        
        sample3 = """
        Sporting Succession Case Brief
        
        This document addresses the concept of sporting succession in the context of club reorganizations.
        
        In the matter of FC United vs. Soccer Federation, the tribunal considered whether New FC could be considered the sporting successor of Old FC, which had gone bankrupt.
        
        The club argues that it maintained sporting continuity despite legal reorganization. The primary elements considered were:
        
        1. Continuation of the same essential identity (name, colors, emblem, fanbase)
        2. Playing in the same stadium
        3. Retention of key players and technical staff
        4. Recognition by supporters as the same club
        
        The tribunal noted in its decision (Case 2018/A/123) that "sporting succession occurs when a new entity continues the sporting legacy of a previous entity, even if there is a break in legal continuity."
        
        The opposing party contested this view, submitting that legal identity is paramount and that sporting rights cannot be transferred outside the federation's regulations.
        
        According to sporting jurisprudence, the concept of sporting succession has been recognized in multiple cases where clubs maintained their sporting identity despite changes in legal structure. This principle acknowledges that clubs exist as sporting entities beyond their mere legal form.
        
        The panel ultimately concluded that sporting succession had occurred and that New FC was entitled to claim the sporting history and records of Old FC, though not automatically entitled to assume all competitive rights without federation approval.
        """
        
        st.session_state.documents = {
            "Claimant_Submission.txt": None, 
            "Respondent_Reply.txt": None,
            "Sporting_Succession_Brief.txt": None
        }
        st.session_state.document_content = {
            "Claimant_Submission.txt": sample1,
            "Respondent_Reply.txt": sample2,
            "Sporting_Succession_Brief.txt": sample3
        }
        st.success("Sample data loaded successfully!")
        st.rerun()

# Main area tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Smart Search", "Document Compare", "Argument Summary", "Document Viewer", "Legal Concepts"])

# Tab 1: Smart Search (keeping this as in the original code)
with tab1:
    st.header("Smart Search")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_area("Enter your search query", 
                                    placeholder="Enter legal concept, argument, or issue to search for...",
                                    value=st.session_state.get('search_query', ''))
    
    with col2:
        search_threshold = st.slider("Similarity Threshold", 
                                    min_value=0.1, max_value=0.9, value=0.2, step=0.05,
                                    help="Lower values return more results but may be less relevant")
        use_enhanced = st.checkbox("Use enhanced search", value=True, 
                                  help="Use advanced techniques for better understanding of legal concepts")
        search_button = st.button("Search Documents", type="primary")
    
    if search_button and search_query:
        # Add to search history
        if search_query not in st.session_state.search_history:
            st.session_state.search_history.append(search_query)
        
        with st.spinner("Searching documents..."):
            search_results = search_documents(search_query, st.session_state.document_content, 
                                             search_threshold, use_enhanced)
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
                st.markdown(f"**Paragraph {result.get('paragraph_number', result['paragraph_index'])}:**")
                
                # Highlight the matching text
                highlighted_text = result['text']
                for term in search_query.lower().split():
                    if len(term) > 3:  # Only highlight meaningful terms
                        pattern = re.compile(re.escape(term), re.IGNORECASE)
                        highlighted_text = pattern.sub(f"<mark>{term}</mark>", highlighted_text)
                
                st.markdown(highlighted_text, unsafe_allow_html=True)
                
                # Show citations and references if any
                if 'citations' in result and result['citations']:
                    st.markdown("**References:**")
                    for citation in result['citations']:
                        st.markdown(f"- {citation['type'].capitalize()}: {citation['id']} ({citation['text']})")
                
                # Show context button
                if st.button(f"Show Context", key=f"context_{i}"):
                    st.markdown("**Context:**")
                    st.markdown(result['context'])
                
                # Button to find counterarguments
                if st.button(f"Find Counterarguments", key=f"counter_{i}"):
                    with st.spinner("Searching for counterarguments..."):
                        counters = find_counterarguments(result['text'], st.session_state.document_content)
                        if counters:
                            st.markdown("**Potential Counterarguments:**")
                            for j, counter in enumerate(counters[:3]):  # Show top 3
                                st.markdown(f"**From {counter['doc_id']}:**")
                                st.markdown(counter['text'])
                                st.markdown("---")
                        else:
                            st.info("No clear counterarguments found.")
        
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
        
        # Enhanced comparison options
        comparison_type = st.radio(
            "Comparison Focus",
            ["Substantial Differences", "All Differences", "Legal Terms", "Numbers & Dates"],
            horizontal=True
        )
        
        compare_button = st.button("Compare Documents", type="primary", key="compare_button")
        
        if compare_button:
            with st.spinner("Comparing documents..."):
                # Use enhanced comparison for substantial differences
                focus_on_substance = comparison_type in ["Substantial Differences", "Legal Terms"]
                compare_results = compare_documents(doc1_id, doc2_id, focus_on_substance)
                
                # Filter results based on comparison type
                if comparison_type == "Legal Terms":
                    compare_results = [r for r in compare_results if r.get('different_legal_terms', False)]
                elif comparison_type == "Numbers & Dates":
                    compare_results = [r for r in compare_results if r.get('different_numbers', False)]
                
                st.session_state.compare_results = compare_results
        
        if st.session_state.compare_results:
            st.subheader(f"Comparison Results ({len(st.session_state.compare_results)} differences)")
            
            # Filter options
            if comparison_type == "All Differences":
                show_substantial_only = st.checkbox("Show substantial differences only", value=False)
                
                # Filter results if needed
                if show_substantial_only:
                    filtered_results = [r for r in st.session_state.compare_results if r.get('is_substantial', False)]
                else:
                    filtered_results = st.session_state.compare_results
            else:
                filtered_results = st.session_state.compare_results
            
            if not filtered_results:
                st.info("No matching differences found based on your criteria.")
            
            for i, result in enumerate(filtered_results):
                # Enhanced expander title with more information
                diff_type = "Substantial" if result.get('is_substantial', False) else "Minor"
                diff_details = []
                
                if result.get('different_legal_terms', False):
                    diff_details.append("Legal Terms")
                if result.get('different_numbers', False):
                    diff_details.append("Numbers")
                if result.get('different_negations', False):
                    diff_details.append("Negations")
                
                diff_info = f"({', '.join(diff_details)})" if diff_details else ""
                
                with st.expander(f"Difference {i+1} - {diff_type} {diff_info} (Similarity: {result['similarity']:.2f})"):
                    # Two-column layout for comparison
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Document: {result['doc1_id']}**")
                        st.markdown(result['doc1_formatted'], unsafe_allow_html=True)
                        
                        # Show unique terms
                        if 'unique_words_doc1' in result and result['unique_words_doc1']:
                            st.markdown("**Unique Terms:**")
                            st.write(", ".join(result['unique_words_doc1'][:10]))
                    
                    with col2:
                        st.markdown(f"**Document: {result['doc2_id']}**")
                        st.markdown(result['doc2_formatted'], unsafe_allow_html=True)
                        
                        # Show unique terms
                        if 'unique_words_doc2' in result and result['unique_words_doc2']:
                            st.markdown("**Unique Terms:**")
                            st.write(", ".join(result['unique_words_doc2'][:10]))
                    
                    # Sentence-level differences (if available)
                    if 'sentence_diffs' in result and result['sentence_diffs']:
                        st.markdown("**Sentence-Level Changes:**")
                        for diff in result['sentence_diffs']:
                            st.markdown(f"**Similarity: {diff['similarity']:.2f}**")
                            st.markdown(f"**Original:** {diff['doc1_sentence']}")
                            st.markdown(f"**Changed:** {diff['doc2_sentence']}")
                            
                            if 'changes' in diff:
                                st.markdown("**Specific Changes:**")
                                for change in diff['changes']:
                                    if change['type'] == 'replace':
                                        st.markdown(f"- Changed: '{change['text1']}' → '{change['text2']}'")
                                    elif change['type'] == 'delete':
                                        st.markdown(f"- Removed: '{change['text1']}'")
                                    elif change['type'] == 'insert':
                                        st.markdown(f"- Added: '{change['text2']}'")
                            
                            st.markdown("---")
            
            # Download results button
            if st.button("Download Comparison Results", key="download_compare"):
                report = create_downloadable_report(compare_results=filtered_results)
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
                                   options=["submission", "exhibit", "brief"],
                                   key="summary_type")
            summarize_button = st.button("Generate Summary", type="primary", key="summarize_button")
        
        if summarize_button:
            with st.spinner("Generating argument summary..."):
                summary = create_summary(doc_id, doc_type)
                st.session_state.summary = summary
        
        if st.session_state.summary:
            st.subheader(f"Argument Summary")
            
            # Display overview section
            with st.expander("Summary Overview", expanded=True):
                st.markdown(f"**Document:** {st.session_state.summary['doc_id']}")
                st.markdown(f"**Document Type:** {st.session_state.summary['doc_type']}")
                st.markdown(f"**Arguments Found:** {st.session_state.summary['argument_count']}")
                st.markdown(f"**Counterarguments Found:** {st.session_state.summary['counterargument_count']}")
                
                if st.session_state.summary.get('legal_concepts', []):
                    st.markdown("**Legal Concepts Identified:**")
                    st.write(", ".join(st.session_state.summary['legal_concepts']))
            
            # Tabs for different summary sections
            summary_tabs = st.tabs(["Arguments", "Counterarguments", "Quotes", "Timeline"])
            
            # Arguments tab
            with summary_tabs[0]:
                if st.session_state.summary['argument_count'] == 0:
                    st.info("No clear arguments found in this document. This could be because the document doesn't contain typical argument patterns or uses different phrasing.")
                    st.write("You can try:")
                    st.write("1. Selecting a different document type")
                    st.write("2. Using the Smart Search tab to search for specific legal terms")
                
                for i, arg in enumerate(st.session_state.summary['arguments']):
                    with st.expander(f"Argument {i+1}"):
                        st.markdown(f"**Text:** {arg['text']}")
                        
                        # Display paragraph reference
                        if 'paragraph' in arg:
                            st.markdown(f"**Location:** Paragraph {arg['paragraph']}")
                        
                        # Display legal concepts
                        if 'legal_concepts' in arg and arg['legal_concepts']:
                            st.markdown("**Legal concepts:**")
                            st.write(", ".join(arg['legal_concepts']))
                        
                        # Display evidence
                        if arg['evidence']:
                            st.markdown("**Evidence cited:**")
                            for ev in arg['evidence']:
                                st.markdown(f"- {ev}")
                        
                        # Display counterarguments
                        if 'counterarguments' in arg and arg['counterarguments']:
                            st.markdown("**Related counterarguments:**")
                            for counter in arg['counterarguments']:
                                st.markdown(f"- {counter}")
                        
                        # Display context
                        st.markdown("**Context:**")
                        st.text(arg['context'])
                        
                        # Find similar arguments button
                        if st.button(f"Find Similar Arguments", key=f"similar_{i}"):
                            with st.spinner("Searching for similar arguments..."):
                                similar = search_documents(arg['text'], 
                                                        {k: v for k, v in st.session_state.document_content.items() 
                                                        if k != doc_id},  # Exclude current document
                                                        threshold=0.3, 
                                                        use_enhanced=True)
                                if similar:
                                    st.markdown("**Similar Arguments in Other Documents:**")
                                    for j, sim in enumerate(similar[:3]):  # Show top 3
                                        st.markdown(f"**From {sim['doc_id']}:**")
                                        st.markdown(sim['text'])
                                        st.markdown("---")
                                else:
                                    st.info("No similar arguments found in other documents.")
            
            # Counterarguments tab
            with summary_tabs[1]:
                if st.session_state.summary['counterargument_count'] == 0:
                    st.info("No explicit counterarguments found in this document.")
                
                for i, arg in enumerate(st.session_state.summary['counterarguments']):
                    with st.expander(f"Counterargument {i+1}"):
                        st.markdown(f"**Text:** {arg['text']}")
                        
                        # Display paragraph reference
                        if 'paragraph' in arg:
                            st.markdown(f"**Location:** Paragraph {arg['paragraph']}")
                        
                        # Display evidence
                        if arg['evidence']:
                            st.markdown("**Evidence cited:**")
                            for ev in arg['evidence']:
                                st.markdown(f"- {ev}")
                        
                        # Display context
                        st.markdown("**Context:**")
                        st.text(arg['context'])
            
            # Quotes tab
            with summary_tabs[2]:
                if not st.session_state.summary.get('quotes', []):
                    st.info("No significant quotes found in this document.")
                
                for i, quote in enumerate(st.session_state.summary.get('quotes', [])):
                    with st.expander(f"Quote {i+1}"):
                        st.markdown(f"**Text:** \"{quote['text']}\"")
                        st.markdown("**Context:**")
                        st.text(quote['context'])
            
            # Timeline tab
            with summary_tabs[3]:
                if not st.session_state.summary.get('key_dates', []):
                    st.info("No key dates found in this document.")
                else:
                    # Create a timeline view
                    for i, date in enumerate(st.session_state.summary['key_dates']):
                        st.markdown(f"**{date['date']}**")
                        st.markdown(f"*Context:* {date['context']}")
                        st.markdown("---")
            
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
            
            # Enhanced document viewer options
            viewer_tabs = st.tabs(["Plain Text", "Structured View", "Citations"])
            
            # Plain text view
            with viewer_tabs[0]:
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
            
            # Structured view
            with viewer_tabs[1]:
                # Split document into paragraphs and display with numbers
                paragraphs = re.split(r'\n\s*\n', content)
                paragraphs = [p for p in paragraphs if len(p.strip()) > 20]
                
                for i, para in enumerate(paragraphs):
                    with st.expander(f"Paragraph {i+1}"):
                        st.write(para)
                        
                        # Extract citations for this paragraph
                        citations = extract_citations(para)
                        if citations:
                            st.markdown("**Citations:**")
                            for citation in citations:
                                st.markdown(f"- {citation['type'].capitalize()}: {citation['id']} ({citation['text']})")
            
            # Citations view
            with viewer_tabs[2]:
                # Extract all citations from the document
                citations = []
                paragraphs = re.split(r'\n\s*\n', content)
                for i, para in enumerate(paragraphs):
                    para_citations = extract_citations(para)
                    for citation in para_citations:
                        citation['paragraph'] = i + 1
                        citations.append(citation)
                
                if not citations:
                    st.info("No citations found in this document.")
                else:
                    # Group by citation type
                    citation_types = set(c['type'] for c in citations)
                    
                    for c_type in citation_types:
                        with st.expander(f"{c_type.capitalize()} References", expanded=True):
                            type_citations = [c for c in citations if c['type'] == c_type]
                            unique_ids = set(c['id'] for c in type_citations)
                            
                            for c_id in unique_ids:
                                st.markdown(f"**{c_id}**")
                                id_citations = [c for c in type_citations if c['id'] == c_id]
                                for citation in id_citations:
                                    st.markdown(f"- Paragraph {citation['paragraph']}: \"{citation['text']}\"")

# Tab 5: Legal Concepts (New Tab)
with tab5:
    st.header("Legal Concepts")
    
    # Two-column layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Manage Legal Concepts")
        
        # Display existing concepts
        existing_concepts = list(st.session_state.legal_concepts.keys())
        selected_concept = st.selectbox("Select a concept", options=[''] + existing_concepts)
        
        if selected_concept:
            variations = st.session_state.legal_concepts[selected_concept]
            
            # Display and edit variations
            st.write("**Variations:**")
            variation_text = "\n".join(variations)
            new_variations = st.text_area("Edit variations (one per line)", value=variation_text)
            
            if st.button("Update Variations"):
                st.session_state.legal_concepts[selected_concept] = [v.strip() for v in new_variations.split('\n') if v.strip()]
                st.success(f"Updated variations for '{selected_concept}'")
                st.rerun()
        
        # Add new concept
        st.write("**Add New Concept:**")
        new_concept = st.text_input("Concept name")
        new_concept_variations = st.text_area("Variations (one per line)")
        
        if st.button("Add Concept") and new_concept:
            variations_list = [v.strip() for v in new_concept_variations.split('\n') if v.strip()]
            st.session_state.legal_concepts[new_concept] = variations_list
            st.success(f"Added new concept: '{new_concept}'")
            st.rerun()
    
    with col2:
        st.subheader("Search by Concept")
        
        # Allow searching by concept
        concept_search = st.selectbox(
            "Select a legal concept to search for",
            options=[''] + list(st.session_state.legal_concepts.keys())
        )
        
        if concept_search and st.button("Search", key="concept_search"):
            # Create search query from concept and variations
            query = concept_search + " " + " ".join(st.session_state.legal_concepts[concept_search])
            
            with st.spinner("Searching documents..."):
                search_results = search_documents(query, st.session_state.document_content, 
                                             threshold=0.2, use_enhanced=True)
                
                if search_results:
                    st.success(f"Found {len(search_results)} matches for '{concept_search}'")
                    
                    for i, result in enumerate(search_results[:5]):  # Show top 5
                        with st.expander(f"Result {i+1} - {result['doc_id']}"):
                            st.markdown(f"**From document:** {result['doc_id']}")
                            st.markdown(f"**Paragraph {result.get('paragraph_number', result['paragraph_index'])}:**")
                            st.markdown(result['text'])
                            
                            # Show a "View Full" button that sets the search query
                            if st.button(f"Expand in Smart Search", key=f"expand_{i}"):
                                st.session_state.search_query = query
                                st.rerun()
                else:
                    st.info(f"No matches found for '{concept_search}'")
        
        # Display all concepts and variations
        st.subheader("All Legal Concepts")
        
        for concept, variations in st.session_state.legal_concepts.items():
            with st.expander(concept):
                st.write("**Variations:**")
                for var in variations:
                    st.write(f"- {var}")

# Footer
st.markdown("---")
st.markdown("**Sports Arbitration Smart Search Tool** - Developed to assist legal professionals in analyzing arbitration documents")
