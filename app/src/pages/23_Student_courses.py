import streamlit as st
import requests
from modules.nav import SideBarLinks


# PAGE SETUP
st.set_page_config(
    page_title="Courses",
    page_icon="📘",
    layout="wide"
)

SideBarLinks()

API = "http://localhost:4000/courses"    

# Auth checks
if not st.session_state.get("authenticated", False):
    st.warning("Please log in first.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied. Students only.")
    st.stop()

student_id = st.session_state.get("studentID")
student_name = st.session_state.get("user_name", "Student")


# HELPERS
@st.cache_data(ttl=5)
def fetch_student_courses(student_id):
    try: 
        res = requests.get(API, params={"studentID": student_id})
        return res.json() if res.status_code == 200 else []
    except:
        return []

@st.cache_data(ttl=5)
def fetch_course_catalog():
    try:
        res = requests.get(f"{API}/catalog")
        return res.json() if res.status_code == 200 else []
    except:
        return []

# Load data
student_courses = fetch_student_courses(student_id)
catalog = fetch_course_catalog()


# PAGE HEADER
st.markdown("""
    <h1 style="margin-bottom:0;">📘 Course Management</h1>
    <p style="color:#888; font-size:16px; margin-top:0;">
        View enrolled courses, add new ones, or remove them from your plan.
    </p>
""", unsafe_allow_html=True)

st.markdown("---")


# ADD COURSE (POST)
st.subheader("➕ Add a Course to Your Plan")

if not catalog:
    st.info("No courses available in the catalog.")
else:
    course_options = {
        f"{c['courseCode']} — {c['courseName']} ({c['department']})": c["courseID"]
        for c in catalog
    }

    selected = st.selectbox("Choose a course to add:", list(course_options.keys()))

    if st.button("Add Course", type="primary"):
        payload = {
            "studentID": student_id,
            "courseID": course_options[selected]
        }

        res = requests.post(API, json=payload)

        if res.status_code == 201:
            st.success("Course added successfully!")
            st.cache_data.clear()
        else:
            st.error(f"Failed to add course: {res.text}")

st.markdown("---")


# DISPLAY COURSES (GET) + DELETE
st.subheader("📚 Your Courses")

if not student_courses:
    st.info("You are not enrolled in any courses yet.")
else:
    for c in student_courses:
        with st.container(border=True):
            colA, colB = st.columns([6, 2])

            # COURSE DETAILS
            with colA:
                st.markdown(f"""
                    <h4 style="margin-bottom:2px;">{c['courseCode']} — {c['courseName']}</h4>
                    <p style="margin:0; color:#666;">
                        Dept: {c['department']} • Credits: {c['credits']}
                    </p>
                    <p style="margin:0; color:#777;">
                        Instructor: {c.get('instructor', 'N/A')} <br>
                        Term: {c.get('termName', 'N/A')}
                    </p>
                """, unsafe_allow_html=True)

            # DELETE COURSE
            with colB:
                if st.button("🗑️ Remove", key=f"delete_{c['courseID']}"):
                    res = requests.delete(f"{API}/{student_id}/{c['courseID']}")

                    if res.status_code == 200:
                        st.success("Course removed!")
                        st.cache_data.clear()
                    else:
                        st.error("Delete failed.")