import streamlit as st
import pandas as pd
from datetime import datetime
from io import StringIO

# Set page configuration
st.set_page_config(
    page_title="CaseLens Timeline",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to match the design
st.markdown("""
<style>
    .main-title {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        margin-bottom: 20px;
    }
    .event-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        margin-bottom: 16px;
        background-color: white;
        box-shadow: 0px 1px 3px rgba(0,0,0,0.1);
    }
    .event-header {
        padding: 16px;
        cursor: pointer;
    }
    .event-header:hover {
        background-color: #f9f9f9;
    }
    .event-date {
        font-weight: bold;
    }
    .event-content {
        padding: 16px;
        border-top: 1px solid #eee;
        background-color: #f9f9f9;
    }
    .citation-counter {
        display: flex;
        align-items: center;
        padding: 12px;
        background-color: #f5f5f5;
        border-radius: 8px;
        margin-bottom: 16px;
    }
    .counter-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 4px 8px;
        margin-right: 16px;
    }
    .counter-value {
        font-size: 18px;
        font-weight: bold;
        color: #1E88E5;
    }
    .counter-label {
        font-size: 12px;
        color: #757575;
    }
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 5px;
    }
    .badge-active-claimant {
        background-color: #E3F2FD;
        color: #1565C0;
    }
    .badge-active-respondent {
        background-color: #FFEBEE;
        color: #C62828;
    }
    .badge-inactive {
        background-color: #F5F5F5;
        color: #BDBDBD;
    }
    .document-card {
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
    }
    .document-link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 8px 12px;
        background-color: #E3F2FD;
        color: #1565C0;
        border-radius: 6px;
        text-decoration: none;
        font-size: 14px;
        margin-top: 8px;
    }
    .claimant-header {
        color: #1565C0;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .respondent-header {
        color: #C62828;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .sidebar-title {
        font-size: 20px;
        font-weight: bold;
        color: #1E88E5;
        margin-left: 10px;
    }
    .sidebar-icon {
        background-color: #1E88E5;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
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
    st.sidebar.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 24px;">
        <div class="sidebar-icon">
            <svg width="20" height="20" viewBox="0 0 101 110" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path fill-rule="evenodd" clip-rule="evenodd" d="M100.367 21.7435C89.6483 8.05273 73.7208 0.314453 56.3045 0.314453C26.2347 0.314453 1.52391 24.8686 1.52391 54.7799C1.52391 64.6651 4.18587 73.8971 8.83697 81.8449L8.69251 81.7082L0.917969 109.7L28.5411 101.473C36.8428 106.321 46.5458 109.097 56.8997 109.097C74.6142 109.097 90.6914 100.465 100.664 87.3699L77.2936 69.3636C72.5301 76.2088 64.7894 79.9291 56.4531 79.9291C42.4603 79.9291 30.9982 68.6194 30.9982 54.7799C30.9982 40.6427 42.6093 29.4818 56.751 29.4818C65.2359 29.4818 72.679 33.6486 77.2936 40.0474L100.367 21.7435Z" fill="white"/>
            </svg>
        </div>
        <span class="sidebar-title">CaseLens</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Search
    st.sidebar.markdown("### 🔍 Search Events")
    search_query = st.sidebar.text_input("", placeholder="Search...", label_visibility="collapsed")
    
    # Sidebar - Date Range
    st.sidebar.markdown("### 📅 Date Range")
    
    # Get min and max dates
    valid_dates = [parse_date(event["date"]) for event in events if parse_date(event["date"])]
    min_date = min(valid_dates) if valid_dates else datetime(1965, 1, 1)
    max_date = max(valid_dates) if valid_dates else datetime(2022, 1, 1)
    
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)
    
    # Main content area
    st.markdown("<h1 class='main-title'>Desert Line Projects (DLP) and The Republic of Yemen</h1>", unsafe_allow_html=True)
    
    # Button to copy timeline
    if st.button("📋 Copy Timeline", type="primary"):
        timeline_text = generate_timeline_text(events)
        st.code(timeline_text, language="markdown")
        st.download_button(
            label="Download Timeline as Text",
            data=timeline_text,
            file_name="timeline.md",
            mime="text/markdown",
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
            
            # Citations counter and party badges
            st.markdown(f"""
            <div class="citation-counter">
                <div class="counter-box">
                    <span class="counter-value">{total_count}</span>
                    <span class="counter-label">Citations</span>
                </div>
                <div style="border-left: 1px solid #ddd; height: 24px; margin: 0 16px;"></div>
                <span style="font-size: 12px; text-transform: uppercase; color: #757575; font-weight: 500; margin-right: 10px;">Addressed by:</span>
                <span class="badge {'badge-active-claimant' if has_claimant else 'badge-inactive'}">Claimant</span>
                <span class="badge {'badge-active-respondent' if has_respondent else 'badge-inactive'}">Respondent</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Supporting Documents section
            if event.get("pdf_name") or event.get("source_text"):
                st.markdown("### 📄 Supporting Documents")
                
                for i, pdf_name in enumerate(event.get("pdf_name", [])):
                    source_text = event.get("source_text", [""])[i] if i < len(event.get("source_text", [])) else ""
                    
                    st.markdown(f"""
                    <div class="document-card">
                        <div style="font-weight: 500;">{pdf_name}</div>
                        <div style="font-size: 14px; color: #616161; margin-top: 4px;">{source_text}</div>
                        <a href="#" class="document-link">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                                <polyline points="15 3 21 3 21 9"></polyline>
                                <line x1="10" y1="14" x2="21" y2="3"></line>
                            </svg>
                            Open Document
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Submissions section
            st.markdown("### 📝 Submissions")
            
            # Two-column layout for claimant and respondent
            col1, col2 = st.columns(2)
            
            # Claimant submissions
            with col1:
                st.markdown("<div class='claimant-header'>Claimant</div>", unsafe_allow_html=True)
                
                if event.get("claimant_arguments"):
                    for arg in event["claimant_arguments"]:
                        st.markdown(f"""
                        <div class="document-card">
                            <div style="font-weight: 500;">Page {arg['page']}</div>
                            <div style="font-size: 14px; color: #616161; margin-top: 4px;">{arg['source_text']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color: #BDBDBD; font-style: italic;'>No claimant submissions</div>", unsafe_allow_html=True)
            
            # Respondent submissions
            with col2:
                st.markdown("<div class='respondent-header'>Respondent</div>", unsafe_allow_html=True)
                
                if event.get("respondent_arguments"):
                    for arg in event["respondent_arguments"]:
                        st.markdown(f"""
                        <div class="document-card">
                            <div style="font-weight: 500;">Page {arg['page']}</div>
                            <div style="font-size: 14px; color: #616161; margin-top: 4px;">{arg['source_text']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color: #BDBDBD; font-style: italic;'>No respondent submissions</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
