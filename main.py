import streamlit as st
import pandas as pd
import json
from datetime import datetime
import base64
from io import StringIO
import re

st.set_page_config(
    page_title="CaseLens - Legal Timeline",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 20px;
    }
    .event-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .event-header {
        cursor: pointer;
        display: flex;
        justify-content: space-between;
    }
    .event-date {
        font-weight: 700;
    }
    .citation-counter {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 4px 12px;
        font-weight: 700;
        color: #1E88E5;
        display: inline-block;
        text-align: center;
    }
    .party-tag {
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 14px;
        font-weight: 500;
    }
    .claimant-tag {
        background-color: #E3F2FD;
        color: #1565C0;
    }
    .respondent-tag {
        background-color: #FFEBEE;
        color: #C62828;
    }
    .inactive-tag {
        background-color: #F5F5F5;
        color: #9E9E9E;
    }
    .document-card {
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 10px;
        background-color: white;
    }
    .document-title {
        font-weight: 500;
        margin-bottom: 6px;
    }
    .document-context {
        font-size: 14px;
        color: #616161;
    }
    .section-title {
        font-size: 18px;
        font-weight: 600;
        margin: 16px 0 12px 0;
    }
    .sidebar-title {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .open-doc-button {
        background-color: #E3F2FD;
        color: #1565C0;
        padding: 6px 12px;
        border-radius: 6px;
        border: none;
        display: inline-flex;
        align-items: center;
        font-size: 14px;
        cursor: pointer;
        text-decoration: none;
        margin-top: 8px;
    }
    .open-doc-button:hover {
        background-color: #BBDEFB;
    }
    .doc-icon {
        margin-right: 6px;
    }
    .evidence-summary {
        background-color: #F5F5F5;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
    }
    .divider {
        height: 24px;
        width: 1px;
        background-color: #e0e0e0;
        margin: 0 12px;
    }
    .copy-button {
        background-color: #1976D2;
        color: white;
        padding: 8px 16px;
        border-radius: 6px;
        border: none;
        display: inline-flex;
        align-items: center;
        font-size: 14px;
        cursor: pointer;
    }
    .copy-icon {
        margin-right: 6px;
    }
    .source-text {
        font-size: 14px;
        font-style: italic;
        color: #616161;
        background-color: #F5F5F5;
        padding: 8px;
        border-radius: 4px;
        margin-top: 8px;
    }
    .argument-card {
        border-left: 4px solid;
        padding: 10px;
        margin-bottom: 10px;
        background-color: #FAFAFA;
    }
    .argument-claimant {
        border-left-color: #1565C0;
    }
    .argument-respondent {
        border-left-color: #C62828;
    }
</style>
""", unsafe_allow_html=True)

# Function to load JSON data
def load_sample_data():
    """Load sample timeline data if no file is uploaded"""
    return {
        "events": [
            {
                "date": "2007-12-28",
                "end_date": None,
                "event": "Issuance of Law Decree 53/2007 on the Control of Foreign Trade in Defence and Dual-Use Material.",
                "source_text": [
                    "29.12.2007 Official Journal of the Republic of Martineek L 425 LAW DECREE 53/20 07 of 28 December 2007 ON THE CONTROL OF FOREIGN TRADE IN DEFENCE AND DUAL -USE MATERIAL"
                ],
                "page": [
                    "1"
                ],
                "pdf_name": [
                    "RESPONDENT'S EXHIBIT R1 - Law Decree 53:2007 on the Control of Foreign Trade in Defence and Dual-Use Material.pdf"
                ],
                "doc_name": [
                    "name of the document"
                ],
                "doc_sum": [
                    "summary of the document"
                ],
                "claimant_arguments": [],
                "respondent_arguments": [
                    {
                        "fragment_start": "LAW DECREE",
                        "fragment_end": "Claimant's investment.",
                        "page": "13",
                        "event": "Issuance of Law Decree 53/2007 on the Control of Foreign Trade in Defence and Dual-Use Material.",
                        "source_text": "LAW DECREE 53/2007,11 that is, Dual-Use Regulation, has been promulgated on 28 December 2007, which is the basis for judging the legitimacy of Claimant's investment."
                    }
                ]
            }
        ]
    }

# Function to parse date formats
def parse_date(date_str):
    """Parse different date formats"""
    if not date_str or date_str == "null" or date_str is None:
        return None
    
    # Handle year-only dates
    if re.match(r'^\d{4}-00-00$', date_str):
        return datetime.strptime(date_str[:4], '%Y')
    
    # Handle year-month dates
    if re.match(r'^\d{4}-\d{2}-00$', date_str):
        return datetime.strptime(date_str[:7], '%Y-%m')
    
    # Standard date format
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%d %B %Y')
        except ValueError:
            # Return a default date if parsing fails
            return datetime(1900, 1, 1)

# Function to format date for display
def format_date_for_display(date_str):
    """Format date string for display"""
    if not date_str or date_str == "null" or date_str is None:
        return ""
    
    parsed_date = parse_date(date_str)
    if not parsed_date:
        return ""
    
    # Handle year-only dates
    if date_str.endswith("-00-00"):
        return parsed_date.strftime('%Y')
    
    # Handle year-month dates
    if date_str.endswith("-00"):
        return parsed_date.strftime('%B %Y')
    
    # Full dates
    return parsed_date.strftime('%d %B %Y')

# Function to create downloadable text
def get_download_link(text, filename, link_text):
    """Generate a link to download text content as a file"""
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}" class="copy-button">{link_text}</a>'
    return href

# Function to format timeline for export
def format_timeline_for_export(timeline_data):
    """Format timeline data for text export"""
    export_text = ""
    
    # Sort events by date
    sorted_events = sorted(
        timeline_data["events"], 
        key=lambda x: parse_date(x["date"]) if x["date"] else datetime(1900, 1, 1)
    )
    
    for event in sorted_events:
        # Format date
        formatted_date = format_date_for_display(event["date"])
        
        # Main text with date
        timeline_text = f"**{formatted_date}** - {event['event']}"
        
        # Add source references
        if event.get("pdf_name") and len(event["pdf_name"]) > 0:
            pdf_refs = "; ".join([pdf for pdf in event["pdf_name"] if pdf])
            timeline_text += f"\nSource: {pdf_refs}"
        
        # Add arguments
        has_arguments = False
        
        if event.get("claimant_arguments") and len(event["claimant_arguments"]) > 0:
            has_arguments = True
            timeline_text += "\n\nClaimant Arguments:"
            for arg in event["claimant_arguments"]:
                timeline_text += f"\n- {arg['source_text']}"
        
        if event.get("respondent_arguments") and len(event["respondent_arguments"]) > 0:
            has_arguments = True
            timeline_text += "\n\nRespondent Arguments:"
            for arg in event["respondent_arguments"]:
                timeline_text += f"\n- {arg['source_text']}"
        
        export_text += f"{timeline_text}\n\n{'=' * 50}\n\n"
    
    return export_text

# Sidebar
with st.sidebar:
    st.title("CaseLens")
    
    # File uploader for JSON data
    uploaded_file = st.file_uploader("Upload Timeline JSON", type=["json"])
    
    st.markdown("<div class='sidebar-title'>Search Events</div>", unsafe_allow_html=True)
    search_query = st.text_input("", placeholder="Search...", label_visibility="collapsed")
    
    st.markdown("<div class='sidebar-title'>Date Range</div>", unsafe_allow_html=True)
    start_date = st.date_input("Start Date", value=None, label_visibility="collapsed")
    end_date = st.date_input("End Date", value=None, label_visibility="collapsed")
    
    st.markdown("<div class='sidebar-title'>Filter by Party</div>", unsafe_allow_html=True)
    show_claimant = st.checkbox("Claimant Arguments", value=True)
    show_respondent = st.checkbox("Respondent Arguments", value=True)

# Main content
st.markdown("<h1 class='main-header'>Legal Case Timeline</h1>", 
            unsafe_allow_html=True)

# Load data
if uploaded_file is not None:
    timeline_data = json.load(uploaded_file)
else:
    # Use the provided JSON structure from the document
    with open('json_structure.json', 'r') as f:
        timeline_data = json.load(f)

# Export functionality
export_text = format_timeline_for_export(timeline_data)
st.markdown(
    get_download_link(export_text, "timeline_export.txt", "📋 Export Timeline"),
    unsafe_allow_html=True
)

# Process and display timeline events
events = timeline_data["events"]

# Apply filters if needed
if search_query:
    events = [e for e in events if search_query.lower() in e["event"].lower()]

# Apply party filters
if not show_claimant and not show_respondent:
    # If both are unchecked, show all events anyway
    filtered_events = events
elif not show_claimant:
    # Show only events with respondent arguments
    filtered_events = [e for e in events if e.get("respondent_arguments") and len(e["respondent_arguments"]) > 0]
elif not show_respondent:
    # Show only events with claimant arguments
    filtered_events = [e for e in events if e.get("claimant_arguments") and len(e["claimant_arguments"]) > 0]
else:
    # Show all events
    filtered_events = events

# Sort events by date
try:
    sorted_events = sorted(
        filtered_events, 
        key=lambda x: parse_date(x["date"]) if x["date"] else datetime(1900, 1, 1)
    )
except Exception as e:
    st.error(f"Error sorting events: {e}")
    sorted_events = filtered_events

# Display events
for event in sorted_events:
    # Format date for display
    formatted_date = format_date_for_display(event["date"])
    
    # Count arguments
    claimant_arg_count = len(event.get("claimant_arguments", []))
    respondent_arg_count = len(event.get("respondent_arguments", []))
    total_arg_count = claimant_arg_count + respondent_arg_count
    
    # Determine if each party has arguments
    has_claimant_arguments = claimant_arg_count > 0
    has_respondent_arguments = respondent_arg_count > 0
    
    # Create expander for each event
    with st.expander(f"**{formatted_date}** - {event['event']}", expanded=False):
        # Evidence summary
        st.markdown(
            f"""
            <div class="evidence-summary">
                <div class="citation-counter">{total_arg_count}<br><span style="font-size:12px;">Arguments</span></div>
                <div class="divider"></div>
                <div>
                    <span style="font-size:12px; text-transform:uppercase; font-weight:500; margin-right:8px;">Addressed by:</span>
                    <span class="party-tag {'claimant-tag' if has_claimant_arguments else 'inactive-tag'}">Claimant</span>
                    <span class="party-tag {'respondent-tag' if has_respondent_arguments else 'inactive-tag'}">Respondent</span>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # Source Documents
        if event.get("source_text") and event.get("pdf_name"):
            st.markdown("<div class='section-title'>Source Documents</div>", unsafe_allow_html=True)
            
            for i, (source, pdf, page) in enumerate(zip(
                event.get("source_text", []), 
                event.get("pdf_name", []), 
                event.get("page", [""])
            )):
                if source and pdf:
                    st.markdown(
                        f"""
                        <div class="document-card">
                            <div class="document-title">{pdf}</div>
                            <div class="document-context">Page: {page}</div>
                            <div class="source-text">{source}</div>
                            <a href="#" class="open-doc-button"><span class="doc-icon">📄</span> Open Document</a>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
        
        # Arguments section
        if has_claimant_arguments or has_respondent_arguments:
            st.markdown("<div class='section-title'>Arguments</div>", unsafe_allow_html=True)
            
            # Create two columns for claimant and respondent
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<div style='color:#1565C0; font-weight:500; margin-bottom:8px;'>Claimant Arguments</div>", unsafe_allow_html=True)
                if has_claimant_arguments:
                    for arg in event.get("claimant_arguments", []):
                        st.markdown(
                            f"""
                            <div class="argument-card argument-claimant">
                                <div class="document-context">Page: {arg.get('page', 'N/A')}</div>
                                <div class="source-text">{arg.get('source_text', '')}</div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown("<em>No claimant arguments for this event</em>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div style='color:#C62828; font-weight:500; margin-bottom:8px;'>Respondent Arguments</div>", unsafe_allow_html=True)
                if has_respondent_arguments:
                    for arg in event.get("respondent_arguments", []):
                        st.markdown(
                            f"""
                            <div class="argument-card argument-respondent">
                                <div class="document-context">Page: {arg.get('page', 'N/A')}</div>
                                <div class="source-text">{arg.get('source_text', '')}</div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown("<em>No respondent arguments for this event</em>", unsafe_allow_html=True)
