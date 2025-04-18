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
    
    /* Explanation box - blue background */
    .explanation {
        font-size: 0.95rem;
        color: #1e3a8a;
        background-color: #eff6ff;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    /* Highlighted relevant paragraph - green background */
    .relevant-paragraph {
        background-color: #d1fae5;  /* Light green background */
        padding: 1rem;
        margin: 0;
    }
    
    /* Context paragraphs - normal styling */
    .context-paragraph {
        padding: 1rem;
        margin: 0;
    }
    
    /* Document section containing context and relevant paragraph */
    .document-section {
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        margin-bottom: 1.5rem;
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
</style>
""", unsafe_allow_html=True)

# Sample CAS decision content
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
    },
    {
        "id": "CAS 2023/A/9872",
        "title": "Astra Satellite Communications v. Celestrian National Frequency Authority",
        "date": "2023-05-18",
        "type": "Appeal",
        "sport": "Space Technology",
        "full_text": """
1. The Appellant, Astra Satellite Communications (hereinafter "Astracommex Regional" or the "Appellant"), is a multinational corporation specialized in satellite communications with its principal place of business in Celestria. The Appellant operates a constellation of satellites providing communications services across multiple regions.

2. The Respondent, the Celestrian National Frequency Authority (hereinafter the "NFA" or the "Respondent"), is the regulatory body responsible for managing radio frequency spectrum and satellite orbital positions within Celestria.

3. On 4 March 2020, Astracommex Regional submitted an application to the NFA for authorization to operate a new satellite network in the Ku-band frequency range. The application included technical specifications, orbital parameters, and frequency usage plans.

4. On 17 April 2020, the NFA acknowledged receipt of the application and initiated its review process in accordance with national and international regulations governing radio frequency spectrum allocation.

5. On 8 June 2020, the NFA requested additional technical information from Astracommex Regional regarding potential signal interference with existing satellite networks operating in adjacent frequency bands.

6. On 22 June 2020, Astracommex Regional provided the requested technical information, including detailed interference analyses demonstrating that the proposed network would comply with all applicable technical standards and would not cause harmful interference to existing systems.

7. On 14 August 2020, the NFA expressed concerns about the potential impact of the proposed satellite network on atmospheric data collection systems operating in nearby frequency bands, particularly weather monitoring satellites utilizing microwave sounders.

8. On 28 August 2020, Astracommex Regional submitted additional analyses addressing the NFA's concerns, providing evidence that the proposed network would maintain sufficient spectral separation from sensitive weather monitoring frequencies.

9. On 17 September 2020, the International Telecommunication Union (ITU) published a technical paper highlighting emerging concerns about the potential impact of certain Ku-band satellite operations on weather forecasting capabilities.

10. On 29 September 2020, the World Meteorological Organization (WMO) issued an advisory note recommending that national regulatory authorities exercise heightened scrutiny when authorizing new satellite systems operating near frequencies used for atmospheric sensing.

11. On 2 October 2020, the NFA requested additional documentation from Astracommex Regional to specifically address these atmospheric concerns. On 15 October 2020, Astracommex Regional responded to the NFA, declining to provide the requested supplementary information. On 15 December 2020, the NFA rejected Astracommex Regional's application to Ku-band frequencies on the basis of the NEPA.

12. On 20 December 2020, Astracommex Regional filed an appeal with the Celestrian Communications Appeal Tribunal challenging the NFA's decision. The Tribunal upheld the NFA's decision on 3 March 2021, finding that the regulatory authority had acted within its mandate to protect critical scientific infrastructure.

13. On 1 April 2021, Astracommex Regional filed a Statement of Appeal with the Court of Arbitration for Sport (CAS) against the decision rendered by the Celestrian Communications Appeal Tribunal.

II. PROCEEDINGS BEFORE THE COURT OF ARBITRATION FOR SPORT

14. The main issue for determination by the Panel is whether the NFA's rejection of Astracommex Regional's application for Ku-band frequency authorization was legitimate and proportionate.

15. Astracommex Regional argues that the NFA's decision was arbitrary and discriminatory, as other satellite operators had previously been granted similar authorizations without being required to provide the same level of documentation.

16. The NFA contends that its decision was based on legitimate concerns about the protection of atmospheric sensing capabilities essential for weather forecasting and climate monitoring, and that it applied the precautionary principle appropriately in this case.

17. The Panel finds that regulatory authorities have substantial discretion in managing radiofrequency spectrum, which is a limited natural resource requiring careful coordination to maximize its utility while preventing harmful interference.

18. The Panel notes that the emergence of new scientific evidence regarding potential interference with weather monitoring systems constitutes a legitimate basis for regulatory reassessment, even if this results in more stringent requirements than were applied in the past.

19. The Panel considers that Astracommex Regional's refusal to provide the additional documentation requested by the NFA on 2 October 2020 significantly undermined its position, as regulatory cooperation is an essential aspect of effective spectrum management.

20. The Panel acknowledges that while Astracommex Regional may face commercial disadvantages as a result of the NFA's decision, the protection of atmospheric sensing capabilities represents a compelling public interest that justifies certain restrictions on commercial satellite operations.

21. On 1 January 2021, one of Astracommex Regional's satellites, AS100, collided with a cube satellite (cubesat) that wandered around the adjacent orbit on a crossed orbital plate. The cube satellite was run by Valinor, a private company, in partnership with Celestria's Department of Defense ("DoD"). The cubesat was not equipped with any collision avoidance system and was smashed into small debris upon collision. AS100 was partially damaged – but both its Telemetry, Tracking, and Command (TT&C) system and its communication system ceased to function. The data up until the impact moment indicated an interference to onboard computing system by extreme radiation. This record was transmitted and stored in the Astra System, and subsequently used by Astracommex's engineers to assess the event and prepare software updates for existing and future Astra satellites.

22. On 5 January 2021, the DoD initiated an investigation and ordered Astracommex Regional to suspend all satellite communications within the territory of Celestria.

23. On 10 January 2021, Astracommex Regional submitted a request to the NFA for temporary emergency frequency allocation to restore essential services while the investigation was ongoing. The NFA denied this request on 12 January 2021, citing the ongoing DoD investigation.

24. The Panel finds that the collision incident, while concerning, is not directly relevant to the legitimacy of the NFA's earlier decision regarding Ku-band frequency authorization, as it occurred after the decision was made and involved different technical issues.

25. However, the Panel notes that the collision incident does highlight the importance of careful regulatory oversight of orbital activities and the potential consequences of inadequate coordination among satellite operators.

III. DECISION

The Court of Arbitration for Sport rules that:

1. The appeal filed by Astra Satellite Communications on 1 April 2021 against the decision rendered by the Celestrian Communications Appeal Tribunal on 3 March 2021 is dismissed.

2. The decision rendered by the Celestrian Communications Appeal Tribunal on 3 March 2021 is confirmed.

3. The costs of the arbitration, to be determined and communicated separately by the CAS Court Office, shall be borne by Astra Satellite Communications.

4. Astra Satellite Communications shall pay to the Celestrian National Frequency Authority the amount of EUR 12,000 (twelve thousand Euros) as a contribution towards its legal and other costs incurred in connection with the present arbitration.

5. All other motions or prayers for relief are dismissed.
        """,
        "claimant": "Astra Satellite Communications",
        "respondent": "Celestrian National Frequency Authority",
        "panel": "Prof. Maria Stellanova (President), Dr. Henry Orbital, Ms. Jenna Frequency",
        "decision": "Appeal dismissed, NFA decision upheld.",
        "keywords": ["frequency allocation", "satellite communications", "regulatory authority", "precautionary principle", "satellite collision"]
    }
]

# Convert to DataFrame for easier manipulation
df_decisions = pd.DataFrame(cas_decisions)

# Initialize session state
if 'search_history' not in st.session_state:
    st.session_state.search_history = [
        {"query": "buy-out clause", "timestamp": "2024-04-18 15:32:42"},
        {"query": "sporting results", "timestamp": "2024-04-18 14:20:23"},
        {"query": "satellite collision", "timestamp": "2024-04-18 11:45:18"}
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

# Enhanced semantic search function that finds paragraphs and their surrounding context
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
        cleaned_paragraphs = []
        
        # Clean the paragraphs and remove empty ones
        for p in paragraphs:
            p = p.strip()
            if p:
                cleaned_paragraphs.append(p)
        
        # Find relevant paragraphs
        case_chunks = []
        for para_idx, para in enumerate(cleaned_paragraphs):
            score = 0
            for term in query_terms:
                if term in para.lower():
                    score += 1
            
            # Only include if it has some relevance
            if score > 0:
                # Get explanation based on content
                explanation = generate_relevance_explanation(para, query_terms)
                
                # Find the surrounding paragraphs for context
                context_paragraphs = []
                
                # Get paragraph before (if available)
                if para_idx > 0:
                    context_paragraphs.append({"text": cleaned_paragraphs[para_idx-1], "position": "before"})
                
                # The matched paragraph itself
                context_paragraphs.append({"text": para, "position": "match", "score": score})
                
                # Get paragraph after (if available)
                if para_idx < len(cleaned_paragraphs) - 1:
                    context_paragraphs.append({"text": cleaned_paragraphs[para_idx+1], "position": "after"})
                
                # Create a chunk with the set of context paragraphs
                chunk = {
                    "case_id": case["id"],
                    "case_title": case["title"],
                    "paragraphs": context_paragraphs,
                    "relevance_score": score,
                    "explanation": explanation
                }
                
                case_chunks.append(chunk)
        
        # If we found relevant chunks, add this case to results
        if case_chunks:
            # Sort chunks by relevance
            case_chunks = sorted(case_chunks, key=lambda x: x["relevance_score"], reverse=True)
            
            # Only keep top 3 chunks per case
            case_chunks = case_chunks[:3]
            
            # Add all chunks to overall list
            all_chunks.extend(case_chunks)
            
            # Add case to results
            result = case.copy()
            result["relevant_chunks"] = case_chunks
            all_results.append(result)
    
    # Sort results by the maximum relevance score of any chunk
    if all_results:
        all_results = sorted(all_results, 
                            key=lambda x: max([c["relevance_score"] for c in x["relevant_chunks"]]), 
                            reverse=True)
    
    # Sort all chunks by relevance
    all_chunks = sorted(all_chunks, key=lambda x: x["relevance_score"], reverse=True)
    
    return all_results, all_chunks

# Generate a detailed explanation for the blue box at the top
def generate_relevance_explanation(text, query_terms):
    # Default explanations based on common legal topics
    explanations = {
        "buy-out clause": "Understanding buy-out clauses involves examining their contractual nature, enforceability, and proportionality.",
        "contract termination": "Contract termination analysis requires determining whether just cause existed and calculating appropriate compensation.",
        "sporting results": "Poor sporting results alone typically do not constitute just cause for terminating a coach's contract.",
        "coach contract": "Coach employment contracts have specific characteristics different from player contracts under FIFA regulations.",
        "just cause": "Just cause for termination requires serious breaches of contract obligations, not merely disappointing performance.",
        "satellite collision": "Processing of satellite collision events involves assessing damage, analyzing data, and preparing software updates.",
        "frequency allocation": "Frequency allocation disputes involve regulatory discretion, technical assessments, and protection of public interests."
    }
    
    # Check if any of our pre-defined topics match the query
    for topic, explanation in explanations.items():
        if topic in " ".join(query_terms).lower():
            return explanation
    
    # If no pre-defined explanation matches, generate a generic one
    terms_text = ", ".join([f"'{term}'" for term in query_terms])
    return f"Legal analysis of {terms_text} involves examining relevant regulations, precedents, and specific case circumstances."

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
            time.sleep(2)  # 2 second delay
            
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
                    
                    # Display each relevant chunk with its context
                    for chunk in case['relevant_chunks']:
                        # First, show the explanation box
                        st.markdown(f"""
                        <div class="explanation">
                        <strong>Explanation:</strong> {chunk['explanation']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Now display the paragraphs in their natural order
                        paragraphs_html = ""
                        
                        for para in chunk['paragraphs']:
                            if para['position'] == 'match':
                                # This is the matching paragraph - highlight it with green background
                                paragraphs_html += f'<div class="relevant-paragraph">{para["text"]}</div>'
                            else:
                                # This is a context paragraph - normal styling
                                paragraphs_html += f'<div class="context-paragraph">{para["text"]}</div>'
                        
                        # Output the entire document section
                        st.markdown(f"""
                        <div class="document-section">
                        {paragraphs_html}
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
        - buy-out clause
        - sporting results
        - satellite collision
        - coach contract
        - just cause
        - compensation
        """)
