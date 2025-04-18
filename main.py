import streamlit as st
import pandas as pd
from datetime import datetime
import random

# Set page configuration
st.set_page_config(
    page_title="CASLens - Sports Arbitration Search",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with better UI structure and visual hierarchy
st.markdown("""
<style>
    /* Base styles and typography */
    * {
        font-family: 'Inter', sans-serif;
        box-sizing: border-box;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        color: #1F2937;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
    }
    
    /* Logo area */
    .logo-container {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #E5E7EB;
    }
    
    .logo {
        font-size: 28px;
        font-weight: 700;
        color: #4F46E5;
        letter-spacing: -0.025em;
    }
    
    /* Cards and content containers */
    .content-card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .sidebar-card {
        background-color: #F9FAFB;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
    }
    
    /* Search components */
    .search-container {
        display: flex;
        align-items: center;
        background-color: white;
        border-radius: 8px;
        padding: 0.5rem;
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    
    .status-active {
        background-color: #10B981;
    }
    
    .status-pending {
        background-color: #F59E0B;
    }
    
    /* Case display */
    .case-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.5rem;
    }
    
    .case-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-bottom: 1rem;
        font-size: 0.875rem;
    }
    
    .case-meta-item {
        color: #4B5563;
        background-color: #F3F4F6;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
    }
    
    /* Message boxes */
    .disclaimer {
        background-color: #FEF2F2;
        border-left: 4px solid #DC2626;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
        color: #991B1B;
    }
    
    .explanation {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    
    .highlight {
        background-color: #ECFDF5;
        border-left: 4px solid #10B981;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    
    .selected-highlight {
        background-color: #F3F4F6;
        border-left: 4px solid #4F46E5;
        padding: 1rem;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    
    /* Tags and chips */
    .tag {
        display: inline-block;
        background-color: #E5E7EB;
        color: #374151;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Timeline components */
    .timeline {
        position: relative;
        padding-left: 2rem;
        margin-bottom: 1rem;
    }
    
    .timeline::before {
        content: "";
        position: absolute;
        left: 0;
        top: 6px;
        bottom: 0;
        width: 2px;
        background-color: #E5E7EB;
    }
    
    .timeline-item {
        position: relative;
        padding-bottom: 1.5rem;
    }
    
    .timeline-item::before {
        content: "";
        position: absolute;
        left: -2rem;
        top: 6px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #4F46E5;
    }
    
    /* Buttons and interactive elements */
    .primary-button {
        background-color: #4F46E5;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        cursor: pointer;
    }
    
    .primary-button:hover {
        background-color: #4338CA;
    }
    
    .secondary-button {
        background-color: white;
        color: #374151;
        border: 1px solid #D1D5DB;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        cursor: pointer;
    }
    
    .secondary-button:hover {
        background-color: #F9FAFB;
    }
    
    /* Custom Streamlit component styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom styling for sidebar */
    .sidebar .sidebar-content {
        background-color: #F9FAFB;
    }
    
    /* Search history styling */
    .history-item {
        padding: 0.75rem;
        border-radius: 4px;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .history-item:hover {
        background-color: #F3F4F6;
    }
    
    .history-item.active {
        background-color: #EFF6FF;
        border-left: 3px solid #4F46E5;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #F9FAFB;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 0.5rem 0 0.5rem;
        border: 1px solid #E5E7EB;
        border-bottom: none;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #F3F4F6;
        border-radius: 6px 6px 0 0;
        padding: 0.5rem 1rem;
        margin-right: 2px;
        color: #4B5563;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #4F46E5 !important;
        border-top: 3px solid #4F46E5;
        border-bottom: none;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 1rem;
    }
    
    /* Radio styling for history items */
    .stRadio > div {
        padding: 0;
    }
    
    .stRadio > div > div {
        border-radius: 4px;
        transition: background-color 0.2s;
    }
    
    .stRadio > div > div:hover {
        background-color: #F3F4F6;
    }
    
    .stRadio > div > div > label {
        padding: 0.5rem 0.75rem;
        width: 100%;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #4F46E5 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
    }
    
    .stButton > button:hover {
        background-color: #4338CA !important;
    }
    
    /* Search input styling */
    .stTextInput > div > div > input {
        border-radius: 4px;
        border: 1px solid #D1D5DB;
        padding: 0.5rem 1rem;
    }
    
    /* Add additional padding and styling to improve the layout */
    .content-section {
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Scrollable containers */
    .scrollable-container {
        max-height: 400px;
        overflow-y: auto;
        padding-right: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Social media icons */
    .social-media-container {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load fonts and custom header
st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
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
        "line_end": 450,
        "status": "Decided"
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
        "line_end": 320,
        "status": "Decided"
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
        "line_end": 580,
        "status": "Decided"
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
        "line_end": 650,
        "status": "Decided"
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
        "line_end": 490,
        "status": "Decided"
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
        "line_end": 620,
        "status": "Decided"
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
        "line_end": 540,
        "status": "Decided"
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
        "line_end": 480,
        "status": "Decided"
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
if 'active_history_index' not in st.session_state:
    st.session_state.active_history_index = 0
if 'filters' not in st.session_state:
    st.session_state.filters = {
        "case_type": "All",
        "sport": "All",
        "date_range": (datetime(2020, 1, 1), datetime(2024, 12, 31))
    }

# Semantic search function with improved relevance scoring
def semantic_search(query, filters=None):
    if not query or query == "CAS decisions search":
        filtered_df = df_decisions
    else:
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
            
            # Direct term matches with varying weights
            for term in query_terms:
                if term in case['title'].lower():
                    score += 8  # Title matches are highly relevant
                if term in case['summary'].lower():
                    score += 6  # Summary matches are very relevant
                if term in case['key_facts'].lower():
                    score += 5  # Key facts matches are relevant
                if term in case['decision'].lower() or term in case['reasoning'].lower():
                    score += 4  # Decision and reasoning matches are somewhat relevant
            
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
                elif any(term in keyword.lower() for term in query_terms):
                    score += 7
            
            scores.append(score)
        
        # Add scores to dataframe
        df_with_scores = df_decisions.copy()
        df_with_scores['relevance_score'] = scores
        
        # Filter and sort by relevance
        filtered_df = df_with_scores[df_with_scores['relevance_score'] > 0]
        filtered_df = filtered_df.sort_values('relevance_score', ascending=False)
        
        if len(filtered_df) == 0:
            # If no results, return all cases
            filtered_df = df_decisions
    
    # Apply additional filters if provided
    if filters:
        if filters.get("case_type") and filters.get("case_type") != "All":
            filtered_df = filtered_df[filtered_df['type'] == filters.get("case_type")]
        
        if filters.get("sport") and filters.get("sport") != "All":
            filtered_df = filtered_df[filtered_df['sport'] == filters.get("sport")]
        
        if filters.get("date_range"):
            start_date, end_date = filters.get("date_range")
            filtered_df = filtered_df[
                (pd.to_datetime(filtered_df['date']) >= start_date) & 
                (pd.to_datetime(filtered_df['date']) <= end_date)
            ]
    
    return filtered_df

# Add to search history
def add_to_history(query):
    if query and query != "CAS decisions search":
        # Add new search to history
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if this query is already in history
        exists = False
        for i, item in enumerate(st.session_state.search_history):
            if item["query"] == query:
                exists = True
                # Update timestamp and move to top
                item["timestamp"] = formatted_time
                st.session_state.search_history.remove(item)
                st.session_state.search_history.insert(0, item)
                st.session_state.active_history_index = 0
                break
        
        # If not in history, add it
        if not exists:
            st.session_state.search_history.insert(0, {"query": query, "timestamp": formatted_time})
            st.session_state.active_history_index = 0
            # Keep only the most recent 10 searches
            if len(st.session_state.search_history) > 10:
                st.session_state.search_history = st.session_state.search_history[:10]

# Select a case from history
def select_history_item(index):
    st.session_state.active_history_index = index
    query = st.session_state.search_history[index]["query"]
    st.session_state.search_results = semantic_search(query, st.session_state.filters)
    if not st.session_state.search_results.empty:
        st.session_state.selected_case = st.session_state.search_results.iloc[0]

# Format date for display
def format_date(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d %b %Y")

# Create a collapsible section
def collapsible_section(title, content, open_by_default=True):
    with st.expander(title, expanded=open_by_default):
        st.markdown(content, unsafe_allow_html=True)

# App layout with better structure
col1, col2 = st.columns([1, 3])

# Sidebar with improved visual hierarchy
with col1:
    # Logo and branding
    st.markdown("""
    <div class="logo-container">
        <div class="logo">⚖️ CASLens</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Advanced search section
    st.markdown("<h4>Advanced Filters</h4>", unsafe_allow_html=True)
    
    with st.form("search_filters", clear_on_submit=False):
        # Case type filter
        case_type = st.selectbox(
            "Case Type",
            ["All", "Appeal", "Ordinary"],
            index=0
        )
        
        # Sport filter
        all_sports = ["All"] + sorted(df_decisions["sport"].unique().tolist())
        sport = st.selectbox(
            "Sport",
            all_sports,
            index=0
        )
        
        # Date range filter
        date_range = st.date_input(
            "Date Range",
            value=(datetime(2020, 1, 1), datetime(2024, 12, 31)),
            format="YYYY-MM-DD"
        )
        
        # Apply filters button
        if st.form_submit_button("Apply Filters"):
            st.session_state.filters = {
                "case_type": case_type,
                "sport": sport,
                "date_range": date_range if isinstance(date_range, tuple) else (date_range, date_range)
            }
            # Re-run search with current query and new filters
            if st.session_state.search_history:
                current_query = st.session_state.search_history[st.session_state.active_history_index]["query"]
                st.session_state.search_results = semantic_search(current_query, st.session_state.filters)
                if not st.session_state.search_results.empty:
                    st.session_state.selected_case = st.session_state.search_results.iloc[0]
    
    # Search history with improved styling
    st.markdown("<h4>Search History</h4>", unsafe_allow_html=True)
    
    for i, item in enumerate(st.session_state.search_history):
        active_class = "active" if i == st.session_state.active_history_index else ""
        st.markdown(f"""
        <div class="history-item {active_class}" onclick="this.onclick=null; window.location.reload();">
            <div style="font-weight: 500;">{item["query"]}</div>
            <div style="font-size: 0.75rem; color: #6B7280; margin-top: 0.25rem;">{item["timestamp"]}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Hidden radio button for selection
        if st.radio(
            "",
            [item["query"]],
            key=f"history_{i}",
            label_visibility="collapsed",
            horizontal=True,
            index=0 if i == st.session_state.active_history_index else None
        ):
            select_history_item(i)
    
    # User profile section
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-top: 1rem;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <div style="width: 32px; height: 32px; border-radius: 16px; background-color: #4F46E5; color: white; display: flex; align-items: center; justify-content: center; margin-right: 0.5rem; font-weight: 600;">SV</div>
            <div style="font-weight: 500;">Shushan Vaziyan</div>
        </div>
        <div style="font-size: 0.875rem; color: #6B7280; margin-bottom: 1rem;">Premium Account</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Logout", key="logout_btn"):
        st.info("Logging out... (simulation)")
    
    # Social media links with improved styling
    st.markdown("<div class='social-media-container'>", unsafe_allow_html=True)
    st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com)")
    st.markdown("[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com)")
    st.markdown("[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://facebook.com)")
    st.markdown("</div>", unsafe_allow_html=True)

# Main content area with improved layout and components
with col2:
    # Top search and controls bar
    st.markdown("<div class='search-container'>", unsafe_allow_html=True)
    
    gen_col, search_col, search_btn_col = st.columns([1, 5, 1])
    
    with gen_col:
        if st.button("Generate", key="generate_btn", help="Generate a new CAS decision analysis"):
            st.session_state.search_results = df_decisions
            if not st.session_state.search_results.empty:
                st.session_state.selected_case = st.session_state.search_results.iloc[3]  # Default to satellite collision case
    
    with search_col:
        search_query = st.text_input("", "Processing of satellite collision events", key="search_input", 
                                     placeholder="Search CAS decisions...")
    
    with search_btn_col:
        if st.button("Search", key="search_btn"):
            if search_query and search_query != "CAS decisions search":
                add_to_history(search_query)
                st.session_state.search_results = semantic_search(search_query, st.session_state.filters)
                if not st.session_state.search_results.empty:
                    st.session_state.selected_case = st.session_state.search_results.iloc[0]
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Disclaimer with improved styling
    st.markdown("""
    <div class="disclaimer">
        <strong>Disclaimer:</strong> CASLens is a fact-finding assistant tool. While it aims to save time, the accuracy of its answers cannot be guaranteed. 
        Users should treat these as initial insights and verify them before making final judgments.
    </div>
    """, unsafe_allow_html=True)
    
    # Status indicator
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <div class="status-indicator status-active"></div>
        <div style="font-size: 0.875rem; color: #6B7280;">General Answer is processing...</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main tabs with improved styling
    tabs = st.tabs(["All", "Claimant", "Respondent", "Tribunal", "BIT"])
    
    with tabs[0]:
        if 'selected_case' in st.session_state:
            case = st.session_state.selected_case
            
            # Case header with improved styling
            st.markdown(f"""
            <div class="content-card">
                <div class="case-title">Exhibit C-9: DoD Order of 1 March 2021 to Adjust Orbits of 400 km Satellites and Continue to Suspend Operation</div>
                <div class="case-meta">
                    <div class="case-meta-item">Page: 27</div>
                    <div class="case-meta-item">Line(s): 650</div>
                    <div class="case-meta-item">Case ID: {case['id']}</div>
                    <div class="case-meta-item">Date: {format_date(case['date'])}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Explanation box with improved styling
            st.markdown("""
            <div class="explanation">
                <strong>Explanation:</strong> Based on the Department of Defense's investigation of the AS100 satellite collision.
            </div>
            """, unsafe_allow_html=True)
            
            # Highlighted findings with improved styling
            st.markdown(f"""
            <div class="selected-highlight">
                <h4>Key Findings</h4>
                <p>
                    Based on the Department of Defense's investigation of the AS100 satellite collision, we have identified both software and hardware deficiencies in the collision avoidance system of the Astra satellites. Regarding the software, the algorithm Astracommex used to predict relies predominantly on data collected by the Space Surveillance Network of Cosmosis.
                </p>
                <p>
                    Since the cessation of Cosmosis-Celestria diplomatic relations, Celestria has shut down all of Cosmosis' terrestrial radar operations within Celestria's borders, coupled with subsequent national security regulations prohibiting sensitive data transfer to Cosmosis. These measures have significantly impacted Cosmosis' Space Surveillance Network's accuracy on Celestria related space activities.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Statement of uncontested facts with improved styling
            st.markdown("""
            <div class="content-card">
                <h4>STATEMENT OF UNCONTESTED FACTS</h4>
                <div class="case-meta" style="margin-bottom: 1rem;">
                    <div class="case-meta-item">Page: 82</div>
                    <div class="case-meta-item">Line(s): 2050</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Second explanation box with improved styling
            st.markdown("""
                <div class="explanation">
                    <strong>Explanation:</strong> Processing of satellite collision events involves assessing damage, analyzing data, and preparing software updates.
                </div>
            """, unsafe_allow_html=True)
            
            # Timeline of events with improved styling
            st.markdown("""
                <div class="timeline">
                    <div class="timeline-item">
                        <strong>2 October 2020</strong>
                        <p>The NFA requested additional documentation from Astracommex Regional to specifically address these atmospheric concerns.</p>
                    </div>
                    <div class="timeline-item">
                        <strong>15 October 2020</strong>
                        <p>Astracommex Regional responded to the NFA, declining to provide the requested supplementary information.</p>
                    </div>
                    <div class="timeline-item">
                        <strong>15 December 2020</strong>
                        <p>The NFA rejected Astracommex Regional's application to Ku-band frequencies on the basis of the NEPA.</p>
                    </div>
                    <div class="timeline-item">
                        <strong>1 January 2021</strong>
                        <p>One of Astracommex Regional's satellites, AS100, collided with a cube satellite (cubesat) that wandered around the adjacent orbit on a crossed orbital plate.</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Case outcome with improved styling
            st.markdown(f"""
                <div class="highlight">
                    <h4>Key Event: Satellite Collision</h4>
                    <p>
                        On 1 January 2021, one of Astracommex Regional's satellites, AS100, collided with a cube satellite (cubesat) that wandered around the adjacent orbit on a crossed orbital plate. The cube satellite was run by Valinor, a private company, in partnership with Celestria's Department of Defense ("DoD").
                    </p>
                    <p>
                        The cubesat was not equipped with any collision avoidance system and was smashed into small debris upon collision. AS100 was partially damaged – but both its Telemetry, Tracking, and Command (TT&C) system and its communication system ceased to function.
                    </p>
                    <p>
                        The data up until the impact moment indicated an anomaly in the radiation values that was transmitted and subsequently used by Astracommex's collision avoidance system.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Related cases section
            st.markdown("""
            <div class="content-card">
                <h4>Related Cases</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
            """, unsafe_allow_html=True)
            
            # Generate some related cases
            related_cases = df_decisions[df_decisions['id'] != case['id']].sample(min(3, len(df_decisions)-1))
            for _, related_case in related_cases.iterrows():
                st.markdown(f"""
                    <div style="flex: 1; min-width: 250px; padding: 0.75rem; border: 1px solid #E5E7EB; border-radius: 4px;">
                        <div style="font-weight: 500; margin-bottom: 0.25rem;">{related_case['id']}</div>
                        <div style="font-size: 0.875rem; color: #4B5563; margin-bottom: 0.5rem;">{related_case['title']}</div>
                        <div style="font-size: 0.75rem; color: #6B7280;">{format_date(related_case['date'])}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tabs[1]:
        # Claimant tab with improved layout
        st.markdown("""
        <div class="content-card">
            <h3>Claimant Information</h3>
        """, unsafe_allow_html=True)
        
        case = st.session_state.selected_case
        st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 40px; height: 40px; border-radius: 20px; background-color: #E0F2FE; color: #0369A1; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 1.25rem;">C</div>
                    <div style="font-size: 1.25rem; font-weight: 500;">{case['claimant']}</div>
                </div>
                <div style="margin-top: 0.5rem; color: #6B7280; font-size: 0.875rem;">Case initiated on: {format_date(case['date'])}</div>
            </div>
            
            <h4>Key Arguments</h4>
            <ul style="padding-left: 1.5rem;">
                <li>{case['key_facts']}</li>
                <li>The satellite collision was due to external factors outside claimant's control</li>
                <li>The cubesat operated by Valinor lacked proper collision avoidance systems</li>
                <li>Data anomalies in radiation values contributed to the collision</li>
            </ul>
            
            <h4>Relief Sought</h4>
            <ul style="padding-left: 1.5rem;">
                <li>Declaration that the claimant is not liable for the satellite collision</li>
                <li>Order for the respondent to cover costs of the proceedings</li>
                <li>Reinstatement of operational permits without penalties</li>
            </ul>
            
            <h4>Evidence Submitted</h4>
            <div class="timeline">
                <div class="timeline-item">
                    <strong>Exhibit C-1</strong>
                    <p>Technical specifications of the AS100 satellite and its collision avoidance system</p>
                </div>
                <div class="timeline-item">
                    <strong>Exhibit C-2</strong>
                    <p>Data logs from the satellite's tracking system prior to the collision</p>
                </div>
                <div class="timeline-item">
                    <strong>Exhibit C-3</strong>
                    <p>Expert report on the radiation anomalies detected before impact</p>
                </div>
                <div class="timeline-item">
                    <strong>Exhibit C-4</strong>
                    <p>Documentation of previous diplomatic communications regarding data sharing</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tabs[2]:
        # Respondent tab with improved layout
        st.markdown("""
        <div class="content-card">
            <h3>Respondent Information</h3>
        """, unsafe_allow_html=True)
        
        case = st.session_state.selected_case
        st.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <div style="width: 40px; height: 40px; border-radius: 20px; background-color: #FEF3C7; color: #B45309; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 1.25rem;">R</div>
                    <div style="font-size: 1.25rem; font-weight: 500;">{case['respondent']}</div>
                </div>
            </div>
            
            <h4>Key Arguments</h4>
            <ul style="padding-left: 1.5rem;">
                <li>Defense based on applicable space regulations</li>
                <li>Alleged that the claimant failed to maintain proper collision avoidance systems</li>
                <li>Contested the claimant's interpretation of the satellite collision events</li>
                <li>Data transmission failures were the responsibility of the satellite operator</li>
            </ul>
            
            <h4>Relief Sought</h4>
            <ul style="padding-left: 1.5rem;">
                <li>Dismissal of all claims</li>
                <li>Declaration that the claimant is liable for the damages to the cubesat</li>
                <li>Order for the claimant to cover costs of the proceedings</li>
                <li>Imposition of additional safety requirements for future operations</li>
            </ul>
            
            <h4>Evidence Submitted</h4>
            <div class="timeline">
                <div class="timeline-item">
                    <strong>Exhibit R-1</strong>
                    <p>Technical assessment of the collision avoidance system's deficiencies</p>
                </div>
                <div class="timeline-item">
                    <strong>Exhibit R-2</strong>
                    <p>Analysis of the debris field and damage assessment</p>
                </div>
                <div class="timeline-item">
                    <strong>Exhibit R-3</strong>
                    <p>Expert report on industry standard collision avoidance protocols</p>
                </div>
                <div class="timeline-item">
                    <strong>Exhibit R-4</strong>
                    <p>Documentation of similar incidents involving Astracommex systems</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tabs[3]:
        # Tribunal tab with improved layout
        st.markdown("""
        <div class="content-card">
            <h3>Tribunal</h3>
        """, unsafe_allow_html=True)
        
        case = st.session_state.selected_case
        st.markdown(f"""
            <div style="background-color: #F9FAFB; padding: 1rem; border-radius: 4px; margin-bottom: 1rem;">
                <h4>Panel Composition</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 0.5rem;">
                    <div style="flex: 1; min-width: 200px;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div style="width: 32px; height: 32px; border-radius: 16px; background-color: #4F46E5; color: white; display: flex; align-items: center; justify-content: center; font-weight: 600;">P</div>
                            <div>
                                <div style="font-weight: 500;">Dr. Smith</div>
                                <div style="font-size: 0.75rem; color: #6B7280;">President</div>
                            </div>
                        </div>
                    </div>
                    <div style="flex: 1; min-width: 200px;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div style="width: 32px; height: 32px; border-radius: 16px; background-color: #4F46E5; color: white; display: flex; align-items: center; justify-content: center; font-weight: 600;">A</div>
                            <div>
                                <div style="font-weight: 500;">Prof. Johnson</div>
                                <div style="font-size: 0.75rem; color: #6B7280;">Arbitrator</div>
                            </div>
                        </div>
                    </div>
                    <div style="flex: 1; min-width: 200px;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div style="width: 32px; height: 32px; border-radius: 16px; background-color: #4F46E5; color: white; display: flex; align-items: center; justify-content: center; font-weight: 600;">A</div>
                            <div>
                                <div style="font-weight: 500;">Ms. Williams</div>
                                <div style="font-size: 0.75rem; color: #6B7280;">Arbitrator</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <h4>Key Findings</h4>
            <div class="selected-highlight" style="margin-bottom: 1rem;">
                <ul style="padding-left: 1.5rem; margin: 0;">
                    <li>The Panel determined that software and hardware deficiencies existed in the collision avoidance system</li>
                    <li>Diplomatic relations between Cosmosis and Celestria impacted data sharing</li>
                    <li>National security regulations prohibited sensitive data transfer</li>
                    <li>The cubesat lacked collision avoidance capabilities</li>
                </ul>
            </div>
            
            <h4>Decision</h4>
            <div class="highlight" style="margin-bottom: 1rem;">
                <p>{case['decision']}</p>
            </div>
            
            <h4>Reasoning</h4>
            <p>{case['reasoning']}</p>
            
            <h4>Procedural Timeline</h4>
            <div class="timeline">
                <div class="timeline-item">
                    <strong>2 October 2020</strong>
                    <p>NFA requested documentation from Astracommex</p>
                </div>
                <div class="timeline-item">
                    <strong>15 October 2020</strong>
                    <p>Astracommex declined to provide information</p>
                </div>
                <div class="timeline-item">
                    <strong>15 December 2020</strong>
                    <p>NFA rejected Astracommex's application</p>
                </div>
                <div class="timeline-item">
                    <strong>1 January 2021</strong>
                    <p>Satellite collision occurred</p>
                </div>
                <div class="timeline-item">
                    <strong>1 March 2021</strong>
                    <p>DoD ordered adjustment of satellite orbits</p>
                </div>
                <div class="timeline-item">
                    <strong>15 April 2021</strong>
                    <p>Claimant filed appeal with CAS</p>
                </div>
                <div class="timeline-item">
                    <strong>2 June 2021</strong>
                    <p>Hearing held at CAS headquarters</p>
                </div>
                <div class="timeline-item">
                    <strong>30 July 2021</strong>
                    <p>Decision rendered by the Panel</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with tabs[4]:
        # BIT (Background, Interpretation, and Theory) tab with improved layout
        st.markdown("""
        <div class="content-card">
            <h3>Legal Framework & Jurisprudence</h3>
            
            <div style="display: flex; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem;">
                <div style="flex: 1; min-width: 250px;">
                    <h4>Relevant Legal Principles</h4>
                    <ul style="padding-left: 1.5rem;">
                        <li>Space debris mitigation guidelines</li>
                        <li>Satellite operator responsibility</li>
                        <li>Orbital slot allocation regulations</li>
                        <li>International space law obligations</li>
                        <li>Force majeure in space operations</li>
                    </ul>
                </div>
                
                <div style="flex: 1; min-width: 250px;">
                    <h4>Applicable Regulations</h4>
                    <ul style="padding-left: 1.5rem;">
                        <li>Outer Space Treaty, Art. IX</li>
                        <li>Space Debris Mitigation Guidelines</li>
                        <li>ITU Radio Regulations</li>
                        <li>National Space Policy Directive 3</li>
                        <li>Satellite Operator Certification Standards</li>
                    </ul>
                </div>
            </div>
            
            <h4>Precedent Cases</h4>
            <div class="scrollable-container">
                <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                    <div style="padding: 0.75rem; border: 1px solid #E5E7EB; border-radius: 4px;">
                        <div style="font-weight: 500; margin-bottom: 0.25rem;">CAS 2018/A/5211</div>
                        <div style="font-size: 0.875rem; margin-bottom: 0.25rem;">Orbital Communications Inc. v. Space Regulatory Authority</div>
                        <div style="font-size: 0.75rem; color: #6B7280; margin-bottom: 0.5rem;">15 June 2018</div>
                        <div style="font-size: 0.875rem;">Established the principle that satellite operators bear primary responsibility for collision avoidance regardless of data availability from third parties.</div>
                    </div>
                    
                    <div style="padding: 0.75rem; border: 1px solid #E5E7EB; border-radius: 4px;">
                        <div style="font-weight: 500; margin-bottom: 0.25rem;">CAS 2019/O/6310</div>
                        <div style="font-size: 0.875rem; margin-bottom: 0.25rem;">International Space Standards Association v. Satellite Operator X</div>
                        <div style="font-size: 0.75rem; color: #6B7280; margin-bottom: 0.5rem;">22 November 2019</div>
                        <div style="font-size: 0.875rem;">Defined minimum technical requirements for collision avoidance systems in commercial satellites.</div>
                    </div>
                    
                    <div style="padding: 0.75rem; border: 1px solid #E5E7EB; border-radius: 4px;">
                        <div style="font-weight: 500; margin-bottom: 0.25rem;">CAS 2020/A/7001</div>
                        <div style="font-size: 0.875rem; margin-bottom: 0.25rem;">Space Technology Corp v. International Telecommunications Union</div>
                        <div style="font-size: 0.75rem; color: #6B7280; margin-bottom: 0.5rem;">7 March 2020</div>
                        <div style="font-size: 0.875rem;">Addressed the issue of data sharing between competing satellite operators and regulatory bodies.</div>
                    </div>
                </div>
            </div>
            
            <h4>Key Legal Interpretations</h4>
            <div class="explanation" style="margin-top: 1rem;">
                <p>
                    The Panel has interpreted Article IX of the Outer Space Treaty to require that satellite operators implement redundant collision avoidance systems that do not rely exclusively on data from a single source. The Panel found that the diplomatic tensions between states cannot be used as a valid defense for failing to maintain adequate collision avoidance capabilities.
                </p>
                <p>
                    While acknowledging that the cubesat operated by Valinor lacked collision avoidance systems, the Panel held that this does not absolve the primary satellite operator (Astracommex) from its duty to maintain functional avoidance systems for all potential collision scenarios, including those involving non-maneuverable objects.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Additional section with case statistics
    st.markdown("""
    <div class="content-card" style="margin-top: 1rem;">
        <h4>Case Statistics</h4>
        <div style="display: flex; flex-wrap: wrap; gap: 1rem;">
            <div style="flex: 1; min-width: 200px; text-align: center; padding: 1rem; background-color: #F3F4F6; border-radius: 4px;">
                <div style="font-size: 2rem; font-weight: 600; color: #4F46E5;">82</div>
                <div style="font-size: 0.875rem; color: #6B7280;">Pages</div>
            </div>
            <div style="flex: 1; min-width: 200px; text-align: center; padding: 1rem; background-color: #F3F4F6; border-radius: 4px;">
                <div style="font-size: 2rem; font-weight: 600; color: #4F46E5;">12</div>
                <div style="font-size: 0.875rem; color: #6B7280;">Exhibits</div>
            </div>
            <div style="flex: 1; min-width: 200px; text-align: center; padding: 1rem; background-color: #F3F4F6; border-radius: 4px;">
                <div style="font-size: 2rem; font-weight: 600; color: #4F46E5;">4</div>
                <div style="font-size: 0.875rem; color: #6B7280;">Expert Witnesses</div>
            </div>
            <div style="flex: 1; min-width: 200px; text-align: center; padding: 1rem; background-color: #F3F4F6; border-radius: 4px;">
                <div style="font-size: 2rem; font-weight: 600; color: #4F46E5;">147</div>
                <div style="font-size: 0.875rem; color: #6B7280;">Days Duration</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
