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

# Ensure studentID is set (default to 1 for Maya Johnson if not set)
if 'studentID' not in st.session_state:
    st.session_state['studentID'] = 1

student_id = st.session_state.get('studentID', 1)
student_name = st.session_state.get('name', 'Student')

# Page Content
st.title("🎓 Student Dashboard")
st.subheader(f"Welcome back, {student_name}!")

st.write("Use this dashboard to manage your assignments, reminders, events, grades, and workload insights.")

# Display current student ID for debugging
with st.expander("Session Info (Debug)"):
    st.write(f"Student ID: {student_id}")
    st.write(f"Student Name: {student_name}")
    st.write(f"Role: {st.session_state.get('role')}")

st.divider()

# Quick Stats Section
st.subheader("📊 Quick Overview")

API_BASE = "http://web-api:4000"  # Use Docker service name

col1, col2, col3, col4 = st.columns(4)

# Fetch quick stats
try:
    # Get courses count
    courses_res = requests.get(f"{API_BASE}/student/courses", params={"studentID": student_id}, timeout=5)
    courses_count = len(courses_res.json()) if courses_res.status_code == 200 else 0
    
    # Get upcoming assignments
    calendar_res = requests.get(f"{API_BASE}/student/calendar", params={"studentID": student_id}, timeout=5)
    calendar_items = calendar_res.json() if calendar_res.status_code == 200 else []
    assignments_count = len([i for i in calendar_items if i.get('itemType') == 'assignment'])
    events_count = len([i for i in calendar_items if i.get('itemType') == 'event'])
    
    # Get active reminders
    reminders_res = requests.get(f"{API_BASE}/student/reminders", params={"studentID": student_id}, timeout=5)
    reminders_count = len(reminders_res.json()) if reminders_res.status_code == 200 else 0

    with col1:
        st.metric("Enrolled Courses", courses_count)
    with col2:
        st.metric("Upcoming Assignments", assignments_count)
    with col3:
        st.metric("Upcoming Events", events_count)
    with col4:
        st.metric("Active Reminders", reminders_count)

except Exception as e:
    st.warning(f"Could not load stats: {e}")
    with col1:
        st.metric("Enrolled Courses", "N/A")
    with col2:
        st.metric("Upcoming Assignments", "N/A")
    with col3:
        st.metric("Upcoming Events", "N/A")
    with col4:
        st.metric("Active Reminders", "N/A")

st.divider()

# Quick Navigation Buttons
st.subheader("🚀 Quick Navigation")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📅 View Calendar", use_container_width=True):
        st.switch_page("pages/20_Student_calendar.py")

    if st.button("⏰ Reminders", use_container_width=True):
        st.switch_page("pages/21_Student_reminder.py")

with col2:
    if st.button("📊 Grades", use_container_width=True):
        st.switch_page("pages/22_Student_grades.py")

    if st.button("📘 Courses", use_container_width=True):
        st.switch_page("pages/23_Student_courses.py")

with col3:
    if st.button("🎭 Events", use_container_width=True):
        st.switch_page("pages/24_Student_events.py")

    if st.button("📈 Workload Insights", use_container_width=True):
        st.switch_page("pages/25_Student_workload.py")

st.divider()

# Recent Activity Preview
st.subheader("📋 Recent Calendar Items")

try:
    if calendar_items:
        for item in calendar_items[:5]:  # Show first 5 items
            item_type = "📝" if item.get('itemType') == 'assignment' else "📅"
            title = item.get('assignmentTitle', 'Unknown')
            due_date = item.get('dueDate', 'N/A')
            status = item.get('status', '')
            
            st.markdown(f"""
            <div style="padding:10px; border-radius:8px; background:#f8f9fa; margin-bottom:8px; border-left:4px solid #3498db;">
                <strong>{item_type} {title}</strong><br>
                <span style="color:#666;">Due: {due_date} {f'• Status: {status}' if status else ''}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No upcoming calendar items found.")
except Exception as e:
    st.warning(f"Could not load calendar preview: {e}")