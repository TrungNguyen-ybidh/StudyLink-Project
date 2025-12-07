import streamlit as st
import requests
from modules.nav import SideBarLinks

# PAGE SETUP
st.set_page_config(page_title="Courses", page_icon="📘", layout="wide")
SideBarLinks()

# Use Docker service name for container communication
API_BASE = "http://web-api:4000"
API = f"{API_BASE}/student/courses"

# AUTH CHECK
if not st.session_state.get("authenticated", False):
    st.warning("Please log in first.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied. Students only.")
    st.stop()

student_id = st.session_state.get("studentID", 1)
student_name = st.session_state.get("name", "Student")


# ============================================
# API FUNCTIONS
# ============================================
@st.cache_data(ttl=10)
def fetch_student_courses(sid):
    """Fetch courses enrolled by the student."""
    try:
        res = requests.get(API, params={"studentID": sid}, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

@st.cache_data(ttl=30)
def fetch_course_catalog():
    """Fetch all available courses in the catalog."""
    try:
        res = requests.get(f"{API}/catalog", timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except:
        return []

def add_course(sid, course_id):
    """Add a course to student's plan."""
    payload = {"studentID": sid, "courseID": course_id}
    return requests.post(API, json=payload, timeout=10)

def remove_course(sid, course_id):
    """Remove a course from student's plan."""
    return requests.delete(f"{API}/{sid}/{course_id}", timeout=10)


# LOAD DATA
student_courses = fetch_student_courses(student_id)
catalog = fetch_course_catalog()

# Get list of enrolled course IDs for filtering
enrolled_course_ids = [c.get('courseID') for c in student_courses]


# PAGE HEADER
st.title(f"📘 Course Management for {student_name}")
st.write("View enrolled courses, add new ones, or remove them from your plan.")

# Debug expander
with st.expander("🔧 Debug Info"):
    st.write(f"Student ID: {student_id}")
    st.write(f"Enrolled courses: {len(student_courses)}")
    st.write(f"Catalog courses: {len(catalog)}")
    if student_courses:
        st.json(student_courses[:2])

st.divider()


# ============================================
# COURSE STATS
# ============================================
if student_courses:
    col1, col2, col3 = st.columns(3)
    
    total_credits = sum(c.get('credits', 0) for c in student_courses)
    departments = list(set(c.get('department', 'Unknown') for c in student_courses))
    
    with col1:
        st.metric("Enrolled Courses", len(student_courses))
    with col2:
        st.metric("Total Credits", total_credits)
    with col3:
        st.metric("Departments", len(departments))

st.divider()


# ============================================
# ENROLLED COURSES
# ============================================
st.subheader("📚 Your Enrolled Courses")

if not student_courses:
    st.info("You are not enrolled in any courses yet. Add courses from the catalog below!")
else:
    # Group courses by term if available
    terms = {}
    for c in student_courses:
        term = c.get('termName', 'Unknown Term')
        if term not in terms:
            terms[term] = []
        terms[term].append(c)
    
    for term_name, courses in terms.items():
        st.markdown(f"#### 📅 {term_name}")
        
        for c in courses:
            course_id = c.get('courseID')
            course_code = c.get('courseCode', 'N/A')
            course_name = c.get('courseName', 'Unknown Course')
            department = c.get('department', 'N/A')
            credits = c.get('credits', 0)
            instructor = c.get('instructor', 'TBA')
            location = c.get('location', 'TBA')
            
            # Department colors
            dept_colors = {
                'Computer Science': '#3498db',
                'Mathematics': '#9b59b6',
                'Engineering': '#e67e22',
                'Business': '#27ae60',
                'Psychology': '#e91e63',
                'Biology': '#00bcd4'
            }
            dept_color = dept_colors.get(department, '#95a5a6')
            
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="padding:15px; border-radius:10px; background:#ffffff; 
                                border:1px solid #e0e0e0; border-left:5px solid {dept_color}; margin-bottom:10px;">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <h4 style="margin:0; color:#333;">{course_code} - {course_name}</h4>
                                <p style="margin:5px 0; color:#666; font-size:14px;">
                                    🏛️ {department} • 📊 {credits} credits
                                </p>
                                <p style="margin:0; color:#888; font-size:13px;">
                                    👨‍🏫 {instructor} • 📍 {location}
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.write("")  # Spacing
                    if st.button("🗑️ Drop", key=f"drop_{course_id}", help="Remove from your courses"):
                        res = remove_course(student_id, course_id)
                        if res.status_code == 200:
                            st.success(f"Dropped {course_code}!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Failed to drop: {res.text}")
        
        st.write("")  # Spacing between terms

st.divider()


# ============================================
# ADD COURSES FROM CATALOG
# ============================================
st.subheader("➕ Add Course from Catalog")

if not catalog:
    st.info("No courses available in the catalog.")
else:
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        departments = ["All Departments"] + list(set(c.get('department', 'Unknown') for c in catalog))
        filter_dept = st.selectbox("Filter by Department:", departments)
    
    with col2:
        terms = ["All Terms"] + list(set(c.get('termName', 'Unknown') for c in catalog if c.get('termName')))
        filter_term = st.selectbox("Filter by Term:", terms)
    
    # Filter catalog
    filtered_catalog = catalog.copy()
    if filter_dept != "All Departments":
        filtered_catalog = [c for c in filtered_catalog if c.get('department') == filter_dept]
    if filter_term != "All Terms":
        filtered_catalog = [c for c in filtered_catalog if c.get('termName') == filter_term]
    
    # Remove already enrolled courses
    available_courses = [c for c in filtered_catalog if c.get('courseID') not in enrolled_course_ids]
    
    st.write(f"Showing {len(available_courses)} available courses")
    
    if not available_courses:
        st.info("No available courses match your filters, or you're already enrolled in all of them.")
    else:
        # Display available courses
        for c in available_courses:
            course_id = c.get('courseID')
            course_code = c.get('courseCode', 'N/A')
            course_name = c.get('courseName', 'Unknown Course')
            department = c.get('department', 'N/A')
            credits = c.get('credits', 0)
            instructor = c.get('instructor', 'TBA')
            location = c.get('location', 'TBA')
            term = c.get('termName', 'N/A')
            
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style="padding:12px; border-radius:8px; background:#f8f9fa; border:1px solid #e0e0e0; margin-bottom:8px;">
                        <strong>{course_code} - {course_name}</strong><br>
                        <span style="color:#666; font-size:13px;">
                            {department} • {credits} credits • {instructor} • {term}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("➕ Add", key=f"add_{course_id}", type="primary"):
                        res = add_course(student_id, course_id)
                        if res.status_code == 201:
                            st.success(f"Added {course_code}!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            error_msg = res.json().get('error', res.text) if res.status_code == 400 else res.text
                            st.error(f"Failed: {error_msg}")

st.divider()


# ============================================
# QUICK ADD BY COURSE ID
# ============================================
st.subheader("🔢 Quick Add by Course ID")

with st.form("quick_add_form"):
    st.write("If you know the course ID, you can add it directly:")
    
    quick_course_id = st.number_input("Course ID:", min_value=1, step=1)
    
    if st.form_submit_button("Add Course", type="primary"):
        if quick_course_id in enrolled_course_ids:
            st.warning("You are already enrolled in this course.")
        else:
            res = add_course(student_id, quick_course_id)
            if res.status_code == 201:
                st.success("Course added successfully!")
                st.cache_data.clear()
                st.rerun()
            else:
                error_msg = res.json().get('error', res.text) if res.status_code == 400 else res.text
                st.error(f"Failed to add course: {error_msg}")

# Refresh button
st.divider()
if st.button("🔄 Refresh Courses"):
    st.cache_data.clear()
    st.rerun()