import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

API_BASE = "http://web-api:4000/api/advisor"
advisor_id = st.session_state.get("advisor_id")
advisor_name = st.session_state.get("user_name", "Advisor")

st.title(f"My Reports – {advisor_name}")

if not advisor_id:
    st.error("No advisor ID found. Please return to the home page and log in again.")
    st.stop()

# Load reports
try:
    response = requests.get(f"{API_BASE}/{advisor_id}/reports", timeout=10)
    response.raise_for_status()
    reports = response.json()
except Exception as e:
    st.error(f"Error fetching reports: {str(e)}")
    st.stop()

st.subheader("My Reports")
if not reports:
    st.info("No reports created by you yet.")
else:
    for report in reports:
        st.markdown(f"### {report['title']}")
        st.markdown(f"*Created at: {report['created_at']}*")
        st.markdown(report['content'])
        st.markdown("---")

# New Report Form
st.subheader("Create New Report")

student_id_input = st.number_input("Student ID", min_value=1, step=1)
title_input = st.text_input("Report Title")
content_input = st.text_area("Report Content")

if st.button("Create Report", use_container_width=True):
    if not title_input or not content_input:
        st.error("Title and content are required.")
    else:
        payload = {
            "title": title_input,
            "content": content_input,
            "studentID": student_id_input
        }
        try:
            response = requests.post(f"{API_BASE}/{advisor_id}/reports", json=payload, timeout=10)
            if response.status_code == 201:
                st.success("Report created successfully!")
                st.experimental_rerun()
            else:
                st.error(f"Failed to create report: {response.status_code} {response.text}")
        except Exception as e:
            st.error(f"Error creating report: {str(e)}")
