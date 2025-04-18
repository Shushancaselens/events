import streamlit as st
import pandas as pd
from datetime import datetime
import random

# Set page configuration
st.set_page_config(page_title="CASLens", layout="wide")

# Custom CSS to match the style in the screenshot
st.markdown("""
<style>
    body {font-family: Arial, sans-serif;}
    .main-header {color: #1F2937; font-size: 24px; font-weight: bold;}
    .sub-header {color: #374151; font-size: 18px; font-weight: bold;}
    .sidebar-content {background-color: #F3F4F6; padding: 20px; border-radius: 5px;}
    .disclaimer {background-color: #FEE2E2; padding: 10px; border-radius: 5px; color: #DC2626;}
    .explanation {background-color: #E6F0F9; padding: 10px; border-radius: 5px;}
    .highlight {background-color: #ECFDF5; padding: 10px; border-radius: 5px;}
    .selected-highlight {background-color: #ECFDF5; padding: 10px; border-radius: 5px; border-left: 4px solid #10B981;}
    .caselens-primary {background-color: #4F46E5; color: white;}
    .centered-title {text-align: center; margin-bottom: 1rem;}
    .case-header {font-size: 1.2rem; font-weight: bold; margin-top: 1.5rem; margin-bottom: 0.5rem;}
    
    /* Button styling */
    .stButton>button {
        background-color: #4F46E5 !important; 
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
    }
    .stButton>button:hover {
        background-color: #4338CA !important;
    }
    
    /* Search styling */
    .stTextInput>div>div>input {
        border-radius: 5px;
        border: 1px solid #D1D5DB;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: #F3F4F6;
        border-radius: 4px 4px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #4B5563;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5;
        color: white !important;
    }
    
    /* Radio button styling */
    .stRadio>div {
        padding: 5px 10px;
        background-color: #F9FAFB;
        border-radius: 4px;
        margin-bottom: 5px;
    }
    .stRadio>div:hover {
        background-color: #F3F4F6;
    }
</style>
""", unsafe_allow_html=True)

# Sample CAS decisions data
cas_decisions = [
    {
        "id": "CAS 2021/A/7876",
        "title": "Football Club X v. Football Association Y",
        "date": "2021-06-15",
        "type": "Appeal",
        "sport": "Football",
        "claimant": "Football Club X",
        "respondent": "Football Association Y",
        "panel": "Prof. Smith (President), Dr. Johnson, Ms. Garcia",
        "summary": "Appeal against a decision of the Disciplinary Committee of Football Association Y regarding a transfer ban.",
        "key_facts": "The club was sanctioned with a three-window transfer ban for breaching regulations on signing youth players.",
        "decision": "The Panel partially upheld the appeal, reducing the transfer ban from three to two transfer windows.",
        "reasoning": "The Panel found that while the violation did occur, the sanction was disproportionate compared to similar cases.",
        "keywords": ["transfer ban", "youth players", "proportionality", "sanctions"],
        "page": 24,
        "line_start": 120,
        "line_end": 450
    },
    {
        "id": "CAS 2022/A/8123",
        "title": "Athlete A v. International Federation B",
        "date": "2022-02-28",
        "type": "Appeal",
        "sport": "Athletics",
        "claimant": "Athlete A",
        "respondent": "International Federation B",
        "panel": "Dr. Garcia (President), Prof. Williams, Mr. Chen",
        "summary": "Appeal against a doping violation finding and four-year suspension.",
        "key_facts": "The athlete tested positive for a prohibited substance and was sanctioned with a four-year suspension.",
        "decision": "The Panel dismissed the appeal and confirmed the four-year suspension.",
        "reasoning": "The Panel found no grounds to reduce the standard sanction as the athlete failed to establish how the substance entered their system.",
        "keywords": ["doping", "prohibited substance", "four-year suspension", "burden of proof"],
        "page": 18,
        "line_start": 85,
        "line_end": 320
    },
    {
        "id": "CAS 2020/O/6789",
        "title": "National Olympic Committee C v. International Olympic Committee",
        "date": "2020-11-10",
        "type": "Ordinary",
        "sport": "Olympic",
        "claimant": "National Olympic Committee C",
        "respondent": "International Olympic Committee",
        "panel": "Prof. Taylor (President), Ms. Rodriguez, Mr. Patel",
        "summary": "Dispute regarding the qualification criteria for the Olympic Games.",
        "key_facts": "The NOC challenged the qualification system implemented by the IOC for the upcoming Olympic Games.",
        "decision": "The Panel ruled in favor of the IOC, finding that the qualification criteria were applied correctly.",
        "reasoning": "The Panel determined that the IOC had acted within its authority and the criteria were objective and non-discriminatory.",
        "keywords": ["qualification criteria", "Olympic Games", "discrimination", "authority"],
        "page": 32,
        "line_start": 210,
        "line_end": 580
    },
    {
        "id": "CAS 2021/A/7991",
        "title": "Athlete X v. International Federation Y - Satellite Collision Case",
        "date": "2021-03-01",
        "type": "Appeal",
        "sport": "Space Athletics",
        "claimant": "Athlete X",
        "respondent": "International Federation Y",
        "panel": "Dr. Smith (President), Prof. Johnson, Ms. Williams",
        "summary": "Appeal regarding the interpretation of satellite collision events during space athletics competition.",
        "key_facts": "The athlete was disqualified following a satellite collision incident during the Space Athletics World Championship.",
        "decision": "The Panel upheld the appeal, finding that the satellite collision was outside the athlete's control.",
        "reasoning": "The Panel determined that the Federation's avoidance system had deficiencies that contributed to the collision.",
        "keywords": ["satellite collision", "space athletics", "avoidance system", "deficiencies"],
        "page": 27,
        "line_start": 350,
        "line_end": 650
    },
    {
        "id": "CAS 2023/A/9012",
        "title": "Football Player Z v. Club W",
        "date": "2023-01-20",
        "type": "Appeal",
        "sport": "Football",
        "claimant": "Football Player Z",
        "respondent": "Club W",
        "panel": "Ms. Johnson (President), Dr. Alvarez, Prof. Kim",
        "summary": "Appeal regarding the termination of a player contract and claim for outstanding salaries.",
        "key_facts": "The player's contract was terminated by the club for alleged misconduct. The player claimed this was unjustified and sought payment of remaining salary.",
        "decision": "The Panel partially upheld the appeal, finding the termination unjustified and awarding partial compensation.",
        "reasoning": "The Panel found insufficient evidence to support the club's allegations of misconduct, but reduced the compensation based on the player's failure to mitigate damages.",
        "keywords": ["contract termination", "player contract", "compensation", "misconduct"],
        "page": 28,
        "line_start": 150,
        "line_end": 490
    },
    {
        "id": "CAS 2021/O/7654",
        "title": "International Federation X v. Athlete Y",
        "date": "2021-09-05",
        "type": "Ordinary",
        "sport": "Swimming",
        "claimant": "International Federation X",
        "respondent": "Athlete Y",
        "panel": "Prof. Brown (President), Dr. Martinez, Ms. Lee",
        "summary": "Proceedings related to an adverse analytical finding in an out-of-competition test.",
        "key_facts": "The athlete tested positive for a prohibited substance but claimed contamination through a supplement.",
        "decision": "The Panel found an anti-doping rule violation and imposed a two-year suspension.",
        "reasoning": "While accepting the contamination theory, the Panel found that the athlete failed to exercise sufficient caution in verifying the supplement ingredients.",
        "keywords": ["doping", "contamination", "supplements", "caution", "verification"],
        "page": 42,
        "line_start": 220,
        "line_end": 620
    },
    {
        "id": "CAS 2022/A/8456",
        "title": "Club P v. Federation Q & Player R",
        "date": "2022-08-15",
        "type": "Appeal",
        "sport": "Basketball",
        "claimant": "Club P",
        "respondent": "Federation Q & Player R",
        "panel": "Dr. Wilson (President), Prof. Black, Ms. Ahmed",
        "summary": "Appeal regarding the validity of a unilateral extension option in a player contract.",
        "key_facts": "The club attempted to exercise a unilateral extension option which the player contested as invalid.",
        "decision": "The Panel ruled that the unilateral extension option was invalid and the player was free to sign with a new club.",
        "reasoning": "The Panel found that the unilateral extension option created a significant imbalance in the parties' rights and obligations, contrary to established CAS jurisprudence.",
        "keywords": ["unilateral extension", "contract validity", "player rights", "freedom of movement"],
        "page": 36,
        "line_start": 180,
        "line_end": 540
    },
    {
        "id": "CAS 2023/A/9234",
        "title": "Athlete M v. Anti-Doping Organization N",
        "date": "2023-03-12",
        "type": "Appeal",
        "sport": "Cycling",
        "claimant": "Athlete M",
        "respondent": "Anti-Doping Organization N",
        "panel": "Prof. Adams (President), Dr. Thompson, Mr. Lopez",
        "summary": "Appeal against a finding of three whereabouts failures within a 12-month period.",
        "key_facts": "The athlete contested the recording of whereabouts failures, arguing procedural irregularities.",
        "decision": "The Panel partially upheld the appeal, invalidating one of the whereabouts failures and setting aside the suspension.",
        "reasoning": "The Panel found that the notification procedure for one of the failures did not comply with the applicable regulations.",
        "keywords": ["whereabouts failures", "procedural compliance", "notification", "filing failure"],
        "page": 30,
        "line_start": 160,
        "line_end": 480
    }
]

# Convert to DataFrame for easier manipulation
df_decisions = pd.DataFrame(cas_decisions)

# Initialize session state
if 'search_history' not in st.session_state:
    st.session_state.search_history = [
        {"query": "satellite collision", "timestamp": "2024-07-14 18:22:42"},
        {"query": "facts related to national security", "timestamp": "2024-07-14 18:20:23"},
        {"query": "tribunal case redoing collision report", "timestamp": "2024-07-13 10:15:18"}
    ]
if 'selected_case' not in st.session_state:
    st.session_state.selected_case = df_decisions.iloc[3]  # Selecting the satellite collision case by default
if 'search_results' not in st.session_state:
    st.session_state.search_results = df_decisions

# Semantic search function
def semantic_search(query):
    if not query or query == "CAS decisions search":
        return df_decisions
    
    # In a real implementation, this would use embeddings or NLP techniques
    # For demonstration, we'll use a more sophisticated keyword matching approach
    
    # Extract query terms and look for semantic matches
    query_terms = query.lower().split()
    
    # Score each decision based on relevance to query terms
    scores = []
    for _, case in df_decisions.iterrows():
        score = 0
        
        # Check various fields for relevance
        text_to_search = (
            case['title'].lower() + " " +
            case['summary'].lower() + " " +
            case['key_facts'].lower() + " " +
            case['decision'].lower() + " " +
            case['reasoning'].lower() + " " +
            " ".join(case['keywords']).lower()
        )
        
        # Direct term matches
        for term in query_terms:
            if term in text_to_search:
                score += 5
        
        # Sports-specific relevance
        if query.lower() in case['sport'].lower():
            score += 10
        
        # Document type relevance
        if ("appeal" in query.lower() and case['type'] == "Appeal") or \
           ("ordinary" in query.lower() and case['type'] == "Ordinary"):
            score += 8
        
        # Satellite collision relevance (prioritize this for the example)
        if "satellite" in query.lower() and "satellite" in text_to_search:
            score += 20
        
        # Collision relevance
        if "collision" in query.lower() and "collision" in text_to_search:
            score += 15
        
        # Security relevance
        if "security" in query.lower() and "security" in text_to_search:
            score += 15
        
        # Keyword matches
        for keyword in case['keywords']:
            if keyword.lower() in query.lower():
                score += 10
        
        scores.append(score)
    
    # Add scores to dataframe
    df_with_scores = df_decisions.copy()
    df_with_scores['relevance_score'] = scores
    
    # Filter and sort by relevance
    relevant_cases = df_with_scores[df_with_scores['relevance_score'] > 0]
    relevant_cases = relevant_cases.sort_values('relevance_score', ascending=False)
    
    if len(relevant_cases) > 0:
        return relevant_cases
    else:
        # If no results, return all cases
        return df_decisions

# Add to search history
def add_to_history(query):
    if query and query != "CAS decisions search":
        # Add new search to history
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if this query is already in history
        exists = False
        for item in st.session_state.search_history:
            if item["query"] == query:
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

# App layout
col1, col2 = st.columns([1, 4])

# Sidebar column
with col1:
    st.markdown("<div class='centered-title'><h2>CASLens</h2></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
    st.markdown("📋 Chronology of Events")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("## History")
    
    # Display search history with radio buttons
    for i, item in enumerate(st.session_state.search_history):
        key = f"history_{i}"
        if st.radio(
            "",
            [item["query"]],
            key=key,
            label_visibility="collapsed",
            index=0 if i == 0 else None
        ):
            st.session_state.search_results = semantic_search(item["query"])
            if not st.session_state.search_results.empty:
                st.session_state.selected_case = st.session_state.search_results.iloc[0]
                
        st.caption(item["timestamp"])
    
    st.markdown("---")
    st.markdown("### Shushan Vaziyan")
    if st.button("Logout"):
        st.write("Logging out...")
    
    st.markdown("Connect with us!")
    social_col1, social_col2, social_col3 = st.columns(3)
    with social_col1:
        st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com)")
    with social_col2:
        st.markdown("[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com)")
    with social_col3:
        st.markdown("[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://facebook.com)")

# Main content column
with col2:
    # Top search bar and generate button
    gen_col, search_col = st.columns([1, 6])
    
    with gen_col:
        if st.button("Generate", key="generate_btn", help="Generate a new CAS decision analysis"):
            st.session_state.search_results = df_decisions
            if not st.session_state.search_results.empty:
                st.session_state.selected_case = st.session_state.search_results.iloc[3]  # Default to satellite collision case
    
    with search_col:
        search_query = st.text_input("", "Processing of satellite collision events", key="search_input")
        if search_query and search_query != "CAS decisions search":
            add_to_history(search_query)
            st.session_state.search_results = semantic_search(search_query)
            if not st.session_state.search_results.empty:
                st.session_state.selected_case = st.session_state.search_results.iloc[0]
    
    # Disclaimer
    st.markdown("""
    <div class="disclaimer">
        <strong>Disclaimer:</strong> CASLens is a fact-finding assistant tool. While it aims to save time, the accuracy of its answers cannot be guaranteed. 
        Users should treat these as initial insights and verify them before making final judgments.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p>General Answer is processing ...</p>", unsafe_allow_html=True)
    
    # Tabs for different views
    tabs = st.tabs(["All", "Claimant", "Respondent", "Tribunal", "BIT"])
    
    with tabs[0]:
        if 'selected_case' in st.session_state:
            case = st.session_state.selected_case
            
            # Case header - specifically styled for the satellite collision case
            st.markdown(f"""
            <div class="case-header">
                Exhibit C-9: DoD Order of 1 March 2021 to Adjust Orbits of 400 km Satellites and Continue to Suspend Operation; page: 27; line(s): 650
            </div>
            """, unsafe_allow_html=True)
            
            # Explanation box
            st.markdown("""
            <div class="explanation">
                <strong>Explanation:</strong> Based on the Department of Defense's investigation of the AS100 satellite collision.
            </div>
            """, unsafe_allow_html=True)
            
            # Highlighted findings for satellite collision case
            st.markdown(f"""
            <div class="selected-highlight">
                Based on the Department of Defense's investigation of the AS100 satellite collision, we have identified both software and hardware deficiencies in the collision avoidance system of the Astra satellites. Regarding the software, the algorithm Astracommex used to predict relies predominantly on data collected by the Space Surveillance Network of Cosmosis. Since the cessation of Cosmosis-Celestria diplomatic relations, Celestria has shut down all of Cosmosis' terrestrial radar operations within Celestria's borders, coupled with subsequent national security regulations prohibiting sensitive data transfer to Cosmosis. These measures have significantly impacted Cosmosis' Space Surveillance Network's accuracy on Celestria related space activities.
            </div>
            """, unsafe_allow_html=True)
            
            # Statement of uncontested facts
            st.markdown("""
            <div style="margin-top: 20px; margin-bottom: 10px;">
                <strong>STATEMENT OF UNCONTESTED FACTS; page: 82; line(s): 2050</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Second explanation box
            st.markdown("""
            <div class="explanation">
                <strong>Explanation:</strong> Processing of satellite collision events involves assessing damage, analyzing data, and preparing software updates.
            </div>
            """, unsafe_allow_html=True)
            
            # Case details specifically for satellite collision case
            st.markdown(f"""
            <div style="margin-top: 20px;">
                <strong>37.</strong> On 2 October 2020, the NFA requested additional documentation from Astracommex Regional to specifically address these atmospheric concerns. On 15 October 2020, Astracommex Regional responded to the NFA, declining to provide the requested supplementary information. On 15 December 2020, the NFA rejected Astracommex Regional's application to Ku-band frequencies on the basis of the NEPA
            </div>
            """, unsafe_allow_html=True)
            
            # Case outcome specifically for satellite collision case
            st.markdown(f"""
            <div class="highlight" style="margin-top: 20px;">
                <strong>38.</strong> On 1 January 2021, one of Astracommex Regional's satellites, AS100, collided with a cube satellite (cubesat) that wandered around the adjacent orbit on a crossed orbital plate. The cube satellite was run by Valinor, a private company, in partnership with Celestria's Department of Defense ("DoD"). The cubesat was not equipped with any collision avoidance system and was smashed into small debris upon collision. AS100 was partially damaged – but both its Telemetry, Tracking, and Command (TT&C) system and its communication system ceased to function. The data up until the impact moment indicated an anomaly in the radiation values that was transmitted and subsequently used by Astracommex's collision avoidance system.
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[1]:
        st.markdown(f"<h3>Claimant: {st.session_state.selected_case['claimant']}</h3>", unsafe_allow_html=True)
        st.markdown(f"Case initiated on: {st.session_state.selected_case['date']}")
        st.markdown("Claimant's key arguments:")
        st.markdown("• " + st.session_state.selected_case['key_facts'])
        st.markdown("• The satellite collision was due to external factors outside claimant's control")
        st.markdown("• The cubesat operated by Valinor lacked proper collision avoidance systems")
        st.markdown("• Data anomalies in radiation values contributed to the collision")
    
    with tabs[2]:
        st.markdown(f"<h3>Respondent: {st.session_state.selected_case['respondent']}</h3>", unsafe_allow_html=True)
        st.markdown("Respondent's key arguments:")
        st.markdown("• Defense based on applicable space regulations")
        st.markdown("• Alleged that the claimant failed to maintain proper collision avoidance systems")
        st.markdown("• Contested the claimant's interpretation of the satellite collision events")
        st.markdown("• Data transmission failures were the responsibility of the satellite operator")
    
    with tabs[3]:
        st.markdown("<h3>Tribunal</h3>", unsafe_allow_html=True)
        st.markdown(f"<strong>Panel Composition:</strong> {st.session_state.selected_case['panel']}", unsafe_allow_html=True)
        st.markdown("<strong>Key Findings:</strong>", unsafe_allow_html=True)
        st.markdown("• The Panel determined that software and hardware deficiencies existed in the collision avoidance system")
        st.markdown("• Diplomatic relations between Cosmosis and Celestria impacted data sharing")
        st.markdown("• National security regulations prohibited sensitive data transfer")
        st.markdown("• The cubesat lacked collision avoidance capabilities")
        st.markdown("<strong>Procedural Timeline:</strong>", unsafe_allow_html=True)
        st.markdown("• 2 October 2020: NFA requested documentation from Astracommex")
        st.markdown("• 15 October 2020: Astracommex declined to provide information")
        st.markdown("• 15 December 2020: NFA rejected Astracommex's application")
        st.markdown("• 1 January 2021: Satellite collision occurred")
        st.markdown("• 1 March 2021: DoD ordered adjustment of satellite orbits")
    
    with tabs[4]:
        st.markdown("<h3>Relevant Legal Principles</h3>", unsafe_allow_html=True)
        st.markdown("• Space debris mitigation guidelines")
        st.markdown("• Satellite operator responsibility")
        st.markdown("• Orbital slot allocation regulations")
        st.markdown("• International space law obligations")
        st.markdown("<h3>References to Previous CAS Jurisprudence</h3>", unsafe_allow_html=True)
        st.markdown("• CAS 2018/A/5211 - Orbital Communications Inc. v. Space Regulatory Authority")
        st.markdown("• CAS 2019/O/6310 - International Space Standards Association v. Satellite Operator X")
        st.markdown("• CAS 2020/A/7001 - Space Technology Corp v. International Telecommunications Union")
