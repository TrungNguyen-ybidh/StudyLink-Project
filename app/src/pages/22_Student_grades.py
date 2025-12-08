import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

# PAGE CONFIG
st.set_page_config(page_title="Grades", page_icon="📊", layout="wide")
SideBarLinks()

# Use Docker service name for container communication
API_BASE = "http://web-api:4000"
API = f"{API_BASE}/student/grades"

# AUTH CHECK
if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied. Students only.")
    st.stop()

student_id = st.session_state.get("studentID", 1)
student_name = st.session_state.get("name", "Student")

# HEADER
st.title(f"Grades Overview for {student_name}")
st.write("Track your grades, assignment progress, and estimated GPA.")


# ============================================
# API FUNCTIONS
# ============================================
@st.cache_data(ttl=10)
def fetch_grades(sid):
    """Fetch all grades for a student."""
    try:
        res = requests.get(API, params={"studentID": sid}, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

@st.cache_data(ttl=10)
def fetch_grade_summary(sid):
    """Fetch grade summary by course."""
    try:
        res = requests.get(f"{API}/summary", params={"studentID": sid}, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except:
        return []


# Helper function to safely convert to float
def safe_float(value, default=0.0):
    """Safely convert a value to float."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


# LOAD DATA
grades = fetch_grades(student_id)
summary = fetch_grade_summary(student_id)

st.divider()


# ============================================
# OVERALL STATS
# ============================================
st.subheader("Overall Performance")

if grades:
    df = pd.DataFrame(grades)
    
    # Convert percentageScore to numeric, handling any string issues
    if 'percentageScore' in df.columns:
        df['percentageScore'] = pd.to_numeric(df['percentageScore'], errors='coerce')
    
    if 'scoreReceived' in df.columns:
        df['scoreReceived'] = pd.to_numeric(df['scoreReceived'], errors='coerce')
    
    if 'maxScore' in df.columns:
        df['maxScore'] = pd.to_numeric(df['maxScore'], errors='coerce')
    
    if 'weight' in df.columns:
        df['weight'] = pd.to_numeric(df['weight'], errors='coerce')
    
    # Calculate overall stats
    total_assignments = len(df)
    graded_count = len(df[df['status'] == 'graded']) if 'status' in df.columns else 0
    
    # Average percentage - safely calculate
    if 'percentageScore' in df.columns:
        valid_percentages = df['percentageScore'].dropna()
        avg_percentage = valid_percentages.mean() if len(valid_percentages) > 0 else 0
    else:
        avg_percentage = 0
    
    # GPA calculation
    def pct_to_gpa(p):
        if pd.isna(p) or p is None:
            return None
        p = float(p)
        if p >= 93: return 4.0
        if p >= 90: return 3.7
        if p >= 87: return 3.3
        if p >= 83: return 3.0
        if p >= 80: return 2.7
        if p >= 77: return 2.3
        if p >= 73: return 2.0
        if p >= 70: return 1.7
        if p >= 67: return 1.3
        if p >= 63: return 1.0
        if p >= 60: return 0.7
        return 0.0
    
    if 'percentageScore' in df.columns:
        gpa_values = df['percentageScore'].dropna().apply(pct_to_gpa)
        estimated_gpa = gpa_values.mean() if len(gpa_values) > 0 else 0
    else:
        estimated_gpa = 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Assignments", total_assignments)
    with col2:
        st.metric("Graded", f"{graded_count}/{total_assignments}")
    with col3:
        st.metric("Average Score", f"{avg_percentage:.1f}%" if avg_percentage else "N/A")
    with col4:
        st.metric("Estimated GPA", f"{estimated_gpa:.2f}" if estimated_gpa else "N/A")

else:
    st.info("No grade data available.")

st.divider()


# ============================================
# COURSE SUMMARY CARDS
# ============================================
st.subheader("📚 Performance by Course")

if summary:
    # Create rows of 3 cards each
    for i in range(0, len(summary), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(summary):
                course = summary[i + j]
                avg_score = safe_float(course.get('averageScore'), 0)
                
                # Color based on score
                if avg_score >= 80:
                    color = "#27ae60"
                elif avg_score >= 70:
                    color = "#f39c12"
                elif avg_score >= 60:
                    color = "#e67e22"
                else:
                    color = "#e74c3c"
                
                graded = course.get('gradedAssignments', 0) or 0
                total = course.get('totalAssignments', 0) or 0
                progress = (graded / total * 100) if total > 0 else 0
                
                with col:
                    st.markdown(f"""
                    <div style="padding:20px; border-radius:12px; background:linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%); 
                                border:1px solid #e0e0e0; border-left:5px solid {color}; height:180px;">
                        <h4 style="margin:0 0 5px 0; color:#333;">{course.get('courseCode', 'N/A')}</h4>
                        <p style="margin:0 0 15px 0; color:#666; font-size:13px; height:35px; overflow:hidden;">
                            {course.get('courseName', 'Unknown Course')}
                        </p>
                        <h2 style="margin:0; color:{color};">{avg_score:.1f}%</h2>
                        <p style="margin:5px 0 0 0; color:#888; font-size:12px;">
                            {graded}/{total} assignments graded ({progress:.0f}%)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")  # Spacing
else:
    st.info("No course summary available.")

st.divider()


# ============================================
# DETAILED GRADES TABLE
# ============================================
st.subheader("All Assignment Grades")

if not grades:
    st.info("No grade data found.")
else:
    df = pd.DataFrame(grades)
    
    # Convert numeric columns
    numeric_cols = ['percentageScore', 'scoreReceived', 'maxScore', 'weight', 'weightedScore']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        courses = ["All Courses"]
        if 'courseName' in df.columns:
            courses += list(df['courseName'].dropna().unique())
        filter_course = st.selectbox("Filter by Course:", courses)
    
    with col2:
        statuses = ["All Statuses"]
        if 'status' in df.columns:
            statuses += list(df['status'].dropna().unique())
        filter_status = st.selectbox("Filter by Status:", statuses)
    
    with col3:
        types = ["All Types"]
        if 'assignmentType' in df.columns:
            types += list(df['assignmentType'].dropna().unique())
        filter_type = st.selectbox("Filter by Type:", types)
    
    # Apply filters
    filtered_df = df.copy()
    if filter_course != "All Courses":
        filtered_df = filtered_df[filtered_df['courseName'] == filter_course]
    if filter_status != "All Statuses":
        filtered_df = filtered_df[filtered_df['status'] == filter_status]
    if filter_type != "All Types":
        filtered_df = filtered_df[filtered_df['assignmentType'] == filter_type]
    
    st.write(f"Showing {len(filtered_df)} of {len(df)} assignments")
    
    # Display as styled cards
    for idx, row in filtered_df.iterrows():
        title = row.get('assignmentTitle', 'Untitled')
        course = row.get('courseName', 'N/A')
        course_code = row.get('courseCode', '')
        a_type = row.get('assignmentType', 'N/A')
        status = row.get('status', 'pending')
        score = safe_float(row.get('scoreReceived'), None)
        max_score = safe_float(row.get('maxScore'), 100)
        percentage = safe_float(row.get('percentageScore'), None)
        weight = row.get('weight')
        
        # Status colors
        status_colors = {
            'graded': '#27ae60',
            'submitted': '#3498db',
            'pending': '#e74c3c',
            'reviewing': '#f39c12'
        }
        status_color = status_colors.get(status, '#95a5a6')
        
        # Score display
        if score is not None and percentage is not None:
            score_display = f"{score:.0f}/{max_score:.0f} ({percentage:.1f}%)"
            score_color = '#27ae60' if percentage >= 70 else '#e74c3c'
        else:
            score_display = "Not graded"
            score_color = '#95a5a6'
        
        with st.container():
            col1, col2, col3 = st.columns([4, 2, 2])
            
            with col1:
                weight_str = f" • Weight: {safe_float(weight):.1f}%" if weight else ""
                st.markdown(f"""
                <div style="border-left:4px solid {status_color}; padding-left:12px;">
                    <strong style="font-size:15px;">{title}</strong><br>
                    <span style="color:#666; font-size:13px;">
                        {course_code} - {course} • {a_type.capitalize() if a_type else 'N/A'}{weight_str}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="text-align:center;">
                    <span style="background:{status_color}; color:white; padding:3px 10px; border-radius:12px; font-size:12px;">
                        {status.upper() if status else 'UNKNOWN'}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style="text-align:right;">
                    <strong style="color:{score_color}; font-size:16px;">{score_display}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()

st.divider()


# ============================================
# GPA CALCULATOR
# ============================================
st.subheader("🎓 GPA Scale Reference")

with st.expander("View GPA Scale"):
    gpa_data = {
        "Letter Grade": ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F"],
        "Percentage": ["93-100", "90-92", "87-89", "83-86", "80-82", "77-79", "73-76", "70-72", "67-69", "63-66", "60-62", "<60"],
        "GPA Points": [4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0, 0.7, 0.0]
    }
    gpa_df = pd.DataFrame(gpa_data)
    st.dataframe(gpa_df, use_container_width=True, hide_index=True)

# Refresh button
st.divider()
if st.button("🔄 Refresh Grades"):
    st.cache_data.clear()
    st.rerun()