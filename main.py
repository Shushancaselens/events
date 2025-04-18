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
    .stButton>button {background-color: #4F46E5; color: white;}
    .stTextInput>div>div>input {border-radius: 5px;}
    .stTabs [data-baseweb="tab-list"] {gap: 2px;}
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5;
        color: white;
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
        {"query": "transfer ban", "timestamp": "2024-04-18 15:32:42"},
        {"query": "doping violation", "timestamp": "2024-04-18 14:20:23"},
        {"query": "qualification criteria", "timestamp": "2024-04-17 09:45:18"}
    ]
if 'selected_case' not in st.session_state:
    st.session_state.selected_case = df_decisions.iloc[0]
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
        
        # Doping-related relevance
        if "doping" in query.lower() and ("doping" in text_to_search or "prohibited substance" in text_to_search):
            score += 15
        
        # Contract-related relevance
        if "contract" in query.lower() and "contract" in text_to_search:
            score += 15
        
        # Olympic-related relevance
        if "olympic" in query.lower() and "olympic" in text_to_search:
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
    cols
