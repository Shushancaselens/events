import streamlit as st
import pandas as pd
import re
from collections import Counter
import base64
from datetime import datetime

# Page configuration
st.set_page_config(page_title="Sports Arbitration Search", layout="wide")

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = []

# Helper functions
def highlight_text(text, search_terms):
    """Highlight search terms in text"""
    highlighted = text
    for term in search_terms:
        if term.strip():
            pattern = re.compile(f'({re.escape(term)})', re.IGNORECASE)
            highlighted = pattern.sub(r'**\1**', highlighted)
    return highlighted

def simple_search(text, search_terms):
    """Search for terms in text and return score"""
    score = 0
    text_lower = text.lower()
    for term in search_terms:
        term_lower = term.lower().strip()
        if term_lower and term_lower in text_lower:
            score += text_lower.count(term_lower)
    return score

def search_documents(search_query, doc_filters=None):
    """Search across all documents with optional filters"""
    if not search_query.strip():
        return []
    
    # Prepare search terms
    search_terms = [term.strip() for term in search_query.split() if term.strip()]
    
    results = []
    for i, doc in enumerate(st.session_state.documents):
        # Apply filters if any
        if doc_filters:
            if 'type' in doc_filters and doc_filters['type'] != 'All' and doc['type'] != doc_filters['type']:
                continue
            if 'party' in doc_filters and doc_filters['party'] != 'All' and doc['party'] != doc_filters['party']:
                continue
        
        # Search in paragraphs for more precise results
        paragraphs = doc['text'].split('\n\n')
        for j, para in enumerate(paragraphs):
            if para.strip():  # Skip empty paragraphs
                score = simple_search(para, search_terms)
                
                if score > 0:
                    # Only include results with matches
                    highlighted_text = highlight_text(para, search_terms)
                    
                    results.append({
                        'doc_id': i,
                        'para_id': j,
                        'filename': doc['filename'],
                        'type': doc['type'],
                        'party': doc['party'],
                        'score': score,
                        'text': para,
                        'highlighted_text': highlighted_text
                    })
    
    # Sort by score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def extract_references(text):
    """Extract exhibit references from text"""
    # Pattern for exhibit references like "Exhibit X" or "Exhibit No. X"
    exhibit_pattern = re.compile(r'exhibit\s+(?:no\.\s*)?(\d+|\w+)', re.IGNORECASE)
    matches = exhibit_pattern.findall(text)
    return matches

def export_results(results, format_type="markdown"):
    """Export search results to file"""
    if format_type == "markdown":
        output = "# Search Results\n\n"
        for i, result in enumerate(results):
            output += f"## Result {i+1}: {result['filename']}\n"
            output += f"**Document Type:** {result['type']}\n"
            output += f"**Party:** {result['party']}\n\n"
            output += f"{result['highlighted_text']}\n\n"
            output += "---\n\n"
        return output
    
    elif format_type == "csv":
        output = "Result,Filename,Type,Party,Text\n"
        for i, result in enumerate(results):
            # Clean the text for CSV
            clean_text = result['text'].replace('"', '""')
            output += f"{i+1},\"{result['filename']}\",\"{result['type']}\",\"{result['party']}\",\"{clean_text}\"\n"
        return output
    
    return None

# Main application UI
st.title("Sports Arbitration Document Search")

# Main tabs
tab1, tab2, tab3 = st.tabs(["Document Upload", "Search", "About"])

with tab1:
    st.header("Document Upload")
    
    # Sample documents for quick testing
    with st.expander("Load Sample Documents"):
        if st.button("Load Sample Documents"):
            sample_docs = [
                {
                    'filename': 'appellant_submission.txt',
                    'type': 'Submission',
                    'party': 'Club (Appellant)',
                    'text': """SUBMISSION ON BEHALF OF ANORTHOSIS FAMAGUSTA FC
                    
1. The Club terminated the Agreement with Coach Middendorp with just cause due to poor sporting results.

2. The team's performance was below acceptable standards, particularly in European matches.

3. The Club exercised its right under Article 14(d) of the Agreement which states:
"The present contract is terminated when unilaterally for a very serious reason. For the purpose of this contract a 'very serious reason' means any serious breach and/or serious default of the terms and/or conditions of the contract."

4. The Coach failed to follow the regulations concerning technical, sporting and disciplinary matters as specified in Article 2 of the General Conditions.

5. The poor performance led to the disqualification of the Club from European competition, causing significant financial damage.

6. The Coach has already received compensation of EUR 50,000 for only 1.5 months of service.

7. The Coach did not take all reasonable steps to find suitable employment after termination.

8. For these reasons, the Club requests the Panel to set aside the FIFA PSC Decision and reject any claims for further compensation."""
                },
                {
                    'filename': 'respondent_submission.txt',
                    'type': 'Submission',
                    'party': 'Coach (Respondent)',
                    'text': """SUBMISSION ON BEHALF OF ERNST MIDDENDORP
                    
1. The Club terminated my employment contract without just cause on 25 July 2009.

2. According to established CAS jurisprudence, poor sporting results cannot constitute just cause for termination of a coaching contract (see CAS 2011/A/2596).

3. I had no knowledge of the "Internal Regulations" to which the Club refers, and I did not breach any terms of the Agreement.

4. The Agreement was valid from 1 June 2009 until 30 May 2010, entitling me to a total salary of EUR 200,000.

5. After termination, I found employment with Maritzburg United FC and earned ZAR 418,761 (equivalent to EUR 43,963.27) for the period until 31 May 2010.

6. Swiss law (Article 337c of the Code of Obligations) provides that in case of termination without just cause of an employment contract of set duration, the employer must pay the employee what they would have received until the conclusion of the agreement.

7. I am therefore entitled to compensation of EUR 156,036 (EUR 200,000 minus EUR 43,963.27), as correctly determined by the FIFA PSC.

8. I request the Panel to uphold the FIFA PSC Decision and dismiss the appeal."""
                },
                {
                    'filename': 'employment_contract.txt',
                    'type': 'Contract',
                    'party': 'Both Parties',
                    'text': """EMPLOYMENT CONTRACT EXCERPTS
                    
General Conditions:

(1) The Employer has employed and by this contract employs the Coach for the purpose of rendering his services as a fulltime football Head-Coach to the Employer subject to the terms and conditions detailed herein.

(2) The Coach at all times during his employment shall be obliged to follow the Regulations concerning technical, sporting and disciplinary matters as the same are from time to time required and/or specified by the Employer.

(11) The present contract may be terminated and/or suspended (as the case may be) for one of the following reasons:
[...]
b) In the case of a breach or default of very serious terms of this contract by the Coach.

(14) The present contract is terminated when:
[...]
d) unilaterally for a very serious reason. For the purpose of this contract a "very serious reason" means any serious breach and/or serious default of the terms and/or conditions of the contract, the disciplinary rules of the employer and/or the CFA and the constant wrongful behavior and/or conduct by any one Parties."""
                },
                {
                    'filename': 'cas_jurisprudence.txt',
                    'type': 'Exhibit',
                    'party': 'Coach (Respondent)',
                    'text': """CAS 2011/A/2596 EXCERPT
                    
"1. Notwithstanding that the FIFA Regulations on the Status and Transfer of Players (RSTP) is not directly applicable to coaches, the specific provisions of Articles 22 and 23 RSTP are directly applicable to coaches, thanks to the direct and explicit extension of the provisions to include matters relating to coaches. Prima facie, the FIFA Players Status Committee (PSC) is thus competent to deal with employment-related disputes between a club or an association and a coach of an international dimension, unless the exception clause mentioned in Article 22 RSTP is applicable. This exception clause will be applicable only on condition that reference has specifically been made in the contract to a national independent arbitration tribunal.

2. The absence of sporting results cannot, as a general rule, constitute per se a reason to terminate a contractual relationship with just cause.

3. Article 17 RSTP is not applicable in a dispute concerning a coach (as opposed to a player). Article 1 RSTP ("Scope") provides that the Regulations concern "players", not coaches. Moreover, the FIFA Statutes no longer contain the provision which appeared in Article 33.4 of their 2001 version, which equated coaches with players.

4. Article 337c of the Swiss Code of Obligations (CO) provides that in case of termination without just cause of an employment contract of set duration, the employer must, in principle, pay to the employee everything which the employee would have been entitled to receive until the agreed conclusion of the agreement. The burden of proof lies on the party requesting compensation. Any amount which the employee saved, earned or intentionally failed to earn further to termination can be deducted in mitigation of the amount of the compensation. This reflects the general principle of damage mitigation.""""
                },
                {
                    'filename': 'match_report.txt',
                    'type': 'Exhibit',
                    'party': 'Club (Appellant)',
                    'text': """MATCH REPORT: OFK PETROVAC vs. ANORTHOSIS FAMAGUSTA FC
                    
Date: 23 July 2009
Competition: UEFA Europa League Qualification Round 2
Score: OFK Petrovac 3-1 Anorthosis Famagusta FC
Aggregate: 4-3 (Anorthosis won first leg 2-1)

Match Summary:
Anorthosis Famagusta FC has been eliminated from the UEFA Europa League qualification after losing 3-1 in the second leg against OFK Petrovac. Despite winning the first leg 2-1, the team's performance in Montenegro was below expectations, with multiple defensive errors.

Key Statistics:
- Possession: OFK Petrovac 52% - 48% Anorthosis
- Shots on target: OFK Petrovac 7 - 3 Anorthosis
- Corner kicks: OFK Petrovac 6 - 4 Anorthosis
- Yellow cards: OFK Petrovac 2 - 3 Anorthosis

This elimination represents a significant disappointment for the club and has financial implications due to the loss of European competition revenue."""
                },
                {
                    'filename': 'termination_notice.txt',
                    'type': 'Exhibit',
                    'party': 'Club (Appellant)',
                    'text': """TERMINATION NOTICE
                    
Date: 25 July 2009

Dear Mr. Middendorp,

We hereby inform you that Anorthosis Famagusta FC has decided to terminate your employment contract for just cause and with immediate effect.

The Board of the Club decided that you have seriously and grossly violated the express and implied terms of your employment and well as the Internal Regulations of the Club.

This decision has been taken after the meeting held on 24 July 2009 after considering the report and the suggestions of the Disciplinary Committee and after hearing your plea.

Yours sincerely,
Anorthosis Famagusta FC"""
                }
            ]
            
            st.session_state.documents = sample_docs
            st.success("Sample documents loaded successfully!")
            st.experimental_rerun()
    
    # Manual document upload
    with st.expander("Add Document Manually", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            doc_filename = st.text_input("Document Name")
            doc_type = st.selectbox("Document Type", [
                "Submission", 
                "Exhibit", 
                "Contract", 
                "Decision",
                "Transcript",
                "Other"
            ])
        
        with col2:
            doc_party = st.selectbox("Party", [
                "Club (Appellant)",
                "Coach (Respondent)",
                "Tribunal/CAS",
                "Both Parties",
                "Unknown"
            ])
        
        doc_text = st.text_area("Document Content", height=300)
        
        if st.button("Add Document") and doc_filename and doc_text:
            new_doc = {
                'filename': doc_filename,
                'type': doc_type,
                'party': doc_party,
                'text': doc_text
            }
            st.session_state.documents.append(new_doc)
            st.success(f"Document '{doc_filename}' added successfully!")
    
    # View uploaded documents
    if st.session_state.documents:
        st.header("Uploaded Documents")
        
        # Create DataFrame for display
        doc_df = pd.DataFrame([
            {
                'Filename': doc['filename'],
                'Type': doc['type'],
                'Party': doc['party'],
                'Length (chars)': len(doc['text'])
            } for doc in st.session_state.documents
        ])
        
        st.dataframe(doc_df)
        
        # Document preview
        preview_doc = st.selectbox("Select document to preview", 
                                  [doc['filename'] for doc in st.session_state.documents])
        
        selected_doc = next((doc for doc in st.session_state.documents 
                           if doc['filename'] == preview_doc), None)
        
        if selected_doc:
            st.subheader(f"Preview: {selected_doc['filename']}")
            st.text_area("Content", selected_doc['text'], height=300)
    else:
        st.info("No documents uploaded yet. Please add documents or load sample documents.")

with tab2:
    st.header("Search Documents")
    
    if not st.session_state.documents:
        st.warning("No documents available. Please upload documents in the 'Document Upload' tab.")
    else:
        # Search interface
        search_query = st.text_input("Search Query", 
                                    placeholder="Enter search terms (e.g., 'sporting results', 'just cause', 'Article 337c')")
        
        col1, col2 = st.columns(2)
        with col1:
            doc_type_filter = st.selectbox(
                "Filter by Document Type",
                ["All"] + list(set(doc['type'] for doc in st.session_state.documents))
            )
        
        with col2:
            party_filter = st.selectbox(
                "Filter by Party",
                ["All"] + list(set(doc['party'] for doc in st.session_state.documents))
            )
        
        # Search options
        with st.expander("Search Options"):
            show_context = st.checkbox("Show Extended Context", value=True)
            highlight_exhibits = st.checkbox("Highlight Exhibit References", value=True)
            show_comparison = st.checkbox("Show Party Position Comparison", value=True)
        
        if st.button("Search") and search_query:
            # Apply filters
            filters = {}
            if doc_type_filter != "All":
                filters['type'] = doc_type_filter
            if party_filter != "All":
                filters['party'] = party_filter
            
            # Execute search
            with st.spinner("Searching..."):
                results = search_documents(search_query, filters)
            
            # Display results
            if results:
                st.success(f"Found {len(results)} matches")
                
                # Export options
                col1, col2 = st.columns([1, 3])
                with col1:
                    export_format = st.selectbox("Export Format", ["Markdown", "CSV"])
                    if st.button("Export Results"):
                        export_data = export_results(results, export_format.lower())
                        if export_data:
                            # Create download link
                            b64 = base64.b64encode(export_data.encode()).decode()
                            filename = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M')}.{export_format.lower()}"
                            href = f'<a href="data:text/{export_format.lower()};base64,{b64}" download="{filename}">Click to download {export_format} file</a>'
                            st.markdown(href, unsafe_allow_html=True)
                
                # Group results by document
                doc_results = {}
                for result in results:
                    doc_id = result['doc_id']
                    if doc_id not in doc_results:
                        doc_results[doc_id] = []
                    doc_results[doc_id].append(result)
                
                # Display results by document
                for doc_id, results_group in doc_results.items():
                    doc = st.session_state.documents[doc_id]
                    
                    with st.expander(f"{doc['filename']} ({len(results_group)} matches)", expanded=True):
                        st.markdown(f"**Type:** {doc['type']} | **Party:** {doc['party']}")
                        
                        for i, result in enumerate(results_group):
                            st.markdown(f"#### Match {i+1}:")
                            
                            # Display the highlighted text
                            st.markdown(result['highlighted_text'])
                            
                            # Show context if enabled
                            if show_context:
                                # Find the paragraph's position in the document
                                para_id = result['para_id']
                                paragraphs = doc['text'].split('\n\n')
                                
                                # Show surrounding paragraphs if available
                                context = []
                                if para_id > 0:
                                    context.append(f"**Previous paragraph:** {paragraphs[para_id-1]}")
                                if para_id < len(paragraphs) - 1:
                                    context.append(f"**Next paragraph:** {paragraphs[para_id+1]}")
                                
                                if context:
                                    with st.expander("Show Context"):
                                        for ctx in context:
                                            st.markdown(ctx)
                            
                            # Extract and highlight exhibit references
                            if highlight_exhibits:
                                exhibits = extract_references(result['text'])
                                if exhibits:
                                    st.markdown("**Referenced Exhibits:** " + ", ".join([f"Exhibit {ex}" for ex in exhibits]))
                            
                            st.markdown("---")
                
                # Show position comparison if enabled and if we have both parties
                if show_comparison and search_query:
                    appellant_results = [r for r in results if "appellant" in r['party'].lower()]
                    respondent_results = [r for r in results if "respondent" in r['party'].lower()]
                    
                    if appellant_results and respondent_results:
                        st.subheader("Party Position Comparison")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("#### Appellant Position")
                            for result in appellant_results[:3]:  # Show top 3 matches
                                st.markdown(result['highlighted_text'])
                                st.markdown("---")
                        
                        with col2:
                            st.markdown("#### Respondent Position")
                            for result in respondent_results[:3]:  # Show top 3 matches
                                st.markdown(result['highlighted_text'])
                                st.markdown("---")
            else:
                st.info("No matches found. Try different search terms or adjust filters.")
        
        # Search tips
        with st.expander("Search Tips"):
            st.markdown("""
            ### Effective Search Strategies
            
            - **Use specific legal terms** like "just cause", "termination", "Swiss law"
            - **Search for article references** like "Article 337c", "Article 14"
            - **Look for case citations** like "CAS 2011/A/2596" 
            - **Search for party names** like "Middendorp" or "Anorthosis"
            - **Filter by document type** to focus on submissions or exhibits
            - **Filter by party** to see positions from either side
            
            ### Key Issues in Sports Arbitration
            
            - Just cause for termination
            - Poor sporting results as grounds for termination
            - Calculation of compensation
            - Obligation to mitigate damages
            - Jurisdiction of FIFA PSC for coaching contracts
            """)

with tab3:
    st.header("About This Tool")
    
    st.markdown("""
    ### Sports Arbitration Document Search
    
    This tool is designed specifically for sports arbitration professionals to quickly search and analyze case documents. It helps with:
    
    1. **Finding specific arguments and evidence** across submissions and exhibits
    2. **Comparing positions** between parties on key issues
    3. **Identifying references** to exhibits and supporting evidence
    4. **Preparing for hearings** by creating exportable search results
    
    ### Workflow
    
    1. Upload your case documents in the "Document Upload" tab
    2. Search for specific terms, legal concepts, or article references
    3. Review highlighted matches in context
    4. Export your findings for use in submissions or hearing preparation
    
    ### Features
    
    - **Simple text search** with highlighting
    - **Document filtering** by type and party
    - **Exhibit reference detection**
    - **Party position comparison**
    - **Context view** for better understanding
    - **Export functionality** for documentation
    
    For support or feedback, please contact the development team.
    """)
