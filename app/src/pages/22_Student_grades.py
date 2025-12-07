import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks


# PAGE CONFIG
st.set_page_config(page_title="Grades", page_icon="📘", layout="wide")
SideBarLinks()

API = "http://localhost:4000/student/grades"


# AUTH CHECK
if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied. Students only.")
    st.stop()

student_id = st.session_state.get("studentID")
student_name = st.session_state.get("user_name", "Student")


# HEADER
st.markdown(f"## 📘 Grades Overview for **{student_name}**")
st.write("Track your grades, assignment progress, and estimated GPA.")
st.divider()


# FETCH GRADES FROM API
@st.cache_data(ttl=5)
def fetch_grades(student_id):
    try:
        res = requests.get(API, params={"studentID": student_id})
        if res.status_code == 200:
            return res.json()
        return []
    except:
        return []

grades = fetch_grades(student_id)


# DISPLAY TABLE
st.subheader("📄 Course Grades")

if not grades:
    st.info("No grade data found.")
else:
    df = pd.DataFrame(grades)

    # rename fields for prettier UI
    df = df.rename(columns={
        "courseName": "Course Name",
        "courseCode": "Course",
        "assignmentTitle": "Assignment",
        "assignmentType": "Type",
        "scoreReceived": "Score",
        "maxScore": "Out Of",
        "weight": "Weight (%)",
        "status": "Status",
        "percentageScore": "Percentage",
        "weightedScore": "Weighted Score"
    })

    st.dataframe(df, use_container_width=True)

    st.divider()


    # STATS: Score averages
    st.subheader("📊 Performance Breakdown")

    pct_vals = df["Percentage"].dropna()
    avg_pct = pct_vals.mean() if len(pct_vals) > 0 else 0

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Average Assignment Score", f"{avg_pct:.2f}%")

    with col2:
        completed = df[df["Status"] == "graded"].shape[0]
        total = df.shape[0]
        st.metric("Graded Assignments", f"{completed}/{total}")


    st.divider()

    # GPA CALCULATION
    st.subheader("🎓 Estimated GPA")

    def pct_to_gpa(p):
        if p >= 93: return 4.0
        if p >= 90: return 3.7
        if p >= 87: return 3.3
        if p >= 83: return 3.0
        if p >= 80: return 2.7
        if p >= 77: return 2.3
        if p >= 73: return 2.0
        if p >= 70: return 1.7
        return 0.0

    df["GPA"] = df["Percentage"].apply(lambda p: pct_to_gpa(p) if pd.notnull(p) else None)

    estimated_gpa = df["GPA"].dropna().mean() if df["GPA"].notnull().any() else 0

    st.metric("Estimated GPA", f"{estimated_gpa:.2f}")
    st.caption("This is an estimated GPA using a standard 4.0 scale.")


# REFRESH
if st.button("🔄 Refresh Grades"):
    st.cache_data.clear()
    st.rerun()