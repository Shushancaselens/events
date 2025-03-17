import streamlit as st
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="CaseLens Timeline",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# Improved search function that checks all relevant fields
def search_event(event, query):
    if not query:
        return True
    
    query = query.lower()
    
    # Check main event text
    if query in event["event"].lower():
        return True
    
    # Check source texts
    for source in event.get("source_text", []):
        if query in source.lower():
            return True
    
    # Check document names
    for doc in event.get("pdf_name", []):
        if query in doc.lower():
            return True
    
    # Check claimant arguments
    for arg in event.get("claimant_arguments", []):
        if query in arg.get("source_text", "").lower():
            return True
    
    # Check respondent arguments
    for arg in event.get("respondent_arguments", []):
        if query in arg.get("source_text", "").lower():
            return True
            
    return False

# Main app function
def main():
    # Load data
    data = load_data()
    events = data["events"]
    
    # Sidebar - Logo and title
    with st.sidebar:
        st.title("🔍 CaseLens")
        st.divider()
        
        # Search with improved explanation
        st.subheader("Search Events")
        search_query = st.text_input("", placeholder="Search across all event data...", label_visibility="collapsed")
        if search_query:
            st.caption("Searching in event descriptions, document names, and all arguments")
        
        # Date Range
        st.subheader("Date Range")
        
        # Get min and max dates
        valid_dates = [parse_date(event["date"]) for event in events if parse_date(event["date"])]
        min_date = min(valid_dates) if valid_dates else datetime(1965, 1, 1)
        max_date = max(valid_dates) if valid_dates else datetime(2022, 1, 1)
        
        start_date = st.date_input("Start Date", min_date)
        end_date = st.date_input("End Date", max_date)
    
    # Main content area
    st.title("Desert Line Projects (DLP) and The Republic of Yemen")
    
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
    
    # Filter events - IMPROVED SEARCH
    filtered_events = events.copy()
    
    # Apply search filter
    if search_query:
        filtered_events = [event for event in filtered_events if search_event(event, search_query)]
        st.success(f"Found {len(filtered_events)} events matching '{search_query}'")
    
    # Apply date filter
    filtered_events = [
        event for event in filtered_events
        if parse_date(event["date"]) and start_date <= parse_date(event["date"]).date() <= end_date
    ]
    
    # Sort events by date
    filtered_events = sorted(filtered_events, key=lambda x: parse_date(x["date"]) or datetime.min)
    
    # Display events
    if not filtered_events:
        st.warning("No events match your search criteria. Try adjusting your search or date range.")
    
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
            
            # Citation counter and badges using pure Streamlit
            st.divider()
            
            # Citation counter
            col1, col2 = st.columns([1, 4])
            with col1:
                st.metric("Citations", total_count)
            
            with col2:
                st.write("**Addressed by:**")
                
                # Use pure Streamlit components for badges
                badge_cols = st.columns(2)
                with badge_cols[0]:
                    if has_claimant:
                        st.info("Claimant")
                    else:
                        st.text("Claimant")
                with badge_cols[1]:
                    if has_respondent:
                        st.error("Respondent")
                    else:
                        st.text("Respondent")
            
            st.divider()
            
            # Supporting Documents section
            if event.get("pdf_name") or event.get("source_text"):
                st.subheader("📄 Supporting Documents")
                
                for i, pdf_name in enumerate(event.get("pdf_name", [])):
                    source_text = event.get("source_text", [""])[i] if i < len(event.get("source_text", [])) else ""
                    
                    # Use color to indicate search matches
                    with st.container():
                        if search_query and search_query.lower() in pdf_name.lower():
                            st.success(f"**{pdf_name}**")
                        else:
                            st.write(f"**{pdf_name}**")
                            
                        if search_query and search_query.lower() in source_text.lower():
                            st.success(source_text)
                        else:
                            st.caption(source_text)
                            
                        st.button("Open Document", key=f"doc_{event['date']}_{i}")
                    st.divider()
            
            # Submissions section
            st.subheader("📝 Submissions")
            
            # Two-column layout for claimant and respondent
            claimant_col, respondent_col = st.columns(2)
            
            # Claimant submissions - with Streamlit colors
            with claimant_col:
                # Use info color for claimant
                st.info("**Claimant**")
                
                if event.get("claimant_arguments"):
                    for idx, arg in enumerate(event["claimant_arguments"]):
                        source_text = arg.get('source_text', '')
                        
                        with st.container():
                            st.write(f"**Page {arg['page']}**")
                            
                            # Highlight matched search terms with success color
                            if search_query and search_query.lower() in source_text.lower():
                                st.success(source_text)
                            else:
                                st.caption(source_text)
                                
                        st.divider()
                else:
                    st.caption("No claimant submissions")
            
            # Respondent submissions - with Streamlit colors
            with respondent_col:
                # Use error color for respondent
                st.error("**Respondent**")
                
                if event.get("respondent_arguments"):
                    for idx, arg in enumerate(event["respondent_arguments"]):
                        source_text = arg.get('source_text', '')
                        
                        with st.container():
                            st.write(f"**Page {arg['page']}**")
                            
                            # Highlight matched search terms with success color
                            if search_query and search_query.lower() in source_text.lower():
                                st.success(source_text)
                            else:
                                st.caption(source_text)
                                
                        st.divider()
                else:
                    st.caption("No respondent submissions")

if __name__ == "__main__":
    main()
