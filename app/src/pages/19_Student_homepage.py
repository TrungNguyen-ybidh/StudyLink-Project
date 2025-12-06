import streamlit as st
import requests
from modules.nav import SideBarLinks


# Page Configuration
st.set_page_config(
    page_title="Student Home",
    page_icon="📚",
    layout="wide"
)

# Sidebar links
SideBarLinks()

# Authentication Check
if not st.session_state.get('authenticated', False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get('role') != 'Student':
    st.warning("Access denied. This page is for Students only.")
    st.stop()


# Page Content
st.title("🎓 Student Dashboard")
st.subheader(f"Welcome back, {st.session_state.get('name', 'Student')}!")

st.write("Use this dashboard to manage your assignments, reminders, events, grades, and workload insights.")

st.divider()


# Quick Navigation Buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📅 View Calendar", use_container_width=True):
        st.switch_page("pages/20_Student_calendar.py")

    if st.button("⏰ Reminders", use_container_width=True):
        st.switch_page("pages/21_Student_reminder.py")

with col2:
    if st.button("📊 Grades", use_container_width=True):
        st.switch_page("pages/22_Student_grades.py")

    if st.button("📝 Courses", use_container_width=True):
        st.switch_page("pages/23_Student_courses.py")

with col3:
    if st.button("🎭 Events", use_container_width=True):
        st.switch_page("pages/24_Student_events.py")

    if st.button("📈 Workload Insights", use_container_width=True):
        st.switch_page("pages/25_Student_workload.py")

st.divider()