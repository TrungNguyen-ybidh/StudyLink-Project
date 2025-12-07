import streamlit as st
import requests
from modules.nav import SideBarLinks
import pandas as pd

st.set_page_config(layout="wide")
SideBarLinks()

advisor_name = st.session_state.get("user_name", "Advisor")

st.title(f"My Reports – {advisor_name}")

st.subheader("My Reports")

report_columns = [
    "Report ID",
    "Student ID",
    "Title",
    "Created At",
    "Content Preview"
]

empty_reports_df = pd.DataFrame(columns=report_columns)

st.dataframe(empty_reports_df, use_container_width=True)


# Create New Report


st.subheader("Create New Report")

student_id_input = st.number_input("Student ID", min_value=1, step=1)
title_input = st.text_input("Report Title")
content_input = st.text_area("Report Content")

if st.button("Create Report", use_container_width=True):
    if not title_input or not content_input:
        st.error("Title and content are required.")
    else:
        st.success("Report created successfully!")