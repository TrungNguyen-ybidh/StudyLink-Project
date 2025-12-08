import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(
    page_title="System Admin Home",
    page_icon="🛠️",
    layout="wide"
)

SideBarLinks()

# Auth check
if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get("role") != "System Admin":
    st.warning("Access denied. This page is for System Administrators only.")
    st.stop()

API_BASE = "http://web-api:4000"

user_name = st.session_state.get("user_name", "System Administrator")
admin_id = st.session_state.get("adminID", 1)

# Header styling
st.markdown(
    """
    <style>
      .admin-header{
        background: linear-gradient(135deg,#0f172a 0%,#334155 100%);
        padding:1.5rem;
        border-radius:16px;
        color:white;
        margin-bottom:1.25rem;
      }
      .stat-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #3498db;
      }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="admin-header">
      <h1 style="margin:0;">🛠️ Welcome, {user_name}!</h1>
      <p style="margin:0.5rem 0 0; opacity:0.9;">
        System Administrator — StudyLink Operations
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# Quick Stats
st.subheader("System Overview")

col1, col2, col3, col4 = st.columns(4)

try:
    # Get terms count
    terms_res = requests.get(f"{API_BASE}/terms", timeout=5)
    terms_count = len(terms_res.json()) if terms_res.status_code == 200 else 0
    
    # Get admins count
    admins_res = requests.get(f"{API_BASE}/admins", timeout=5)
    admins_count = len(admins_res.json()) if admins_res.status_code == 200 else 0

    with col1:
        st.metric("Active Terms", terms_count)
    with col2:
        st.metric("System Admins", admins_count)
    with col3:
        st.metric("Status", "🟢 Online")
    with col4:
        st.metric("API", "Connected")

except Exception as e:
    with col1:
        st.metric("Active Terms", "N/A")
    with col2:
        st.metric("System Admins", "N/A")
    with col3:
        st.metric("Status", "⚠️ Check API")
    with col4:
        st.metric("API", "Error")
    st.warning(f"Could not fetch stats: {e}")

st.divider()

# Quick Actions
st.subheader("🚀 Quick Actions")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 📅 Calendar Sync")
    st.write("Connect and verify student calendar sync status.")
    st.caption("Covers User Story 2.1")
    if st.button("Open Calendar Sync", use_container_width=True, type="primary"):
        st.switch_page("pages/42_Admin_Calendar_Sync.py")

with c2:
    st.markdown("### 📚 Term & Course Catalog")
    st.write("Create terms, upload courses, and preview the catalog.")
    st.caption("Covers User Story 2.2")
    if st.button("Open Term/Course Catalog", use_container_width=True, type="primary"):
        st.switch_page("pages/41_Admin_Term_Course_Catalog.py")

with c3:
    st.markdown("### 🧹 Data Quality & Reports")
    st.write("Log data issues, rebuild plans, and export usage reports.")
    st.caption("Covers User Stories 2.3-2.6")
    if st.button("Open Ops & Reports", use_container_width=True, type="primary"):
        st.switch_page("pages/43_Admin_Ops_Quality_Reports.py")

st.divider()

# API Test Section
st.subheader("🔌 API Connection Test")

with st.expander("Test API Endpoints"):
    test_endpoint = st.selectbox("Select Endpoint to Test:", [
        "/terms",
        "/admins",
        "/students/1/calendar",
        "/terms/1/courses"
    ])
    
    if st.button("Test Endpoint"):
        try:
            res = requests.get(f"{API_BASE}{test_endpoint}", timeout=10)
            st.write(f"**Status:** {res.status_code}")
            st.json(res.json())
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# User Stories Reference
with st.expander("ℹ️ System Administrator User Stories"):
    st.markdown("""
    | Story | Description |
    |-------|-------------|
    | **2.1** | Connect students' calendars and verify sync so class times appear reliably |
    | **2.2** | Upload and preview the term and course list so the semester is set up correctly |
    | **2.3** | Import sleep/grade files on a schedule so plans adjust to real-life patterns |
    | **2.4** | Fix data issues and rebuild selected students' plans |
    | **2.5** | Run a daily schedule health check so overlaps are caught early |
    | **2.6** | Export a weekly usage summary with chart and CSV |
    """)