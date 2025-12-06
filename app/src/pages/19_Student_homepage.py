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
        st.switch_page("pages/20_Calendar.py")

    if st.button("⏰ Reminders", use_container_width=True):
        st.switch_page("pages/21_Reminders.py")

with col2:
    if st.button("📝 Assignments", use_container_width=True):
        st.switch_page("pages/22_Assignments.py")

    if st.button("📊 Grades & Performance", use_container_width=True):
        st.switch_page("pages/23_Grades.py")

with col3:
    if st.button("🎭 Events", use_container_width=True):
        st.switch_page("pages/24_Events.py")

    if st.button("📈 Workload Insights", use_container_width=True):
        st.switch_page("pages/25_Workload.py")

st.divider()


# API Integration
st.subheader("Upcoming Deadlines")

try:
    api_url = "http://localhost:4000/calendar"
    response = requests.get(api_url, params={"studentID": st.session_state.get("studentID")})

    if response.status_code == 200:
        items = response.json()

        if items:
            for item in items[:5]: 
                st.write(f"• **{item['assignmentTitle']}** — due on **{item['dueDate']} at {item['dueTime']}**")
        else:
            st.info("No upcoming assignments.")
    else:
        st.error("Failed to load calendar data.")

except Exception as e:
    st.error(f"Error connecting to server: {e}")