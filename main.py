import streamlit as st
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="CaseLens Timeline",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS for blue and red styling
st.markdown("""
<style>
    /* Pill/badge styles */
    .blue-pill {
        background-color: #E3F2FD;
        color: #1565C0;
        border-radius: 12px;
        padding: 6px 14px;
        font-weight: 500;
        font-size: 16px;
        display: inline-block;
    }
    .red-pill {
        background-color: #FFEBEE;
        color: #C62828;
        border-radius: 12px;
        padding: 6px 14px;
        font-weight: 500;
        font-size: 16px;
        display: inline-block;
    }
    .gray-pill {
        background-color: #F5F5F5;
        color: #9E9E9E;
        border-radius: 12px;
        padding: 6px 14px;
        font-weight: 500;
        font-size: 16px;
        display: inline-block;
    }
    
    /* Header styles */
    .blue-header {
        color: #1565C0;
        font-weight: 600;
        font-size: 24px;
        margin-bottom: 12px;
    }
    .red-header {
        color: #C62828;
        font-weight: 600;
        font-size: 24px;
        margin-bottom: 12px;
    }
    
    /* Section titles */
    .section-title {
        font-size: 22px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 16px;
    }
    
    /* Make the main title larger */
    .main-title {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: #333;
        margin-bottom: 30px !important;
    }
    
    /* Document titles */
    .document-title {
        font-size: 18px;
        font-weight: 600;
    }
    
    /* Page reference */
    .page-ref {
        font-size: 16px;
        font-weight: 600;
    }
    
    /* Citations counter */
    .counter-value {
        font-size: 22px !important;
        font-weight: bold;
        color: #1E88E5;
    }
    .counter-label {
        font-size: 14px;
        color: #757575;
    }
    
    /* Addressed by text */
    .addressed-by {
        font-size: 16px;
        color: #555;
        margin-right: 12px;
    }
    
    /* Make the event titles in expanders larger */
    .css-1fcdlhc {
        font-size: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# Load the data directly in Python without JSON parsing
@st.cache_data
def load_data():
    # Create the data structure directly
    data = {
        "events": [
            {
                "date": "1965-00-00",
                "end_date": None,
                "event": "Martineek Herald began publishing reliable everyday news.",
                "source_text": [
                    "FDI Moot CENTER FOR INTERNATIONAL LEGAL STUDIES <LINE: 415> CLAIMANT'S EXHIBIT C9 – Martineek Herald Article of 19 December 2022 VOL. XXIX NO. 83 MONDAY, DECEMBER 19, 2022 MARTINEEK HERALD RELIABLE EVERYDAY NEWS"
                ],
                "page": ["1"],
                "pdf_name": ["CLAIMANT'S EXHIBIT C9 – Martineek Herald Article of 19 December 2022.pdf"],
                "doc_name": ["name of the document"],
                "doc_sum": ["summary of the document"]
            },
            {
                "date": "2007-12-28",
                "end_date": None,
                "event": "Issuance of Law Decree 53/2007 on the Control of Foreign Trade in Defence and Dual-Use Material.",
                "source_text": [
                    "29.12.2007 Official Journal of the Republic of Martineek L 425 LAW DECREE 53/20 07 of 28 December 2007 ON THE CONTROL OF FOREIGN TRADE IN DEFENCE AND DUAL-USE MATERIAL"
                ],
                "page": ["1"],
                "pdf_name": ["RESPONDENT'S EXHIBIT R1 - Law Decree 53:2007 on the Control of Foreign Trade in Defence and Dual-Use Material.pdf"],
                "doc_name": ["name of the document"],
                "doc_sum": ["summary of the document"],
                "claimant_arguments": [],
                "respondent_arguments": [
                    {
                        "fragment_start": "LAW DECREE",
                        "fragment_end": "Claimant's investment.",
                        "page": "13",
                        "event": "Issuance of Law Decree 53/2007 on the Control of Foreign Trade in Defence and Dual-Use Material.",
                        "source_text": "LAW DECREE 53/2007,11 that is, Dual-Use Regulation, has been promulgated on 28 December 2007, which is the basis for judging the legitimacy of Claimant's investment."
                    },
                    {
                        "fragment_start": "According to",
                        "fragment_end": "Dual-Use Material33",
                        "page": "17",
                        "event": "Issuance of Law Decree 53/2007 on the Control of Foreign Trade in Defence and Dual-Use Material.",
                        "source_text": "According to the Law Decree 53/2007 on the Control of Foreign Trade in Defence and Dual-Use Material33"
                    },
                    {
                        "fragment_start": "It was",
                        "fragment_end": "Dual-Use Material35",
                        "page": "17",
                        "event": "Issuance of Law Decree 53/2007 on the Control of Foreign Trade in Defence and Dual-Use Material.",
                        "source_text": "It was clearly stated in the Law Decree 53/2007 on the Control of Foreign Trade in Defence and Dual-Use Material35"
                    }
                ]
            },
            {
                "date": "2013-06-28",
                "end_date": None,
                "event": "The Martineek-Albion BIT was ratified.",
                "source_text": [
                    "rtineek and Albion terminated the 1993 Agreement on Encouragement and Reciprocal Protection of Investments between the Republic of Martineek and the Federation of Albion and replaced it with a revised Agreement on Encouragement and Reciprocal Protection of Investments between the Republic of Martineek and the Federation of Albion (the 'Martineek-Albion BIT'). The Martineek-Albion BIT was ratified on"
                ],
                "page": ["1"],
                "pdf_name": ["Statement of Uncontested Facts.pdf"],
                "doc_name": ["name of the document"],
                "doc_sum": ["summary of the document"],
                "claimant_arguments": [
                    {
                        "fragment_start": "Martineek and",
                        "fragment_end": "28 June 2013.",
                        "page": "16",
                        "event": "The Martineek-Albion BIT was ratified.",
                        "source_text": "Martineek and Albion ratified the BIT on 28 June 2013."
                    }
                ],
                "respondent_arguments": []
            },
            {
                "date": "2016-00-00",
                "end_date": None,
                "event": "Martineek became one of the world's leading manufacturers of industrial robots.",
                "source_text": [
                    "6. In late 2016, with technological advances in the Archipelago, Martineek became one of the world's leading manufacturers of industrial robots."
                ],
                "page": ["1"],
                "pdf_name": ["Statement of Uncontested Facts.pdf"],
                "doc_name": ["name of the document"],
                "doc_sum": ["summary of the document"],
                "claimant_arguments": [
                    {
                        "fragment_start": "In late",
                        "fragment_end": "competitive purposes",
                        "page": "19",
                        "event": "Martineek became one of the world's leading manufacturers of industrial robots.",
                        "source_text": "In late 2016, Martineek became one of the world's leading manufacturers of industrial robots,37 while the rapid development in technology of Albion might be in advance of Martineek's entities. Respondent's actions were more likely for competitive purposes"
                    }
                ],
                "respondent_arguments": [
                    {
                        "fragment_start": "Through a",
                        "fragment_end": "robotic industry.",
                        "page": "6",
                        "event": "Martineek became one of the world's leading manufacturers of industrial robots.",
                        "source_text": "Through a raft of major reforms, Martineek made significant efforts to attract foreign investments and became a global leader in the robotic industry."
                    }
                ]
            }
        ]
    }
    return data

# Function to parse date
def parse_date(date_str):
    if not date_str or date_str == "null":
        return None
    
    # Handle cases like "2016-00-00"
    if "-00-00" in date_str:
        date_str = date_str.replace("-00-00", "-01-01")
    elif "-00" in date_str:
        date_str = date_str.replace("-00", "-01")
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None

# Function to format date for display
def format_date(date_str):
    date = parse_date(date_str)
    if not date:
        return "Unknown date"
    
    # If we have only the year (original had -00-00)
    if "-00-00" in date_str:
        return date.strftime("%Y")
    # If we have year and month (original had -00)
    elif "-00" in date_str:
        return date.strftime("%B %Y")
    # Full date
    else:
        return date.strftime("%d %B %Y")

# Function to generate timeline text for copying
def generate_timeline_text(events):
    text = ""
    for event in sorted(events, key=lambda x: parse_date(x["date"]) or datetime.min):
        # Format the event text with date in bold
        date_formatted = format_date(event["date"])
        text += f"**{date_formatted}** {event['event']}[1]\n\n"
        
        # Sources for footnote
        sources = []
        if event.get("claimant_arguments"):
            sources.extend([f"{arg['fragment_start']}... (Page {arg['page']})" for arg in event["claimant_arguments"]])
        if event.get("respondent_arguments"):
            sources.extend([f"{arg['fragment_start']}... (Page {arg['page']})" for arg in event["respondent_arguments"]])
        if event.get("pdf_name"):
            sources.extend(event["pdf_name"])
        
        if sources:
            text += f"[1] {'; '.join(sources)}\n\n"
    
    return text

# Main app function
def main():
    # Load data
    data = load_data()
    events = data["events"]
    
    # Sidebar - Logo and title
    with st.sidebar:
        st.title("🔍 CaseLens")
        st.divider()
        
        # Search
        st.header("Search Events")
        search_query = st.text_input("", placeholder="Search...", label_visibility="collapsed")
        
        # Date Range
        st.header("Date Range")
        
        # Get min and max dates
        valid_dates = [parse_date(event["date"]) for event in events if parse_date(event["date"])]
        min_date = min(valid_dates) if valid_dates else datetime(1965, 1, 1)
        max_date = max(valid_dates) if valid_dates else datetime(2022, 1, 1)
        
        start_date = st.date_input("Start Date", min_date)
        end_date = st.date_input("End Date", max_date)
    
    # Main content area
    st.markdown("<h1 class='main-title'>Desert Line Projects (DLP) and The Republic of Yemen</h1>", unsafe_allow_html=True)
    
    # Button to copy timeline
    if st.button("📋 Copy Timeline", type="primary", use_container_width=True):
        timeline_text = generate_timeline_text(events)
        st.code(timeline_text, language="markdown")
        st.download_button(
            label="Download Timeline as Text",
            data=timeline_text,
            file_name="timeline.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    # Filter events
    filtered_events = events
    
    # Apply search filter
    if search_query:
        filtered_events = [event for event in filtered_events 
                         if search_query.lower() in event["event"].lower()]
    
    # Apply date filter
    filtered_events = [
        event for event in filtered_events
        if parse_date(event["date"]) and start_date <= parse_date(event["date"]).date() <= end_date
    ]
    
    # Sort events by date
    filtered_events = sorted(filtered_events, key=lambda x: parse_date(x["date"]) or datetime.min)
    
    # Display events
    for event in filtered_events:
        date_formatted = format_date(event["date"])
        
        # Create expander for each event
        with st.expander(f"{date_formatted}: {event['event']}"):
            # Calculate citation counts
            claimant_count = len(event.get("claimant_arguments", []))
            respondent_count = len(event.get("respondent_arguments", []))
            doc_count = len(event.get("pdf_name", []))
            total_count = claimant_count + respondent_count + doc_count
            
            # Determine if each party has addressed this event
            has_claimant = claimant_count > 0
            has_respondent = respondent_count > 0
            
            # Citation counter and badges
            st.markdown("---")
            citation_cols = st.columns([1, 3])
            
            with citation_cols[0]:
                # Number with label
                st.container().markdown(f"""
                <div style="background-color: white; border: 1px solid #ddd; border-radius: 4px; 
                     padding: 8px 16px; text-align: center; width: fit-content;">
                    <div class="counter-value">{total_count}</div>
                    <div class="counter-label">Citations</div>
                </div>
                """, unsafe_allow_html=True)
            
            with citation_cols[1]:
                # Party badges
                st.markdown("<span class='addressed-by'>Addressed by:</span>", unsafe_allow_html=True)
                claimant_class = "blue-pill" if has_claimant else "gray-pill"
                respondent_class = "red-pill" if has_respondent else "gray-pill"
                
                st.markdown(f"""
                <span class="{claimant_class}">Claimant</span> 
                <span class="{respondent_class}">Respondent</span>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Supporting Documents section
            st.markdown("<div class='section-title'>📄 Supporting Documents</div>", unsafe_allow_html=True)
            
            if event.get("pdf_name") or event.get("source_text"):
                for i, pdf_name in enumerate(event.get("pdf_name", [])):
                    source_text = event.get("source_text", [""])[i] if i < len(event.get("source_text", [])) else ""
                    
                    with st.container():
                        st.markdown(f"<div class='document-title'>{pdf_name}</div>", unsafe_allow_html=True)
                        st.caption(source_text)
                        st.button("📄 Open Document", key=f"doc_{event['date']}_{i}", use_container_width=True)
                    st.markdown("---")
            
            # Submissions section
            st.markdown("<div class='section-title'>📝 Submissions</div>", unsafe_allow_html=True)
            
            # Two-column layout for claimant and respondent
            claimant_col, respondent_col = st.columns(2)
            
            # Claimant submissions
            with claimant_col:
                st.markdown("<span class='blue-header'>Claimant</span>", unsafe_allow_html=True)
                
                if event.get("claimant_arguments"):
                    for idx, arg in enumerate(event["claimant_arguments"]):
                        with st.container():
                            st.markdown(f"<div class='page-ref'>Page {arg['page']}</div>", unsafe_allow_html=True)
                            st.caption(arg['source_text'])
                        st.markdown("---")
                else:
                    st.caption("No claimant submissions")
            
            # Respondent submissions
            with respondent_col:
                st.markdown("<span class='red-header'>Respondent</span>", unsafe_allow_html=True)
                
                if event.get("respondent_arguments"):
                    for idx, arg in enumerate(event["respondent_arguments"]):
                        with st.container():
                            st.markdown(f"<div class='page-ref'>Page {arg['page']}</div>", unsafe_allow_html=True)
                            st.caption(arg['source_text'])
                        st.markdown("---")
                else:
                    st.caption("No respondent submissions")

if __name__ == "__main__":
    main()
