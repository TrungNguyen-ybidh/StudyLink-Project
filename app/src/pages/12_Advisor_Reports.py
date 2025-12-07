import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

# PAGE CONFIG
st.set_page_config(page_title="My Reports", page_icon="📄", layout="wide")
SideBarLinks()

# Use Docker service name for container communication
API_BASE = "http://web-api:4000"

# AUTH CHECK
if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get("role") != "Advisor":
    st.warning("Access denied. Advisors only.")
    st.stop()

advisor_id = st.session_state.get("advisorID", 1)
advisor_name = st.session_state.get("name", "Advisor")


# ============================================
# API FUNCTIONS
# ============================================
@st.cache_data(ttl=10)
def fetch_reports(aid):
    """Fetch all reports for an advisor."""
    try:
        res = requests.get(f"{API_BASE}/api/advisor/{aid}/reports", timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

@st.cache_data(ttl=30)
def fetch_students(aid):
    """Fetch students for dropdown."""
    try:
        res = requests.get(f"{API_BASE}/api/advisor/{aid}/students", timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except:
        return []

def create_report(aid, payload):
    """Create a new report."""
    return requests.post(f"{API_BASE}/api/advisor/{aid}/reports", json=payload, timeout=10)

def update_report(report_id, payload):
    """Update an existing report."""
    return requests.put(f"{API_BASE}/api/advisor/reports/{report_id}", json=payload, timeout=10)

def delete_report(report_id):
    """Delete a report."""
    return requests.delete(f"{API_BASE}/api/advisor/reports/{report_id}", timeout=10)


# LOAD DATA
reports = fetch_reports(advisor_id)
students = fetch_students(advisor_id)


# PAGE HEADER
st.title(f"📄 My Reports — {advisor_name}")
st.write("View, create, and manage student reports.")

# Check if coming from student page
selected_student_id = st.session_state.get("selected_student_id")
selected_student_name = st.session_state.get("selected_student_name")

if selected_student_id:
    st.info(f"Viewing reports for: **{selected_student_name}** (ID: {selected_student_id})")
    # Clear selection after showing
    if st.button("Clear Filter"):
        del st.session_state["selected_student_id"]
        del st.session_state["selected_student_name"]
        st.rerun()

# Debug expander
with st.expander("🔧 Debug Info"):
    st.write(f"Advisor ID: {advisor_id}")
    st.write(f"Total reports: {len(reports)}")
    st.write(f"Students available: {len(students)}")
    if reports:
        st.json(reports[:2])

st.divider()


# ============================================
# REPORT STATS
# ============================================
if reports:
    col1, col2, col3, col4 = st.columns(4)
    
    # Count by type
    type_counts = {}
    for r in reports:
        t = r.get('type', 'other')
        type_counts[t] = type_counts.get(t, 0) + 1
    
    with col1:
        st.metric("Total Reports", len(reports))
    with col2:
        st.metric("Meeting Notes", type_counts.get('meeting_note', 0))
    with col3:
        st.metric("Academic", type_counts.get('academic', 0))
    with col4:
        st.metric("Risk Reports", type_counts.get('risk', 0))

st.divider()


# ============================================
# DISPLAY REPORTS
# ============================================
st.subheader("📋 All Reports")

# Filter options
col1, col2 = st.columns(2)

with col1:
    report_types = ["All Types", "meeting_note", "academic", "risk", "wellness"]
    filter_type = st.selectbox("Filter by Type:", report_types)

with col2:
    # Student filter
    student_options = {"All Students": None}
    for s in students:
        name = f"{s.get('fName', '')} {s.get('lName', '')}"
        student_options[name] = s.get('studentID')
    filter_student = st.selectbox("Filter by Student:", list(student_options.keys()))

# Apply filters
filtered_reports = reports.copy()

if filter_type != "All Types":
    filtered_reports = [r for r in filtered_reports if r.get('type') == filter_type]

if filter_student != "All Students":
    sid = student_options[filter_student]
    filtered_reports = [r for r in filtered_reports if r.get('studentID') == sid]

# If coming from student page, filter by that student
if selected_student_id:
    filtered_reports = [r for r in filtered_reports if r.get('studentID') == selected_student_id]

st.write(f"Showing {len(filtered_reports)} reports")

if not filtered_reports:
    st.info("No reports found. Create one below!")
else:
    # Report type colors
    TYPE_COLORS = {
        'meeting_note': '#3498db',
        'academic': '#27ae60',
        'risk': '#e74c3c',
        'wellness': '#9b59b6'
    }
    
    for report in filtered_reports:
        report_id = report.get('reportID')
        student_name = report.get('studentName', 'Unknown Student')
        student_id = report.get('studentID')
        report_desc = report.get('reportDesc', '')
        description = report.get('description', '')
        report_type = report.get('type', 'other')
        date_created = report.get('dateCreated', 'N/A')
        
        type_color = TYPE_COLORS.get(report_type, '#95a5a6')
        
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div style="padding:15px; border-radius:10px; background:#ffffff; 
                            border:1px solid #e0e0e0; border-left:5px solid {type_color}; margin-bottom:5px;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <h4 style="margin:0;">📄 {report_desc or 'No Title'}</h4>
                            <p style="margin:5px 0; color:#666; font-size:14px;">
                                👤 {student_name} (ID: {student_id})
                            </p>
                        </div>
                        <span style="background:{type_color}; color:white; padding:3px 10px; 
                                    border-radius:12px; font-size:11px; text-transform:uppercase;">
                            {report_type.replace('_', ' ')}
                        </span>
                    </div>
                    <p style="margin:10px 0 5px 0; color:#555; font-size:13px;">
                        {description[:200] + '...' if description and len(description) > 200 else description or 'No description'}
                    </p>
                    <small style="color:#888;">📅 Created: {date_created[:10] if date_created else 'N/A'}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.write("")  # Spacing
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("✏️", key=f"edit_{report_id}", help="Edit report"):
                        st.session_state["edit_report_id"] = report_id
                        st.session_state["edit_report_data"] = report
                        st.rerun()
                with btn_col2:
                    if st.button("🗑️", key=f"delete_{report_id}", help="Delete report"):
                        res = delete_report(report_id)
                        if res.status_code == 200:
                            st.success("Report deleted!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {res.text}")
        
        st.write("")  # Spacing

st.divider()


# ============================================
# EDIT REPORT (if selected)
# ============================================
if "edit_report_id" in st.session_state:
    st.subheader(f"✏️ Edit Report #{st.session_state['edit_report_id']}")
    
    edit_data = st.session_state.get("edit_report_data", {})
    
    with st.form("edit_report_form"):
        edit_desc = st.text_input("Report Title/Description", value=edit_data.get('reportDesc', ''))
        edit_type = st.selectbox(
            "Report Type",
            ["meeting_note", "academic", "risk", "wellness"],
            index=["meeting_note", "academic", "risk", "wellness"].index(
                edit_data.get('type', 'meeting_note')
            ) if edit_data.get('type') in ["meeting_note", "academic", "risk", "wellness"] else 0
        )
        edit_description = st.text_area("Detailed Description", value=edit_data.get('description', ''), height=150)
        
        col1, col2 = st.columns(2)
        with col1:
            save_btn = st.form_submit_button("💾 Save Changes", type="primary")
        with col2:
            cancel_btn = st.form_submit_button("❌ Cancel")
        
        if save_btn:
            payload = {
                "reportDesc": edit_desc,
                "type": edit_type,
                "description": edit_description
            }
            
            res = update_report(st.session_state['edit_report_id'], payload)
            
            if res.status_code == 200:
                st.success("Report updated!")
                del st.session_state["edit_report_id"]
                del st.session_state["edit_report_data"]
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Update failed: {res.text}")
        
        if cancel_btn:
            del st.session_state["edit_report_id"]
            del st.session_state["edit_report_data"]
            st.rerun()
    
    st.divider()


# ============================================
# CREATE NEW REPORT
# ============================================
st.subheader("➕ Create New Report")

with st.form("create_report_form"):
    # Student selection
    if students:
        student_options_create = {
            f"{s.get('fName', '')} {s.get('lName', '')} (ID: {s.get('studentID')})": s.get('studentID')
            for s in students
        }
        selected = st.selectbox("Select Student:", list(student_options_create.keys()))
        new_student_id = student_options_create[selected]
    else:
        new_student_id = st.number_input("Student ID:", min_value=1, step=1)
    
    new_desc = st.text_input("Report Title/Description", placeholder="e.g., Weekly Check-in, Academic Progress Review")
    
    new_type = st.selectbox(
        "Report Type",
        ["meeting_note", "academic", "risk", "wellness"],
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    new_description = st.text_area(
        "Detailed Description",
        placeholder="Enter detailed notes about the student meeting, academic progress, concerns, etc.",
        height=150
    )
    
    submitted = st.form_submit_button("📝 Create Report", type="primary")
    
    if submitted:
        if not new_desc:
            st.error("Please enter a report title/description.")
        else:
            payload = {
                "studentID": new_student_id,
                "reportDesc": new_desc,
                "type": new_type,
                "description": new_description
            }
            
            res = create_report(advisor_id, payload)
            
            if res.status_code == 201:
                st.success("Report created successfully!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Error creating report: {res.text}")


# Refresh button
st.divider()
if st.button("🔄 Refresh Reports"):
    st.cache_data.clear()
    st.rerun()