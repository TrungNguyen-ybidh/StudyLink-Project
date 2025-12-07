import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

advisor_name = st.session_state.get("user_name", "Advisor")

st.title(f"My Students – {advisor_name}")

st.subheader("My Students")

# Define columns you want in the table
columns = [
    "studentID",
    "First Name",
    "Last Name",
    "Email",
    "Major",
    "Minor",
    "GPA",
    "Risk Flag",
    "Enrollment Status",
    "Total Credits",
]

# Make an empty dataframe with just headers
import pandas as pd
empty_df = pd.DataFrame(columns=columns)

st.dataframe(empty_df, use_container_width=True)