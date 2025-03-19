import streamlit as st
import pandas as pd
from datetime import datetime
from io import StringIO, BytesIO
import zipfile
import base64
import tempfile
import os

# VISUALIZE START #####################
st.set_page_config(
    page_title="CaseLens: Arbitral Event Timeline",
    page_icon="media/CaseLens Logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
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

# Function to create a minimal Office Open XML (docx) file manually
def generate_timeline_docx_manual(events):
    # We'll create a minimal docx file with the required XML parts
    docx_buffer = BytesIO()
    
    try:
        with zipfile.ZipFile(docx_buffer, 'w') as docx_zip:
            # Add required files for minimal docx
            
            # Add [Content_Types].xml
            content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
    <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
    <Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
    <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
    <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""
            docx_zip.writestr('[Content_Types].xml', content_types_xml)
            
            # Add _rels/.rels
            rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
            docx_zip.writestr('_rels/.rels', rels_xml)
            
            # Add docProps/app.xml
            app_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
    <Application>Streamlit</Application>
</Properties>"""
            docx_zip.writestr('docProps/app.xml', app_xml)
            
            # Add docProps/core.xml
            core_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>Arbitral Event Timeline</dc:title>
    <dc:creator>Streamlit App</dc:creator>
    <dc:created>{}</dc:created>
</cp:coreProperties>""".format(datetime.now().isoformat())
            docx_zip.writestr('docProps/core.xml', core_xml)
            
            # Add word/_rels/document.xml.rels
            document_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
    <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
    <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>
</Relationships>"""
            docx_zip.writestr('word/_rels/document.xml.rels', document_rels_xml)
            
            # Add word/fontTable.xml
            font_table_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fonts xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:font w:name="Calibri">
        <w:panose1 w:val="020F0502020204030204"/>
        <w:charset w:val="00"/>
        <w:family w:val="swiss"/>
        <w:pitch w:val="variable"/>
        <w:sig w:usb0="E10002FF" w:usb1="4000ACFF" w:usb2="00000009" w:usb3="00000000" w:csb0="0000019F" w:csb1="00000000"/>
    </w:font>
</w:fonts>"""
            docx_zip.writestr('word/fontTable.xml', font_table_xml)
            
            # Add word/settings.xml
            settings_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:defaultTabStop w:val="720"/>
</w:settings>"""
            docx_zip.writestr('word/settings.xml', settings_xml)
            
            # Add word/styles.xml (minimal)
            styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:style w:type="paragraph" w:styleId="Normal">
        <w:name w:val="Normal"/>
        <w:pPr/>
        <w:rPr/>
    </w:style>
    <w:style w:type="paragraph" w:styleId="Heading1">
        <w:name w:val="heading 1"/>
        <w:basedOn w:val="Normal"/>
        <w:pPr>
            <w:jc w:val="center"/>
        </w:pPr>
        <w:rPr>
            <w:b/>
            <w:sz w:val="32"/>
        </w:rPr>
    </w:style>
</w:styles>"""
            docx_zip.writestr('word/styles.xml', styles_xml)
            
            # We need to add the footnotes part to content types
            content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
    <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
    <Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
    <Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>
    <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
    <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""
            docx_zip.writestr('[Content_Types].xml', content_types_xml)
            
            # Update document relationships to include footnotes
            document_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
    <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
    <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>
    <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>
</Relationships>"""
            docx_zip.writestr('word/_rels/document.xml.rels', document_rels_xml)
            
            # Update settings to enable footnotes
            settings_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:defaultTabStop w:val="720"/>
    <w:footnotePr>
        <w:pos w:val="pageBottom"/>
        <w:numFmt w:val="decimal"/>
    </w:footnotePr>
</w:settings>"""
            docx_zip.writestr('word/settings.xml', settings_xml)
            
            # Create the footnotes.xml file
            footnotes_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:footnote w:id="0">
        <w:p>
            <w:r>
                <w:rPr>
                    <w:rStyle w:val="FootnoteReference"/>
                </w:rPr>
                <w:footnoteRef/>
            </w:r>
            <w:r>
                <w:t xml:space="preserve"> </w:t>
            </w:r>
        </w:p>
    </w:footnote>
    <w:footnote w:id="1">
        <w:p>
            <w:r>
                <w:rPr>
                    <w:rStyle w:val="FootnoteReference"/>
                </w:rPr>
                <w:footnoteRef/>
            </w:r>
            <w:r>
                <w:t xml:space="preserve"> </w:t>
            </w:r>
        </w:p>
    </w:footnote>"""
            
            # Add custom footnotes for each event
            sorted_events = sorted(events, key=lambda x: parse_date(x["date"]) or datetime.min)
            
            for i, event in enumerate(sorted_events):
                footnote_id = i + 2  # Start from 2 as 0 and 1 are reserved
                
                # Format exhibits for footnote
                claimant_exhibits = []
                respondent_exhibits = []
                other_exhibits = []
                
                if event.get("claimant_arguments"):
                    for arg in event.get("claimant_arguments"):
                        claimant_exhibits.append(f"{arg['fragment_start']}... (Page {arg['page']})")
                
                if event.get("respondent_arguments"):
                    for arg in event.get("respondent_arguments"):
                        respondent_exhibits.append(f"{arg['fragment_start']}... (Page {arg['page']})")
                
                if event.get("doc_name"):
                    other_exhibits.extend(event.get("doc_name"))
                
                # Build footnote content
                footnote_content = ""
                
                if claimant_exhibits or respondent_exhibits or other_exhibits:
                    if claimant_exhibits:
                        footnote_content += "Claimant memorial: " + "; ".join(claimant_exhibits)
                    
                    if respondent_exhibits:
                        if footnote_content:
                            footnote_content += "; "
                        footnote_content += "Respondent memorial: " + "; ".join(respondent_exhibits)
                    
                    if other_exhibits:
                        if footnote_content:
                            footnote_content += "; "
                        footnote_content += "Exhibits: " + "; ".join(other_exhibits)
                else:
                    footnote_content = "No exhibits available"
                
                # Add footnote to XML
                footnotes_xml += f"""
    <w:footnote w:id="{footnote_id}">
        <w:p>
            <w:r>
                <w:rPr>
                    <w:rStyle w:val="FootnoteReference"/>
                </w:rPr>
                <w:footnoteRef/>
            </w:r>
            <w:r>
                <w:t xml:space="preserve"> {footnote_content}</w:t>
            </w:r>
        </w:p>
    </w:footnote>"""
            
            # Close footnotes XML
            footnotes_xml += """
</w:footnotes>"""
            
            docx_zip.writestr('word/footnotes.xml', footnotes_xml)
            
            # Create the main document.xml with timeline content and proper footnote references
            document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        <w:p>
            <w:pPr>
                <w:pStyle w:val="Heading1"/>
            </w:pPr>
            <w:r>
                <w:t>Arbitral Event Timeline</w:t>
            </w:r>
        </w:p>"""
            
            # Add events in chronological order with proper footnotes
            for i, event in enumerate(sorted_events):
                # Format the date
                date_formatted = format_date(event["date"])
                footnote_id = i + 2  # Match with footnote IDs
                
                # Add event paragraph with date in bold and properly referenced footnote
                document_xml += f"""
        <w:p>
            <w:r>
                <w:rPr>
                    <w:b/>
                </w:rPr>
                <w:t>{date_formatted}: </w:t>
            </w:r>
            <w:r>
                <w:t>{event["event"]}</w:t>
            </w:r>
            <w:r>
                <w:rPr>
                    <w:rStyle w:val="FootnoteReference"/>
                </w:rPr>
                <w:footnoteReference w:id="{footnote_id}"/>
            </w:r>
        </w:p>"""
            
            # Close document
            document_xml += """
    </w:body>
</w:document>"""
            
            docx_zip.writestr('word/document.xml', document_xml)
        
        # Reset buffer position to beginning
        docx_buffer.seek(0)
        return docx_buffer.getvalue()
    
    except Exception as e:
        st.error(f"Error creating DOCX file: {str(e)}")
        return None

def show_sidebar(events, unique_id=""):
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
    search_query = st.sidebar.text_input("", placeholder="Search...", label_visibility="collapsed", key=f"search_input_{unique_id}")
    
    # Sidebar - Date Range
    st.sidebar.markdown("### 📅 Date Range")
    
    # Get min and max dates
    valid_dates = [parse_date(event["date"]) for event in events if parse_date(event["date"])]
    min_date = min(valid_dates) if valid_dates else datetime(1965, 1, 1)
    max_date = max(valid_dates) if valid_dates else datetime(2022, 1, 1)
    
    start_date = st.sidebar.date_input("Start Date", min_date, key=f"start_date_{unique_id}")
    end_date = st.sidebar.date_input("End Date", max_date, key=f"end_date_{unique_id}")
    
    return search_query, start_date, end_date

# Main app function
def visualize(data, unique_id="", sidebar_values=None):
    # Use passed data directly
    events = data["events"]
    
    # Use passed sidebar values or create new ones
    if sidebar_values is None:
        search_query, start_date, end_date = show_sidebar(events, unique_id)
    else:
        search_query, start_date, end_date = sidebar_values
    
    # Download timeline button
    if st.button("📋 Download Timeline", type="primary", key=f"download_timeline_{unique_id}"):
        # First try to create the DOCX with pandoc (cleaner approach)
        docx_bytes = try_create_docx_with_pandoc(events)
        
        if docx_bytes:
            # Provide download button for the Word document created with pandoc
            st.download_button(
                label="Download Timeline",
                data=docx_bytes,
                file_name="timeline.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"download_timeline_docx_{unique_id}"
            )
        else:
            # Fall back to plain text if pandoc approach fails
            text_content = generate_timeline_text(events)
            st.download_button(
                label="Download Timeline",
                data=text_content,
                file_name="timeline.txt",
                mime="text/plain",
                key=f"download_timeline_txt_{unique_id}"
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
            doc_count = len(event.get("doc_name", []))
            total_count = claimant_count + respondent_count + doc_count
            
            # Determine if each party has addressed this event
            has_claimant = claimant_count > 0
            has_respondent = respondent_count > 0
            
            
            print(event, " >>> ", has_claimant, has_respondent)
            
            # Citations counter and party badges
            # Build the badges dynamically based on who addressed the event
            badges = []
            if has_claimant:
                badges.append('<span class="badge badge-active-claimant">Claimant</span>')
            if has_respondent:
                badges.append('<span class="badge badge-active-respondent">Respondent</span>')
            badges_html = ''.join(badges) if badges else '<span class="badge badge-inactive">Not Addressed</span>'

            st.markdown(f"""
            <div class="citation-counter">
                <div class="counter-box">
                    <span class="counter-value">{total_count}</span>
                    <span class="counter-label">Sources</span>
                </div>
                <div style="border-left: 1px solid #ddd; height: 24px; margin: 0 16px;"></div>
                <span style="font-size: 12px; text-transform: uppercase; color: #757575; font-weight: 500; margin-right: 10px;">Addressed by:</span>
                {badges_html}
            </div>
            """, unsafe_allow_html=True)
            
            # Supporting Documents section
            if event.get("doc_name") or event.get("doc_sum"):
                st.markdown("### 📄 Supporting Documents")
                
                for i, pdf_name in enumerate(event.get("doc_name", [])):
                    source_text = event.get("doc_sum", [""])[i] if i < len(event.get("doc_sum", [])) else ""

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

# VISUALIZE END #####################
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

if __name__ == "__main__":
    # Load data using the cache function for testing
    data = load_data()
    visualize(data)
