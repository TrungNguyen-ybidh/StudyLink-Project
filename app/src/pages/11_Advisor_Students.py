import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

# PAGE CONFIG
st.set_page_config(page_title="My Students", page_icon="👥", layout="wide")
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

# Get advisor ID - either from session or lookup by email
advisor_id = st.session_state.get("advisorID")
advisor_name = st.session_state.get("user_name", "Advisor")
advisor_email = st.session_state.get("user_email")

# If advisorID not in session, look it up by email
if not advisor_id and advisor_email:
    try:
        lookup_res = requests.get(f"{API_BASE}/api/advisor/lookup/{advisor_email}", timeout=10)
        if lookup_res.status_code == 200:
            advisor_data = lookup_res.json()
            advisor_id = advisor_data.get("advisorID")
            # Save to session for future use
            st.session_state["advisorID"] = advisor_id
    except Exception as e:
        st.error(f"Could not look up advisor: {e}")

# Default to 1 if still not found
if not advisor_id:
    advisor_id = 1


# ============================================
# API FUNCTIONS
# ============================================
@st.cache_data(ttl=10)
def fetch_students(aid):
    """Fetch all students for an advisor."""
    try:
        url = f"{API_BASE}/api/advisor/{aid}/students"
        res = requests.get(url, timeout=10)
        return {
            "status": res.status_code,
            "url": url,
            "data": res.json() if res.status_code == 200 else [],
            "error": None
        }
    except Exception as e:
        return {
            "status": None,
            "url": f"{API_BASE}/api/advisor/{aid}/students",
            "data": [],
            "error": str(e)
        }


# LOAD DATA
result = fetch_students(advisor_id)
students = result["data"]


# PAGE HEADER
st.title(f"My Students — {advisor_name}")
st.write("View and manage students assigned to you.")

st.divider()


# ============================================
# STUDENT STATS
# ============================================
if students:
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate stats
    total = len(students)
    at_risk = len([s for s in students if s.get('riskFlag')])
    avg_gpa = sum(float(s.get('GPA', 0) or 0) for s in students) / total if total > 0 else 0
    enrolled = len([s for s in students if s.get('enrollmentStatus') == 'Enrolled' or s.get('enrollmentStatus') == 'Active'])
    
    with col1:
        st.metric("Total Students", total)
    with col2:
        st.metric("At Risk", at_risk, delta=None if at_risk == 0 else f"{at_risk} need attention", delta_color="inverse")
    with col3:
        st.metric("Average GPA", f"{avg_gpa:.2f}")
    with col4:
        st.metric("Active/Enrolled", enrolled)

st.divider()


# ============================================
# FILTER OPTIONS
# ============================================
st.subheader("🔍 Filter Students")

col1, col2, col3 = st.columns(3)

with col1:
    # Risk filter
    risk_filter = st.selectbox("Risk Status:", ["All", "At Risk", "Not At Risk"])

with col2:
    # Status filter
    statuses = ["All"]
    if students:
        statuses += list(set(s.get('enrollmentStatus', 'Unknown') for s in students))
    status_filter = st.selectbox("Enrollment Status:", statuses)

with col3:
    # Major filter
    majors = ["All"]
    if students:
        majors += list(set(s.get('major', 'Unknown') for s in students if s.get('major')))
    major_filter = st.selectbox("Major:", majors)

# Apply filters
filtered_students = students.copy()

if risk_filter == "At Risk":
    filtered_students = [s for s in filtered_students if s.get('riskFlag')]
elif risk_filter == "Not At Risk":
    filtered_students = [s for s in filtered_students if not s.get('riskFlag')]

if status_filter != "All":
    filtered_students = [s for s in filtered_students if s.get('enrollmentStatus') == status_filter]

if major_filter != "All":
    filtered_students = [s for s in filtered_students if s.get('major') == major_filter]

st.write(f"Showing {len(filtered_students)} of {len(students)} students")

st.divider()


# ============================================
# DISPLAY STUDENTS
# ============================================
st.subheader("Student List")

if not filtered_students:
    st.info("No students found matching your filters.")
else:
    for student in filtered_students:
        student_id = student.get('studentID')
        fname = student.get('fName', '')
        lname = student.get('lName', '')
        email = student.get('email', 'N/A')
        major = student.get('major', 'Undeclared')
        minor = student.get('minor', '')
        gpa = float(student.get('GPA', 0) or 0)
        risk_flag = student.get('riskFlag', False)
        status = student.get('enrollmentStatus', 'Unknown')
        credits = student.get('totalCredits', 0)
        year = student.get('enrollmentYear', 'N/A')
        
        # GPA color
        if gpa >= 3.5:
            gpa_color = "#27ae60"
        elif gpa >= 2.5:
            gpa_color = "#f39c12"
        else:
            gpa_color = "#e74c3c"
        
        # Risk indicator
        risk_badge = "🔴 At Risk" if risk_flag else "🟢 Good Standing"
        risk_color = "#e74c3c" if risk_flag else "#27ae60"
        
        with st.container():
            col1, col2, col3 = st.columns([4, 2, 2])
            
            with col1:
                st.markdown(f"""
                <div style="padding:15px; border-radius:10px; background:#ffffff; 
                            border:1px solid #e0e0e0; border-left:5px solid {risk_color};">
                    <h4 style="margin:0;">{fname} {lname}</h4>
                    <p style="margin:5px 0; color:#666; font-size:14px;">
                        📧 {email}
                    </p>
                    <p style="margin:0; color:#888; font-size:13px;">
                        📚 {major} {f'• Minor: {minor}' if minor else ''} • 
                        🎓 Class of {year} • 
                        📊 {credits} credits
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="text-align:center; padding:10px;">
                    <h2 style="margin:0; color:{gpa_color};">{gpa:.2f}</h2>
                    <small style="color:#888;">GPA</small><br><br>
                    <span style="background:{'#ffebee' if risk_flag else '#e8f5e9'}; 
                                color:{risk_color}; padding:4px 10px; border-radius:12px; font-size:12px;">
                        {risk_badge}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="text-align:center; padding:10px;">
                    <span style="background:#e3f2fd; color:#1976d2; padding:4px 12px; 
                                border-radius:12px; font-size:12px;">
                        {status}
                    </span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📄 View Reports", key=f"reports_{student_id}"):
                    st.session_state["selected_student_id"] = student_id
                    st.session_state["selected_student_name"] = f"{fname} {lname}"
                    st.switch_page("pages/12_Advisor_Reports.py")
        
        st.write("")  # Spacing


# ============================================
# DATA TABLE VIEW
# ============================================
st.divider()
st.subheader("📊 Table View")

with st.expander("View as Data Table"):
    if students:
        df = pd.DataFrame(students)
        
        # Select and rename columns
        display_cols = {
            'studentID': 'ID',
            'fName': 'First Name',
            'lName': 'Last Name',
            'email': 'Email',
            'major': 'Major',
            'minor': 'Minor',
            'GPA': 'GPA',
            'riskFlag': 'At Risk',
            'enrollmentStatus': 'Status',
            'totalCredits': 'Credits'
        }
        
        available_cols = [c for c in display_cols.keys() if c in df.columns]
        df_display = df[available_cols].rename(columns=display_cols)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("No data to display.")


# Refresh button
st.divider()
if st.button("🔄 Refresh Students"):
    st.cache_data.clear()
    st.rerun()