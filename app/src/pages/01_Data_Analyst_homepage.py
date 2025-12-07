import streamlit as st
import requests
from modules.nav import SideBarLinks

# Page configuration
st.set_page_config(
    page_title="Data Analyst Home",
    page_icon="📊",
    layout="wide"
)

SideBarLinks()

# Authentication check
if not st.session_state.get('authenticated', False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get('role') != 'Data Analyst':
    st.warning("Access denied. This page is for Data Analysts only.")
    st.stop()

# API base URL
API_BASE = "http://web-api:8501"

# Header with custom styling
st.markdown("""
<style>
    .analyst-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="analyst-header">
    <h1>📊 Welcome, {st.session_state.get('user_name', 'Data Analyst')}!</h1>
    <p style="font-size: 1.2rem; opacity: 0.9;">
        StudyLink Data Analytics Platform
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# FETCH REAL DATA FROM API
# ============================================
# Based on rest_entry.py:
#   - analyst blueprint -> /analyst (dashboard, engagement, reports)
#   - metrics blueprint -> /data (metrics, data-errors)
#   - datasets blueprint -> /datasets (no prefix)

@st.cache_data(ttl=60)
def fetch_dashboard_summary():
    """Fetch from /analyst/dashboard/summary"""
    try:
        response = requests.get(f"{API_BASE}/analyst/dashboard/summary", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.session_state['api_error'] = str(e)
    return None

@st.cache_data(ttl=60)
def fetch_dashboard():
    """Fetch from /analyst/dashboard"""
    try:
        response = requests.get(f"{API_BASE}/analyst/dashboard", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.session_state['api_error'] = str(e)
    return []

@st.cache_data(ttl=60)
def fetch_datasets():
    """Fetch from /datasets (datasets blueprint has no prefix)"""
    try:
        response = requests.get(f"{API_BASE}/datasets", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.session_state['api_error'] = str(e)
    return []

@st.cache_data(ttl=60)
def fetch_data_errors():
    """Fetch from /data/data-errors (metrics blueprint)"""
    try:
        response = requests.get(f"{API_BASE}/data/data-errors", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.session_state['api_error'] = str(e)
    return []

@st.cache_data(ttl=60)
def fetch_metrics():
    """Fetch from /data/metrics (metrics blueprint)"""
    try:
        response = requests.get(f"{API_BASE}/data/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.session_state['api_error'] = str(e)
    return []

@st.cache_data(ttl=60)
def fetch_student_reports():
    """Fetch from /analyst/students/reports"""
    try:
        response = requests.get(f"{API_BASE}/analyst/students/reports", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.session_state['api_error'] = str(e)
    return []

# Load all data
summary = fetch_dashboard_summary()
dashboard_data = fetch_dashboard()
datasets = fetch_datasets()
data_errors = fetch_data_errors()
metrics = fetch_metrics()
student_reports = fetch_student_reports()

# ============================================
# QUICK STATS OVERVIEW WITH REAL DATA
# ============================================
st.markdown("### 📈 Quick Overview")

col1, col2, col3, col4 = st.columns(4)

# Calculate real metrics from dashboard data
# Dashboard returns student info with GPA, study hours, etc.
total_students = len(set(d.get('studentID') for d in dashboard_data if d.get('studentID'))) if dashboard_data else 0

# If no dashboard data, try to count from student reports
if total_students == 0 and student_reports:
    total_students = len(student_reports)

# Dataset counts
total_datasets = len(datasets) if datasets else 0
active_datasets = len([d for d in datasets if not str(d.get('category', '')).startswith('ARCHIVED')]) if datasets else 0

# Error counts
pending_errors = len([e for e in data_errors if e.get('errorStatus') in ['Pending', 'detected', None]]) if data_errors else 0
resolved_errors = len([e for e in data_errors if e.get('errorStatus') in ['Resolved', 'Corrected', 'corrected']]) if data_errors else 0
total_errors = len(data_errors) if data_errors else 0

# Calculate data quality score
total_metrics = len(metrics) if metrics else 0
if total_metrics > 0:
    quality_score = ((total_metrics - pending_errors) / total_metrics) * 100
    quality_score = min(100, max(0, quality_score))  # Clamp between 0-100
else:
    quality_score = 100.0

# Students at risk (from student reports or dashboard)
students_at_risk = 0
if student_reports:
    students_at_risk = len([s for s in student_reports if s.get('riskFlag') == 1])
elif dashboard_data:
    # Get unique students with riskFlag from dashboard
    risk_students = set()
    for d in dashboard_data:
        if d.get('riskFlag') == 1 and d.get('studentID'):
            risk_students.add(d.get('studentID'))
    students_at_risk = len(risk_students)

# Check if we have any data
has_data = any([summary, dashboard_data, datasets, data_errors, metrics])

with col1:
    with st.container(border=True):
        if total_students > 0:
            st.metric(
                "Active Students", 
                total_students,
                f"{students_at_risk} at risk" if students_at_risk > 0 else "0 at risk",
                delta_color="inverse" if students_at_risk > 0 else "off"
            )
        else:
            st.metric("Active Students", "—", "No data")
        
with col2:
    with st.container(border=True):
        if total_datasets > 0:
            st.metric(
                "Datasets Managed", 
                total_datasets,
                f"{active_datasets} active"
            )
        else:
            st.metric("Datasets Managed", "—", "No data")

with col3:
    with st.container(border=True):
        if total_metrics > 0:
            st.metric(
                "Data Quality Score", 
                f"{quality_score:.1f}%",
                f"{total_metrics} metrics"
            )
        else:
            st.metric("Data Quality Score", "—", "No metrics")

with col4:
    with st.container(border=True):
        st.metric(
            "Pending Issues", 
            pending_errors,
            f"{resolved_errors} resolved" if resolved_errors > 0 else None,
            delta_color="off"
        )

# Show connection status
if not has_data:
    st.warning("📡 Unable to connect to API. Make sure the backend is running on `web-api:4000`.")
    with st.expander("🔧 Debug Info"):
        st.code(f"""
API Base URL: {API_BASE}
Endpoints being called:
  - GET /analyst/dashboard/summary
  - GET /analyst/dashboard  
  - GET /datasets
  - GET /data/data-errors
  - GET /data/metrics
  - GET /analyst/students/reports
        """)
        if 'api_error' in st.session_state:
            st.error(f"Last error: {st.session_state['api_error']}")

st.divider()

# ============================================
# ADDITIONAL STATS ROW
# ============================================
st.markdown("### 📊 Database Statistics")

stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)

# Get stats from summary endpoint or calculate from dashboard data
avg_gpa = 0
avg_study = 0
avg_sleep = 0

if summary:
    avg_gpa = summary.get('avgGPA', 0) or 0
    avg_study = summary.get('avgStudyHours', 0) or 0
    avg_sleep = summary.get('avgSleepHours', 0) or 0
elif dashboard_data:
    # Calculate averages from dashboard data
    gpas = [d.get('GPA') for d in dashboard_data if d.get('GPA')]
    study_hrs = [d.get('avgStudyHrs') for d in dashboard_data if d.get('avgStudyHrs')]
    sleep_hrs = [d.get('avgSleep') for d in dashboard_data if d.get('avgSleep')]
    
    avg_gpa = sum(gpas) / len(gpas) if gpas else 0
    avg_study = sum(study_hrs) / len(study_hrs) if study_hrs else 0
    avg_sleep = sum(sleep_hrs) / len(sleep_hrs) if sleep_hrs else 0

with stat_col1:
    with st.container(border=True):
        st.metric("Average GPA", f"{avg_gpa:.2f}" if avg_gpa > 0 else "—")

with stat_col2:
    with st.container(border=True):
        st.metric("Avg Study Hours", f"{avg_study:.1f} hrs" if avg_study > 0 else "—")

with stat_col3:
    with st.container(border=True):
        st.metric("Avg Sleep Hours", f"{avg_sleep:.1f} hrs" if avg_sleep > 0 else "—")

with stat_col4:
    with st.container(border=True):
        archived_datasets = total_datasets - active_datasets
        st.metric("Archived Datasets", archived_datasets if total_datasets > 0 else "—")

st.divider()

# ============================================
# NAVIGATION CARDS
# ============================================
st.markdown("### 🧭 Quick Navigation")

nav_col1, nav_col2 = st.columns(2)

with nav_col1:
    with st.container(border=True):
        st.markdown("### 📊 Analytics Dashboard")
        st.markdown("*User Stories 1.1, 1.2, 1.6*")
        st.markdown("""
        - View study time, sleep, and GPA summaries
        - Monitor daily and weekly engagement trends
        - Identify students falling behind
        - Export charts for presentations
        """)
        if st.button("Open Dashboard →", key="dashboard_btn", use_container_width=True, type="primary"):
            st.switch_page('pages/02_Data_Analyst_Dashboard.py')

with nav_col2:
    with st.container(border=True):
        st.markdown("### 📁 Dataset Management")
        st.markdown("*User Stories 1.3, 1.5*")
        st.markdown("""
        - Upload new CSV datasets
        - Manage and archive old datasets
        - Track upload history
        - Preview dataset contents
        """)
        if st.button("Manage Datasets →", key="datasets_btn", use_container_width=True, type="primary"):
            st.switch_page('pages/03_Dataset_Management.py')

nav_col3, nav_col4 = st.columns(2)

with nav_col3:
    with st.container(border=True):
        st.markdown("### 🔧 Data Quality Tools")
        st.markdown("*User Story 1.4*")
        st.markdown("""
        - Fix incorrect metric entries
        - Track and resolve data errors
        - Update student records
        - View audit logs
        """)
        if st.button("Quality Tools →", key="quality_btn", use_container_width=True, type="primary"):
            st.switch_page('pages/05_Data_Analyst_tools.py')

with nav_col4:
    with st.container(border=True):
        st.markdown("### 📄 Student Reports")
        st.markdown("*User Story 1.6*")
        st.markdown("""
        - Generate comprehensive student reports
        - Export for advisor presentations
        - View risk indicators
        - Track academic performance
        """)
        if st.button("View Reports →", key="reports_btn", use_container_width=True, type="primary"):
            st.switch_page('pages/02_Data_Analyst_Dashboard.py')

st.divider()

# ============================================
# RECENT ACTIVITY
# ============================================
st.markdown("### 🕐 Recent Activity")

activity_data = []

# Add recent errors
if data_errors:
    for error in data_errors[:2]:
        detected = error.get('detectedAt', '')
        if detected:
            detected = str(detected)[:10]
        activity_data.append({
            "Time": detected or 'Recently',
            "Action": f"Error: {error.get('errorStatus', 'detected')}",
            "Details": f"{error.get('errorType', 'Data issue')} (ID: {error.get('errorID', 'N/A')})"
        })

# Add dataset info
if datasets:
    for ds in datasets[:2]:
        created = ds.get('created_at', '')
        if created:
            created = str(created)[:10]
        activity_data.append({
            "Time": created or 'Recently',
            "Action": "Dataset",
            "Details": f"{ds.get('dataset_name', ds.get('name', 'Unknown'))} ({ds.get('category', 'N/A')})"
        })

# Fallback if no data
if not activity_data:
    activity_data = [
        {"Time": "—", "Action": "Waiting for data", "Details": "Connect to database to see activity"},
    ]

for activity in activity_data[:4]:
    with st.container(border=True):
        acol1, acol2, acol3 = st.columns([1, 2, 3])
        with acol1:
            st.caption(activity["Time"])
        with acol2:
            st.markdown(f"**{activity['Action']}**")
        with acol3:
            st.text(activity["Details"])

st.divider()

# ============================================
# USER STORIES INFO
# ============================================
with st.expander("ℹ️ Features & User Stories Coverage"):
    st.markdown("""
    **Jordan Lee (Data Analyst) - User Stories:**
    
    | Story | Description | Page |
    |-------|-------------|------|
    | **1.1** | Dashboard with study time, sleep, and GPA summaries | Analytics Dashboard |
    | **1.2** | Daily and weekly engagement trends | Analytics Dashboard |
    | **1.3** | Upload and manage datasets directly | Dataset Management |
    | **1.4** | Fix or overwrite incorrect data entries | Data Quality Tools |
    | **1.5** | Archive old datasets | Dataset Management |
    | **1.6** | Export charts and summaries for advisors | Analytics Dashboard |
    """)

# Footer with refresh
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col3:
    st.caption("StudyLink © 2025 | Team OurSQL | Northeastern University CS 3200")