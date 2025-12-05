import streamlit as st
from modules.nav import SideBarLinks

# Page configuration
st.set_page_config(
    page_title="Data Analyst Dashboard",
    page_icon="📊",
    layout="wide"
)

# Show sidebar navigation
SideBarLinks()

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get('role') != 'Data Analyst':
    st.warning("Access denied. This page is for Data Analysts only.")
    st.stop()

# Header section
st.markdown("""
<style>
    .analyst-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .quick-action {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .quick-action:hover {
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# Welcome header
st.markdown(f"""
<div class="analyst-header">
    <h1>📊 Welcome, {st.session_state.get('user_name', 'Data Analyst')}!</h1>
    <p style="font-size: 1.2rem; opacity: 0.9;">
        Data Analyst Dashboard - StudyLink Analytics Platform
    </p>
</div>
""", unsafe_allow_html=True)

# Quick stats row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="📈 Active Datasets", value="12", delta="+2 this week")

with col2:
    st.metric(label="👥 Students Tracked", value="156", delta="+8 new")

with col3:
    st.metric(label="⚠️ Data Errors", value="3", delta="-2 resolved")

with col4:
    st.metric(label="📋 Reports Generated", value="24", delta="+5 today")

st.divider()

# Quick Actions Section
st.subheader("🚀 Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Dashboard & Analytics")
    st.write("View study time, sleep patterns, and GPA trends across all students.")
    if st.button("Open Dashboard", key="dash_btn", use_container_width=True):
        st.switch_page("pages/31_Analytics_Dashboard.py")

with col2:
    st.markdown("### 📁 Dataset Management")
    st.write("Upload, manage, and archive datasets. Track upload history.")
    if st.button("Manage Datasets", key="dataset_btn", use_container_width=True):
        st.switch_page("pages/32_Dataset_Management.py")

with col3:
    st.markdown("### 🔧 Data Quality")
    st.write("Fix errors, correct metrics, and maintain data integrity.")
    if st.button("Data Quality Tools", key="quality_btn", use_container_width=True):
        st.switch_page("pages/33_Data_Quality.py")

st.divider()

# Recent Activity Section
st.subheader("📋 Recent Activity")

activity_data = [
    {"time": "2 hours ago", "action": "Dataset uploaded", "details": "Weekly Study Metrics - Nov 2025"},
    {"time": "5 hours ago", "action": "Metric corrected", "details": "Student #3 sleep hours updated"},
    {"time": "1 day ago", "action": "Report exported", "details": "Q4 Student Performance Summary"},
    {"time": "2 days ago", "action": "Dataset archived", "details": "Legacy Sleep Data 2024"},
]

for activity in activity_data:
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 4])
        with col1:
            st.caption(activity["time"])
        with col2:
            st.write(f"**{activity['action']}**")
        with col3:
            st.write(activity["details"])

st.divider()

# User Stories Coverage Info
with st.expander("ℹ️ Features Available"):
    st.markdown("""
    **This dashboard covers the following user stories:**
    
    1. **User Story 1.1** - Dashboard with study time, sleep, and GPA summaries
    2. **User Story 1.2** - Daily and weekly engagement trends
    3. **User Story 1.3** - Upload and manage datasets directly
    4. **User Story 1.4** - Fix or overwrite incorrect data entries
    5. **User Story 1.5** - Archive old datasets
    6. **User Story 1.6** - Export charts and summaries for advisors
    """)