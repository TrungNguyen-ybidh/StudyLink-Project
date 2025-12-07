import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

API_BASE = "http://web-api:4000/api/advisor"

advisor_id = st.session_state.get("advisor_id")
advisor_name = st.session_state.get("user_name", "Advisor")

st.title(f"My Students – {advisor_name}")

if not advisor_id:
    st.error("No advisor ID found. Please return to the home page and log in again.")
    st.stop()

# Fetch students for this advisor
try:
    response = requests.get(f"{API_BASE}/{advisor_id}/students", timeout=10)
    response.raise_for_status()
    students = response.json()
except Exception as e:
    st.error(f"Error fetching students: {str(e)}")
    st.stop()

if not students:
    st.info("No students assigned to you yet.")
else:
    st.subheader("My Students")
    for student in students:
        st.markdown(
            f"- **{student['fName']} {student['lName']}** "
            f"(ID: {student['studentID']}, Email: {student['email']})"
        )
