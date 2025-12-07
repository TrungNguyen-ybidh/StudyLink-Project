import streamlit as st
import requests
from modules.nav import SideBarLinks


# PAGE CONFIG
st.set_page_config(
    page_title="Workload Analysis",
    page_icon="📚",
    layout="wide"
)

SideBarLinks()


# AUTH CHECK
if not st.session_state.get("authenticated", False):
    st.warning("Please log in first.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied — Students only.")
    st.stop()

API_WORKLOAD = "http://localhost:4000/student/workload"
API_SUMMARY = "http://localhost:4000/student/workload/summary"


# FETCH FUNCTIONS
@st.cache_data(ttl=5)
def fetch_workload(student_id):
    try:
        res = requests.get(API_WORKLOAD, params={"studentID": student_id})
        return res.json() if res.status_code == 200 else []
    except:
        return []


@st.cache_data(ttl=5)
def fetch_summary(student_id):
    try:
        res = requests.get(API_SUMMARY, params={"studentID": student_id})
        return res.json() if res.status_code == 200 else []
    except:
        return []


# PAGE HEADER
st.markdown("""
    <h1 style="margin-bottom:0;">📚 Workload Analysis</h1>
    <p style="margin-top:0; color:#666;">
        Weekly workload based on upcoming assignments and events.
    </p>
""", unsafe_allow_html=True)

st.markdown("---")


# INPUT: STUDENT ID
student_id = st.text_input("Enter your studentID:", value=st.session_state.get("studentID", ""))

if not student_id:
    st.info("Enter studentID to see workload.")
    st.stop()

# Fetch data
workload = fetch_workload(student_id)
summary = fetch_summary(student_id)


# WORKLOAD DISPLAY
st.subheader("📅 Weekly Workload Forecast")

if isinstance(workload, dict) and workload.get("error"):
    st.error(workload["error"])
    st.stop()

if not workload:
    st.info("No workload data found for this student.")
else:
    COLOR_MAP = {
        "Low-intensity": "#A8E6CF",
        "Moderate": "#FFD3B6",
        "High-intensity": "#FF8B94"
    }

    for row in workload:
        weekday = row.get("weekday", "Unknown")
        total_assignments = row.get("totalAssignments", 0)
        total_events = row.get("totalEvents", 0)
        category = row.get("workloadCategory", "Unknown")
        suggestion = row.get("suggestedAction", "")

        bg_color = COLOR_MAP.get(category, "#E0E0E0")

        st.markdown(
            f"""
            <div style="
                background:{bg_color};
                padding:15px;
                border-radius:10px;
                margin-bottom:10px;
            ">
                <h4 style="margin:0;">📆 {weekday}</h4>
                <p style="margin:5px 0;"><b>Assignments:</b> {total_assignments}</p>
                <p style="margin:5px 0;"><b>Events:</b> {total_events}</p>
                <p style="margin:5px 0;"><b>Intensity:</b> {category}</p>
                <p style="margin:5px 0; color:#555;"><i>{suggestion}</i></p>
            </div>
            """,
            unsafe_allow_html=True
        )


# STUDY SUMMARY SECTION
st.subheader("📘 Study Summary (Recent Periods)")

if isinstance(summary, dict) and summary.get("error"):
    st.error(summary["error"])
    st.stop()

if not summary:
    st.info("No study summary available.")
else:
    for s in summary:
        st.markdown(
            f"""
            <div style="
                padding:12px;
                background:#F4F6F7;
                border-radius:8px;
                margin-bottom:8px;
            ">
                <b>Period:</b> {s.get("periodStart")} → {s.get("periodEnd")}  
                <br><b>Total Study Hours:</b> {s.get("totalStudyHrs")}  
                <br><b>Avg Study Hours/day:</b> {s.get("avgStudyHrs")}  
                <br><b>Avg Sleep:</b> {s.get("avgSleep")} hrs  
                <br><b>GPA:</b> {s.get("GPA")}
            </div>
            """,
            unsafe_allow_html=True
        )
