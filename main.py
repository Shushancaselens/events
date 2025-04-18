import streamlit as st
import pandas as pd
from datetime import datetime
import random

# Set page configuration
st.set_page_config(
    page_title="CASLens",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for minimal styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #F9FAFB;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #F3F4F6;
        border-radius: 4px 4px 0 0;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4F46E5;
        color: white !important;
    }
    
    div.stButton > button {
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
        {"query": "transfer ban", "timestamp": "2024-07-14 18:22:42"},
        {"query": "doping violation", "timestamp": "2024-07-14 18:20:23"},
        {"query": "contract termination", "timestamp": "2024-07-13 10:15:18"}
    ]
if 'selected_case' not in st.session_state:
    st.session_state.selected_case = random.choice(df_decisions.to_dict('records'))
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
                if term in text_to_search:
                    score += 2  # General text match
            
            # Sports-specific relevance
            if query.lower() in case['sport'].lower():
                score += 10
            
            # Document type relevance
            if ("appeal" in query.lower() and case['type'] == "Appeal") or \
               ("ordinary" in query.lower() and case['type'] == "Ordinary"):
                score += 8
            
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
        st.session_state.selected_case = st.session_state.search_results.iloc[0].to_dict()

# Format date for display
def format_date(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d %b %Y")

# App layout with improved structure and native Streamlit components
col1, col2 = st.columns([1, 3])

# Sidebar with native Streamlit components
with col1:
    st.subheader("Advanced Filters")
    
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
                    st.session_state.selected_case = st.session_state.search_results.iloc[0].to_dict()
    
    # Search history
    st.subheader("Search History")
    
    # Display search history using native Streamlit radio buttons
    history_options = [f"{item['query']} ({item['timestamp']})" for item in st.session_state.search_history]
    selected_history = st.radio(
        "Previous searches",
        history_options,
        index=st.session_state.active_history_index,
        label_visibility="collapsed"
    )
    
    # Find the index of the selected history item
    selected_index = history_options.index(selected_history)
    if selected_index != st.session_state.active_history_index:
        select_history_item(selected_index)
    
    # User info (simplified)
    st.markdown("---")
    st.text("Shushan Vaziyan")
    st.button("Logout")
    
    # Social media links with native Streamlit components
    st.markdown("Connect with us!")
    cols = st.columns(3)
    with cols[0]:
        st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com)")
    with cols[1]:
        st.markdown("[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com)")
    with cols[2]:
        st.markdown("[![Facebook](https://img.shields.io/badge/Facebook-1877F2?style=for-the-badge&logo=facebook&logoColor=white)](https://facebook.com)")

# Main content area with native Streamlit components
with col2:
    # Search bar
    search_col, search_btn_col = st.columns([5, 1])
    
    with search_col:
        search_query = st.text_input("Search CAS decisions", placeholder="Enter search terms...")
    
    with search_btn_col:
        if st.button("Search"):
            if search_query:
                add_to_history(search_query)
                st.session_state.search_results = semantic_search(search_query, st.session_state.filters)
                if not st.session_state.search_results.empty:
                    st.session_state.selected_case = st.session_state.search_results.iloc[0].to_dict()
    
    # Processing indicator
    st.info("General Answer is processing...")
    
    # Main tabs with native Streamlit components
    tabs = st.tabs(["All", "Claimant", "Respondent", "Tribunal", "BIT"])
    
    with tabs[0]:
        if 'selected_case' in st.session_state:
            case = st.session_state.selected_case
            
            # Display case info using native Streamlit components
            st.markdown(f"## Exhibit C-9: {case['id']} - {case['title']}")
            st.markdown(f"**Page:** {case['page']} | **Line(s):** {case['line_start']}-{case['line_end']}")
            
            # Explanation using native Streamlit components
            st.info(f"**Explanation:** Based on the analysis of {case['id']}.")
            
            # Key findings using native Streamlit components
            st.success(f"""
            ### Key Findings
            
            Based on our analysis of this case, we have identified several key elements:
            
            {case['summary']}
            
            {case['key_facts']}
            """)
            
            # Statement of uncontested facts
            st.subheader("STATEMENT OF UNCONTESTED FACTS")
            st.text(f"Page: 82 | Line(s): 2050")
            
            # Second explanation
            st.info("**Explanation:** Processing of CAS decisions involves assessing evidence, analyzing legal precedents, and preparing legal interpretations.")
            
            # Timeline using native Streamlit components
            st.markdown("### Case Timeline")
            
            # Create a random date 60 days before the case date for timeline purposes
            case_date = datetime.strptime(case['date'], "%Y-%m-%d")
            filing_date = case_date - pd.Timedelta(days=60)
            hearing_date = case_date - pd.Timedelta(days=30)
            
            timeline = {
                f"{filing_date.strftime('%d %b %Y')}": "Case filed with CAS",
                f"{hearing_date.strftime('%d %b %Y')}": "Hearing conducted",
                f"{case_date.strftime('%d %b %Y')}": "Decision rendered"
            }
            
            for date, event in timeline.items():
                cols = st.columns([1, 3])
                with cols[0]:
                    st.markdown(f"**{date}**")
                with cols[1]:
                    st.markdown(event)
            
            # Case outcome
            st.markdown("### Decision")
            st.success(case['decision'])
            
            # Reasoning
            st.markdown("### Reasoning")
            st.markdown(case['reasoning'])
            
    with tabs[1]:
        # Claimant tab with native Streamlit components
        if 'selected_case' in st.session_state:
            case = st.session_state.selected_case
            
            st.header(f"Claimant: {case['claimant']}")
            st.markdown(f"**Case initiated on:** {format_date(case['date'])}")
            
            st.subheader("Key Arguments")
            st.markdown(f"- {case['key_facts']}")
            st.markdown("- Requested relief in accordance with applicable regulations")
            st.markdown("- Submitted supporting evidence")
            
            st.subheader("Relief Sought")
            st.markdown("- Declaration in favor of the claimant's position")
            st.markdown("- Order for the respondent to cover costs of the proceedings")
            st.markdown("- Additional remedies as specified in the claim")
            
            st.subheader("Evidence Submitted")
            evidence = [
                "Witness statements",
                "Expert reports",
                "Documentary evidence",
                "Legal submissions"
            ]
            
            for item in evidence:
                st.markdown(f"- {item}")
    
    with tabs[2]:
        # Respondent tab with native Streamlit components
        if 'selected_case' in st.session_state:
            case = st.session_state.selected_case
            
            st.header(f"Respondent: {case['respondent']}")
            
            st.subheader("Key Arguments")
            st.markdown("- Defense based on applicable regulations")
            st.markdown("- Contested the claimant's interpretation of facts")
            st.markdown("- Requested dismissal of all claims")
            
            st.subheader("Relief Sought")
            st.markdown("- Dismissal of all claims")
            st.markdown("- Order for the claimant to cover costs of the proceedings")
            
            st.subheader("Evidence Submitted")
            evidence = [
                "Counter-witness statements",
                "Expert analysis",
                "Documentary evidence",
                "Legal precedents"
            ]
            
            for item in evidence:
                st.markdown(f"- {item}")
    
    with tabs[3]:
        # Tribunal tab with native Streamlit components
        if 'selected_case' in st.session_state:
            case = st.session_state.selected_case
            
            st.header("Tribunal")
            
            st.subheader("Panel Composition")
            st.markdown(f"{case['panel']}")
            
            st.subheader("Key Findings")
            st.success(f"- {case['decision']}")
            st.markdown(f"- {case['reasoning']}")
            
            st.subheader("Procedural Timeline")
            
            # Create a random date 60 days before the case date for timeline purposes
            case_date = datetime.strptime(case['date'], "%Y-%m-%d")
            filing_date = case_date - pd.Timedelta(days=60)
            hearing_date = case_date - pd.Timedelta(days=30)
            
            st.markdown(f"- Case filed: {filing_date.strftime('%d %b %Y')}")
            st.markdown(f"- Hearing date: {hearing_date.strftime('%d %b %Y')}")
            st.markdown(f"- Decision date: {case_date.strftime('%d %b %Y')}")
    
    with tabs[4]:
        # BIT tab with native Streamlit components
        if 'selected_case' in st.session_state:
            case = st.session_state.selected_case
            
            st.header("Legal Framework & Jurisprudence")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Relevant Legal Principles")
                principles = [
                    "Principle of proportionality",
                    "Burden of proof",
                    "Due process",
                    f"Applicable {case['sport']} regulations"
                ]
                
                for principle in principles:
                    st.markdown(f"- {principle}")
            
            with col2:
                st.subheader("Applicable Regulations")
                regulations = [
                    "CAS Code of Sports-related Arbitration",
                    f"Rules of the {case['sport']} Federation",
                    "World Anti-Doping Code (if applicable)",
                    "Relevant national legislation"
                ]
                
                for regulation in regulations:
                    st.markdown(f"- {regulation}")
            
            st.subheader("Precedent Cases")
            
            # Create sample precedent cases
            precedents = [
                {"id": f"CAS 2018/A/{random.randint(5000, 5999)}", "title": f"Similar {case['sport']} case regarding {random.choice(case['keywords'])}", "date": "2018-06-15"},
                {"id": f"CAS 2019/O/{random.randint(6000, 6999)}", "title": f"Related case on {random.choice(case['keywords'])}", "date": "2019-11-22"},
                {"id": f"CAS 2020/A/{random.randint(7000, 7999)}", "title": f"Precedent on {case['sport']} regulations", "date": "2020-03-07"}
            ]
            
            for precedent in precedents:
                st.markdown(f"**{precedent['id']}**")
                st.markdown(f"{precedent['title']}")
                st.markdown(f"*{precedent['date']}*")
                st.markdown("---")
            
            st.subheader("Key Legal Interpretations")
            st.info(f"""
            The Panel has interpreted the applicable regulations in the context of {case['sport']} and the specific 
            circumstances of this case. The decision provides guidance on how {random.choice(case['keywords'])} 
            should be interpreted in similar cases in the future.
            """)
    
    # Case statistics using native Streamlit components
    st.markdown("---")
    st.subheader("Case Statistics")
    
    # Create columns for statistics
    stat_cols = st.columns(4)
    
    with stat_cols[0]:
        st.metric("Pages", case['page'])
    
    with stat_cols[1]:
        st.metric("Exhibits", random.randint(5, 15))
    
    with stat_cols[2]:
        st.metric("Witnesses", random.randint(2, 6))
    
    with stat_cols[3]:
        # Calculate days from filing to decision
        days_duration = random.randint(90, 180)
        st.metric("Days Duration", days_duration)
