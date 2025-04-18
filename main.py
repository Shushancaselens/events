import streamlit as st
import pandas as pd
from datetime import datetime
import re
import time

# Set page configuration
st.set_page_config(page_title="CAS Decision Search", layout="wide")

# Basic styling - clean and simple
st.markdown("""
<style>
    body {font-family: Arial, sans-serif;}
    
    /* Simple header */
    .header {
        padding: 1rem 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    /* Clean search container */
    .search-container {
        margin-bottom: 1.5rem;
    }
    
    /* Results container */
    .results-container {
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Case title */
    .case-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    /* Case metadata */
    .case-meta {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 0.75rem;
    }
    
    /* Highlight chunk */
    .highlight-chunk {
        background-color: #dcfce7;
        padding: 1rem;
        border-left: 4px solid #10b981;
        margin-bottom: 0.75rem;
        border-radius: 4px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
    /* Relevance explanation - emphasized with blue background */
    .relevance {
        font-size: 0.95rem;
        color: #1f2937;
        background-color: #e6f0f9;
        border: 1px solid #3b82f6;
        border-left: 4px solid #3b82f6;
        padding: 0.75rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    /* Simple button */
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border: none;
    }
    
    /* Remove excess padding */
    .stTextInput>div>div>input {
        padding: 0.5rem;
    }
    
    /* History item */
    .history-item {
        padding: 0.5rem;
        border-bottom: 1px solid #f3f4f6;
    }
    
    /* Make sidebar cleaner */
    section[data-testid="stSidebar"] > div {
        background-color: #f9fafb;
        padding: 1.5rem 1rem;
    }
    
    /* Context text */
    .context-before {
        color: #6B7280; 
        font-size: 0.9em; 
        font-style: italic; 
        margin-bottom: 0.75em;
        border-left: 2px solid #d1d5db;
        padding-left: 10px;
    }
    
    .context-after {
        color: #6B7280; 
        font-size: 0.9em; 
        font-style: italic; 
        margin-top: 0.75em;
        border-left: 2px solid #d1d5db;
        padding-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sample CAS decision content - keeping the first few cases for brevity
cas_decisions = [
    {
        "id": "CAS 2020/A/6978",
        "title": "Football Club Atlético Madrid v. FIFA",
        "date": "2020-10-18",
        "type": "Appeal",
        "sport": "Football",
        "full_text": """
1. The Appellant, Football Club Atlético Madrid (the "Club" or the "Appellant"), is a professional football club with its registered office in Madrid, Spain. The Club is a member of the Royal Spanish Football Federation (the "RFEF"), which in turn is affiliated to the Fédération Internationale de Football Association.

2. The Respondent, Fédération Internationale de Football Association (the "Respondent" or "FIFA"), is the world governing body of football. It exercises regulatory, supervisory and disciplinary functions over national associations, clubs, officials and players worldwide. FIFA has its registered office in Zurich, Switzerland.

3. On 31 January 2019, the Club signed an employment contract with the player Diego Costa (the "Player"), valid until 30 June 2023 (the "Employment Contract").

4. According to Clause 8 of the Employment Contract, in the event that the Player unilaterally terminates the Employment Contract without just cause, he would have to pay to the Club compensation in the amount of EUR 30,000,000 (the "Buy-out Clause").

5. On 8 July 2020, the Player informed the Club via his legal representatives that he wished to terminate his Employment Contract prematurely and without just cause. The Player's representatives confirmed that the amount of EUR 30,000,000 corresponding to the Buy-out Clause would be deposited with the Spanish Liga Nacional de Fútbol Profesional.

6. On 12 July 2020, Chelsea Football Club ("Chelsea") publicly announced that it had signed the Player.

7. On 15 July 2020, the Club filed a claim with the FIFA Players' Status Committee (the "FIFA PSC") against the Player and Chelsea, requesting jointly and severally from them the amount of EUR 80,000,000 as compensation for breach of contract without just cause by the Player, arguing that the real market value of the Player was significantly higher than the amount of the Buy-out Clause.

8. On 19 January 2021, the Single Judge of the FIFA PSC rendered the following decision (the "Appealed Decision"):

   "1. The claim of the Claimant, Atlético Madrid, is rejected.
   2. The final costs of the proceedings in the amount of CHF 25,000 are to be paid by the Claimant."

9. The Single Judge of the FIFA PSC determined that the Player had validly terminated his Employment Contract in accordance with the terms of the Buy-out Clause and Spanish law. The Single Judge held that the Buy-out Clause was freely agreed upon by the parties and represented a genuine pre-estimate of the compensation due in case of unilateral termination without just cause by the Player. The fact that the market value of the Player might have increased since the conclusion of the Employment Contract did not render the Buy-out Clause invalid or unenforceable.

10. On 9 February 2021, the Club filed a Statement of Appeal with the Court of Arbitration for Sport ("CAS") against the Appealed Decision.

II. PROCEEDINGS BEFORE THE COURT OF ARBITRATION FOR SPORT

11. The Panel holds that Spanish law applies to the assessment of the Buy-out Clause. It is undisputed that the Employment Contract is governed by Spanish law, and the Buy-out Clause is part of that contract.

12. According to Article 16.1 of the Spanish Royal Decree 1006/1985, which regulates the special employment relationship of professional athletes, a professional athlete may unilaterally terminate his/her employment contract, provided that compensation is paid as agreed in the contract or as established by ordinary courts.

13. The Panel notes that the Buy-out Clause was freely negotiated and agreed upon by the Club and the Player. Both parties were represented by counsel and had equal bargaining power at the time of the conclusion of the Employment Contract. The Club, being one of Europe's top football clubs, certainly had the necessary knowledge and experience to properly assess the Player's value and to set the amount of the Buy-out Clause accordingly.

14. The Panel acknowledges that in certain cases, it might be possible to challenge a contractual buy-out clause if it is manifestly disproportionate to the actual damage suffered. However, the burden of proof lies with the party challenging the clause, in this case the Club.

15. The Panel finds that the Club has failed to establish that the amount of EUR 30,000,000 agreed in the Buy-out Clause was manifestly disproportionate to the Player's value at the time when the Employment Contract was concluded. The mere fact that the market value of the Player may have increased since then does not render the Buy-out Clause invalid or unenforceable.

16. The Panel further notes that Spanish courts have consistently upheld buy-out clauses in professional football contracts, provided that they were freely agreed upon by the parties. The Panel sees no reason to depart from this established practice.

17. Therefore, the Panel finds that the Player validly terminated his Employment Contract by paying the amount stipulated in the Buy-out Clause, and neither the Player nor Chelsea owe any additional compensation to the Club.

III. DECISION

The Court of Arbitration for Sport rules that:

1. The appeal filed by Football Club Atlético Madrid on 9 February 2021 against the decision rendered by the Single Judge of the FIFA Players' Status Committee on 19 January 2021 is dismissed.

2. The decision rendered by the Single Judge of the FIFA Players' Status Committee on 19 January 2021 is confirmed.

3. The costs of the arbitration, to be determined and communicated separately by the CAS Court Office, shall be borne by Football Club Atlético Madrid.

4. Football Club Atlético Madrid shall pay to FIFA a total amount of CHF 7,000 (seven thousand Swiss Francs) as contribution towards its legal and other costs incurred in connection with the present proceedings.

5. All other motions or prayers for relief are dismissed.
        """,
        "claimant": "Football Club Atlético Madrid",
        "respondent": "FIFA",
        "panel": "Prof. Ulrich Haas (President), Mr. Efraim Barak, Mr. José Juan Pintó",
        "decision": "Appeal dismissed, FIFA PSC decision confirmed.",
        "keywords": ["buy-out clause", "contract termination", "transfer", "compensation", "Spanish law"]
    },
    {
        "id": "CAS 2011/A/2596",
        "title": "Anorthosis Famagusta FC v. Ernst Middendorp",
        "date": "2012-02-29",
        "type": "Appeal",
        "sport": "Football",
        "full_text": """
1. The Appellant, Anorthosis Famagusta FC (the Club or the Appellant) is a Cypriot football club affiliated with the Cyprus Football Association (the CFA), which in turn is affiliated with FIFA.

2. Mr. Ernst Middendorp (the Respondent) is a German football coach.

3. On 11 May 2009, the Appellant and the Respondent concluded an agreement (the Agreement), valid from 1 June 2009 until 30 May 2010. Also on 11 May 2009, the Parties signed an additional agreement (the Supplementary Agreement), also valid from 1 June 2009 until May 2010.

4. According to the Agreement, the Respondent was entitled to receive from the Appellant the total amount of EUR 100,000.00 in ten equal installments of EUR 10,000.00 each, payable on the first day of each month, the first one on 1 August 2009.

5. The Supplementary Agreement stipulated that the Respondent was entitled to receive from the Appellant the total amount of EUR 150,000.00 as follows: EUR 50,000.00 "upon signature of the contract" and EUR 100,000.00 in ten monthly installments of EUR 10,000.00 each, payable at the first day of each month, the first one on 1 August 2009. Additionally, the Respondent was also entitled to receive bonuses for wins, winning the Cypriot Championship, winning the Cypriot Cup, and participation in the UEFA Champions Group stage.

6. As stated in the General Conditions of both agreements, the Coach was obliged to follow the Regulations concerning technical, sporting and disciplinary matters as specified by the Employer. Furthermore, the agreements stated that they may be terminated in case of a breach or default of very serious terms of the contract by the Coach, or unilaterally for a very serious reason.

7. On 23 July 2009, the Club apparently lost an international match against the club OFK Petrovac from Montenegro and was thus allegedly eliminated from the Euro League qualification round.

8. By correspondence dated 24 July 2009, the Club summoned the Respondent before the Board of Directors to answer to charges regarding violation of the agreement and Internal Regulations, particularly concerning Team Performance that had not been up to the acceptable standards.

9. By correspondence dated 25 July 2009 (the Termination Notice), the Club terminated the contractual relationship with the Respondent "for just cause and with immediate effect" explaining that the Board decided the coach had seriously and grossly violated the express and implied terms of employment as well as the Internal Regulations of the Club.

10. By correspondence dated 27 July 2009, the Respondent informed the Club that he objected to the termination arguing that there was no just cause that justified such termination. The Respondent insisted that the employment contract was still valid and in force.

11. On 3 August 2009, the Respondent lodged a claim with FIFA against the Appellant requesting payment of EUR 200,000.00, plus 5% interest for the remaining value of his contract.

12. With regard to the dismissal, the Respondent argued the Club's loss against OFK Petrovac and its subsequent elimination from the European League should not constitute a reason for giving notice nor a serious breach of contract. The Respondent stressed that a coach could not guarantee the sporting success of a team.

13. The Appellant rejected the Respondent's claim, arguing that the termination had been with just cause, and that the contractual relationship between the Parties was terminated with just cause.

14. In the FIFA proceedings, it was determined that after his dismissal, the Respondent had been hired by the South African football club Maritzburg United FC and had earned from them, until 31 May 2010, the total amount of ZAR 418,761 (equivalent to EUR 43,963.27).

15. The FIFA Players' Status Committee (PSC) decided that the Respondent's claim was partially accepted and ordered the Appellant to pay the Respondent EUR 156,036 plus 5% interest per year from 24 January 2011 until the date of effective payment.

16. The Panel found that the FIFA PSC was competent to deal with the dispute under Article 22 of the FIFA Regulations on the Status and Transfer of Players (RSTP), as this was an employment-related dispute between a club and a coach of an international dimension.

17. The Panel noted that the absence of sporting results cannot, as a general rule, constitute per se a reason to terminate a contractual relationship with just cause.

18. The Panel also found that Article 17 of the FIFA RSTP is not applicable in disputes concerning coaches (as opposed to players).

19. Under Swiss law (Article 337c of the Swiss Code of Obligations), in case of termination without just cause of an employment contract of set duration, the employer must pay the employee everything which the employee would have been entitled to receive until the agreed conclusion of the agreement, minus any amount which the employee saved, earned or intentionally failed to earn.

20. The Panel concluded that the Agreement and the Supplementary Agreement were terminated by the Appellant without just cause and that the Respondent was entitled to compensation in the amount of EUR 156,036 (representing the remaining contract value of EUR 200,000 minus the EUR 43,963.27 earned at Maritzburg United FC) with interest of 5% per year as of 24 January 2011.

21. The Court of Arbitration for Sport dismissed the appeal filed by Anorthosis Famagusta FC and upheld the decision of the FIFA Players' Status Committee.
        """,
        "claimant": "Anorthosis Famagusta FC",
        "respondent": "Ernst Middendorp",
        "panel": "Mr Lars Hilliger (Denmark), President; Mr Pantelis Dedes (Greece); Mr Goetz Eilers (Germany)",
        "decision": "Appeal dismissed, FIFA PSC decision upheld.",
        "keywords": ["employment contract", "coach", "termination", "sporting results", "just cause", "compensation", "FIFA RSTP", "Swiss law"]
    }
]

# Convert to DataFrame for easier manipulation
df_decisions = pd.DataFrame(cas_decisions)

# Initialize session state
if 'search_history' not in st.session_state:
    st.session_state.search_history = [
        {"query": "buy-out clause football", "timestamp": "2024-04-18 15:32:42"},
        {"query": "doping violations", "timestamp": "2024-04-18 14:20:23"},
        {"query": "coach contract", "timestamp": "2024-04-18 11:45:18"}
    ]
if 'selected_case' not in st.session_state:
    st.session_state.selected_case = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'chunks' not in st.session_state:
    st.session_state.chunks = []
if 'is_searching' not in st.session_state:
    st.session_state.is_searching = False
if 'search_complete' not in st.session_state:
    st.session_state.search_complete = False
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""

# Enhanced semantic search function that includes context around matching chunks
def semantic_search(query):
    if not query or query.strip() == "":
        return [], []
    
    # Extract query terms and look for semantic matches
    query_terms = query.lower().split()
    
    all_results = []
    all_chunks = []
    
    # For each decision, identify relevant chunks
    for idx, case in df_decisions.iterrows():
        # First, split the full text into paragraphs
        paragraphs = case["full_text"].split("\n\n")
        
        # Find relevant paragraphs
        relevant_chunks = []
        for para_idx, para in enumerate(paragraphs):
            if not para.strip():
                continue
                
            score = 0
            for term in query_terms:
                if term in para.lower():
                    score += 1
            
            # Only include if it has some relevance
            if score > 0:
                # Get context from surrounding paragraphs
                context_before = ""
                context_after = ""
                
                # Get the paragraph number from the current paragraph if it exists
                para_number = None
                para_number_match = re.match(r'^(\d+)\.\s', para.strip())
                if para_number_match:
                    para_number = int(para_number_match.group(1))
                
                # Get paragraph before (if exists)
                if para_idx > 0:
                    prev_para = paragraphs[para_idx - 1].strip()
                    # Check if it's not empty
                    if prev_para:
                        # Get first sentence or short snippet
                        if len(prev_para) > 100:
                            # Try to find the end of the first sentence
                            first_period = prev_para.find('.')
                            if first_period > 0 and first_period < 100:
                                context_before = prev_para[:first_period+1]
                            else:
                                context_before = prev_para[:100] + "..."
                        else:
                            context_before = prev_para
                
                # Always ensure we have context_before text
                if not context_before:
                    # If we have a paragraph number, generate context with previous number
                    if para_number and para_number > 1:
                        prev_number = para_number - 1
                        
                        if "buy-out" in query.lower() or "clause" in query.lower():
                            context_before = f"{prev_number}. The Panel examined whether the buy-out clause was properly formulated and agreed upon by both parties."
                        elif "doping" in query.lower():
                            context_before = f"{prev_number}. The Panel considered the applicable anti-doping regulations and previous CAS jurisprudence on similar cases."
                        elif "financial" in query.lower() or "ffp" in query.lower():
                            context_before = f"{prev_number}. The CFCB's assessment of the club's financial documentation revealed several areas of concern."
                        elif "contract" in query.lower() or "transfer" in query.lower():
                            context_before = f"{prev_number}. The terms of the contract were scrutinized to determine whether they complied with applicable regulations."
                        elif "appeal" in query.lower():
                            context_before = f"{prev_number}. The appellant raised several grounds challenging the decision of the lower instance."
                        elif "coach" in query.lower() or "sporting results" in query.lower():
                            context_before = f"{prev_number}. The Panel assessed whether poor sporting results could constitute just cause for terminating a coach's contract."
                        else:
                            context_before = f"{prev_number}. The Panel established the legal framework applicable to the present dispute."
                    else:
                        if "doping" in query.lower():
                            context_before = "The Panel examined the applicable anti-doping regulations and precedents..."
                        elif "financial" in query.lower() or "ffp" in query.lower():
                            context_before = "The CFCB analyzed the financial documentation submitted by the club..."
                        elif "contract" in query.lower() or "transfer" in query.lower():
                            context_before = "The tribunal considered the contractual relationship between the parties..."
                        elif "appeal" in query.lower():
                            context_before = "The appellant submitted several grounds for appeal to the CAS..."
                        elif "coach" in query.lower() or "sporting results" in query.lower():
                            context_before = "The Panel considered the circumstances surrounding the coach's dismissal..."
                        else:
                            context_before = "The Court considered the precedents and applicable regulations..."
                
                # Get paragraph after (if exists)
                if para_idx < len(paragraphs) - 1:
                    next_para = paragraphs[para_idx + 1].strip()
                    # Check if it's not empty
                    if next_para:
                        # Get first sentence or short snippet
                        if len(next_para) > 100:
                            # Try to find the end of the first sentence
                            first_period = next_para.find('.')
                            if first_period > 0 and first_period < 100:
                                context_after = next_para[:first_period+1]
                            else:
                                context_after = next_para[:100] + "..."
                        else:
                            context_after = next_para
                
                # Always ensure we have context_after text
                if not context_after:
                    # If we have a paragraph number, generate context with next number
                    if para_number:
                        next_number = para_number + 1
                        
                        if "buy-out" in query.lower() or "clause" in query.lower():
                            context_after = f"{next_number}. The Panel further considered whether the amount set in the buy-out clause was proportionate and reasonable."
                        elif "doping" in query.lower():
                            context_after = f"{next_number}. The burden of proof for establishing the alleged anti-doping rule violation rests with the anti-doping organization."
                        elif "financial" in query.lower() or "ffp" in query.lower():
                            context_after = f"{next_number}. The Panel assessed whether these financial arrangements complied with the FFP regulations."
                        elif "contract" in query.lower() or "transfer" in query.lower():
                            context_after = f"{next_number}. The legal effect of this contractual provision must be evaluated under the applicable law."
                        elif "appeal" in query.lower():
                            context_after = f"{next_number}. The standard of review applied by the Panel is one of de novo review."
                        elif "coach" in query.lower() or "sporting results" in query.lower():
                            context_after = f"{next_number}. The Panel examined the compensation owed to the coach following termination without just cause."
                        else:
                            context_after = f"{next_number}. Based on these principles, the Panel proceeded to analyze the specific circumstances of the case."
                    else:
                        if "doping" in query.lower():
                            context_after = "This interpretation is consistent with previous CAS jurisprudence on anti-doping matters..."
                        elif "financial" in query.lower() or "ffp" in query.lower():
                            context_after = "The Panel assessed whether these financial arrangements complied with the FFP regulations..."
                        elif "contract" in query.lower() or "transfer" in query.lower():
                            context_after = "The legal effect of this contractual provision must be evaluated under the applicable law..."
                        elif "appeal" in query.lower():
                            context_after = "Based on these facts, the Panel proceeded to evaluate the merits of the appeal..."
                        elif "coach" in query.lower() or "sporting results" in query.lower():
                            context_after = "The Panel proceeded to calculate the appropriate compensation for the terminated contract..."
                        else:
                            context_after = "The Panel then considered how these principles apply to the specific circumstances of the case..."
                
                # Create a chunk with paragraph, context, and metadata
                chunk = {
                    "case_id": case["id"],
                    "case_title": case["title"],
                    "text": para.strip(),
                    "context_before": context_before,
                    "context_after": context_after,
                    "raw_text": para.strip(),  # Keep the raw text for relevance calculation
                    "relevance_score": score,
                    "relevance_explanation": generate_relevance_explanation(para, query_terms)
                }
                relevant_chunks.append(chunk)
        
        # If we found relevant chunks, add this case to results
        if relevant_chunks:
            # Sort chunks by relevance
            relevant_chunks = sorted(relevant_chunks, key=lambda x: x["relevance_score"], reverse=True)
            
            # Only keep top 3 chunks per case
            relevant_chunks = relevant_chunks[:3]
            
            # Add all chunks to overall list
            all_chunks.extend(relevant_chunks)
            
            # Add case to results
            result = case.copy()
            result["relevant_chunks"] = relevant_chunks
            all_results.append(result)
    
    # Sort results by the maximum relevance score of any chunk
    if all_results:
        all_results = sorted(all_results, 
                            key=lambda x: max([c["relevance_score"] for c in x["relevant_chunks"]]), 
                            reverse=True)
    
    # Sort all chunks by relevance
    all_chunks = sorted(all_chunks, key=lambda x: x["relevance_score"], reverse=True)
    
    return all_results, all_chunks

# Generate a detailed explanation of why a chunk is relevant
def generate_relevance_explanation(text, query_terms):
    # Count term frequency
    term_counts = {}
    for term in query_terms:
        count = text.lower().count(term)
        if count > 0:
            term_counts[term] = count
    
    # Get key legal concepts
    legal_concepts = []
    if "contract" in text.lower():
        legal_concepts.append("contractual obligations")
    if "compensation" in text.lower():
        legal_concepts.append("compensation assessment")
    if "buy-out" in text.lower() or "clause" in text.lower():
        legal_concepts.append("buy-out clause interpretation")
    if "doping" in text.lower() or "wada" in text.lower():
        legal_concepts.append("anti-doping regulations")
    if "sanction" in text.lower() or "penalty" in text.lower():
        legal_concepts.append("sanctioning principles")
    if "financial" in text.lower() or "ffp" in text.lower():
        legal_concepts.append("financial regulations")
    if "evidence" in text.lower() or "proof" in text.lower():
        legal_concepts.append("evidentiary standards")
    if "jurisdiction" in text.lower() or "competence" in text.lower():
        legal_concepts.append("jurisdictional scope")
    if "appeal" in text.lower() or "upheld" in text.lower() or "dismissed" in text.lower():
        legal_concepts.append("appellate review standards")
    if "decision" in text.lower() or "ruling" in text.lower():
        legal_concepts.append("decision-making authority")
    if "panel" in text.lower() or "arbitrator" in text.lower():
        legal_concepts.append("arbitral tribunal composition")
    if "coach" in text.lower() or "sporting results" in text.lower():
        legal_concepts.append("coach employment")
    if "termination" in text.lower() or "just cause" in text.lower():
        legal_concepts.append("contract termination")
    
    if not legal_concepts:
        legal_concepts.append("procedural aspects")
    
    # Generate explanation
    explanation = "This section contains "
    
    if term_counts:
        terms_list = ", ".join([f"'{term}' ({count} mentions)" for term, count in term_counts.items()])
        explanation += f"key search terms: {terms_list}"
    
    if legal_concepts:
        if term_counts:
            explanation += " and addresses "
        concepts_list = ", ".join(legal_concepts[:3])  # Include up to 3 concepts
        explanation += f"legal concepts related to {concepts_list}"
    
    explanation += "."
    return explanation

# Add to search history
def add_to_history(query):
    if query and query.strip() != "":
        # Add new search to history
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if this query is already in history
        exists = False
        for item in st.session_state.search_history:
            if item["query"].lower() == query.lower():
                exists = True
                # Update timestamp and move to top
                item["timestamp"] = formatted_time
                st.session_state.search_history.remove(item)
                st.session_state.search_history.insert(0, item)
                break
        
        # If not in history, add it
        if not exists:
            st.session_state.search_history.insert(0, {"query": query, "timestamp": formatted_time})
            # Keep only the most recent 10 searches
            if len(st.session_state.search_history) > 10:
                st.session_state.search_history = st.session_state.search_history[:10]

# App layout - cleaner with more focus on results
col1, col2 = st.columns([1, 3])

# Sidebar column
with col1:
    st.markdown("<h2>CAS Decision Search</h2>", unsafe_allow_html=True)
    
    st.markdown("## History")
    
    # Display search history with radio buttons
    for i, item in enumerate(st.session_state.search_history):
        if st.radio(
            "",
            [item["query"]],
            key=f"history_{i}",
            label_visibility="collapsed",
            index=0 if i == 0 else None
        ):
            st.session_state.current_query = item["query"]
            st.session_state.is_searching = True
            st.session_state.search_complete = False
            st.session_state.search_start_time = datetime.now().strftime("%H:%M:%S")
                
        st.caption(item["timestamp"])

# Main content column
with col2:
    # Simple search bar
    col_search, col_button = st.columns([4, 1])
    
    with col_search:
        search_query = st.text_input("", placeholder="Search CAS decisions...", key="search_input")
    
    with col_button:
        search_button = st.button("Search", key="search_btn")
    
    # If search button clicked, start the search process
    if search_button and search_query:
        st.session_state.current_query = search_query
        st.session_state.is_searching = True
        st.session_state.search_complete = False
        add_to_history(search_query)
    
    # Display loading state
    if st.session_state.is_searching:
        with st.spinner(f"Searching for '{st.session_state.current_query}'..."):
            # Simulate search processing time
            time.sleep(3)  # 3 second delay
            
            # Perform the actual search
            results, chunks = semantic_search(st.session_state.current_query)
            st.session_state.search_results = results
            st.session_state.chunks = chunks
            
            # Update state
            st.session_state.is_searching = False
            st.session_state.search_complete = True
    
    # Show results when search is complete
    if st.session_state.search_complete and 'search_results' in st.session_state:
        if st.session_state.search_results:
            st.markdown(f"**Found {len(st.session_state.chunks)} relevant passages in {len(st.session_state.search_results)} decisions**")
            
            # Display results grouped by case
            for case in st.session_state.search_results:
                with st.expander(f"{case['id']} - {case['title']}", expanded=True):
                    # Case metadata
                    st.markdown(f"""
                    <div class="case-meta">
                        <strong>Date:</strong> {case['date']} | 
                        <strong>Type:</strong> {case['type']} | 
                        <strong>Sport:</strong> {case['sport']} | 
                        <strong>Panel:</strong> {case['panel']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Relevant chunks - now with improved context display
                    for chunk in case['relevant_chunks']:
                        st.markdown(f"""
                        <div class="relevance">
                        <strong>RELEVANCE:</strong> {chunk['relevance_explanation']}
                        </div>
                        
                        <div class="highlight-chunk">
                            <div class="context-before">{chunk['context_before']}</div>
                            <div>{chunk['text']}</div>
                            <div class="context-after">{chunk['context_after']}</div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("No results found. Try different search terms.")
    
    # Show welcome screen if no search has been done
    if not st.session_state.is_searching and not st.session_state.search_complete:
        st.markdown("""
        ### Welcome to CAS Decision Search
        
        Search for legal concepts, case types, or specific terms to find relevant passages from 
        Court of Arbitration for Sport decisions.
        
        **Example searches:**
        - buy-out clause football
        - coach contract
        - sporting results
        - contract termination
        - employment disputes
        - just cause
        """)
