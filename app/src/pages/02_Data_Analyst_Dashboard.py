import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.nav import SideBarLinks
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Analytics Dashboard",
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

# API base URL - connects to Flask backend
API_BASE = "http://web-api:4000"

st.title("📊 Analytics Dashboard")
st.caption(f"Welcome back, {st.session_state.get('user_name', 'Analyst')}!")

# ============================================
# TOP METRICS SUMMARY (User Story 1.1)
# ============================================
st.markdown("### 📈 Platform Overview")

# Fetch aggregate summary from /analyst/dashboard/summary
summary = None
summary_error = None
try:
    response = requests.get(f"{API_BASE}/analyst/dashboard/summary", timeout=5)
    if response.status_code == 200:
        summary = response.json()
    else:
        summary_error = f"API returned status {response.status_code}"
except requests.exceptions.ConnectionError:
    summary_error = "Cannot connect to API server"
except requests.exceptions.Timeout:
    summary_error = "API request timed out"
except Exception as e:
    summary_error = str(e)

# Display summary metrics
col1, col2, col3, col4, col5 = st.columns(5)

if summary:
    with col1:
        st.metric("Total Students", summary.get('totalStudents', 0))
    with col2:
        avg_gpa = summary.get('avgGPA', 0)
        st.metric("Average GPA", f"{float(avg_gpa):.2f}" if avg_gpa else "N/A")
    with col3:
        avg_study = summary.get('avgStudyHours', 0)
        st.metric("Avg Study Hours", f"{float(avg_study):.1f} hrs" if avg_study else "N/A")
    with col4:
        avg_sleep = summary.get('avgSleepHours', 0)
        st.metric("Avg Sleep", f"{float(avg_sleep):.1f} hrs" if avg_sleep else "N/A")
    with col5:
        st.metric("Students At Risk", summary.get('studentsAtRisk', 0), delta_color="inverse")
else:
    st.warning(f"Could not load summary data: {summary_error}")
    with col1:
        st.metric("Total Students", "—")
    with col2:
        st.metric("Average GPA", "—")
    with col3:
        st.metric("Avg Study Hours", "—")
    with col4:
        st.metric("Avg Sleep", "—")
    with col5:
        st.metric("Students At Risk", "—")

st.divider()

# ============================================
# MAIN DASHBOARD CHARTS (User Story 1.1)
# ============================================
# Fetch dashboard data from /analyst/dashboard
dashboard_data = []
dashboard_error = None
try:
    response = requests.get(f"{API_BASE}/analyst/dashboard", timeout=5)
    if response.status_code == 200:
        dashboard_data = response.json()
    else:
        dashboard_error = f"API returned status {response.status_code}"
except requests.exceptions.ConnectionError:
    dashboard_error = "Cannot connect to API server"
except Exception as e:
    dashboard_error = str(e)

# Create two columns for charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### 📚 Study Time (hrs)")
    st.caption("Study time trends from the past week")
    
    if dashboard_data and len(dashboard_data) > 0:
        df = pd.DataFrame(dashboard_data)
        if 'avgStudyHrs' in df.columns and 'studentName' in df.columns:
            # Filter out None values
            df_filtered = df[df['avgStudyHrs'].notna()]
            if not df_filtered.empty:
                fig = px.bar(
                    df_filtered, 
                    x='studentName',
                    y='avgStudyHrs',
                    color='avgStudyHrs',
                    color_continuous_scale='Blues',
                    labels={'avgStudyHrs': 'Avg Study Hours', 'studentName': 'Student'}
                )
                fig.update_layout(
                    showlegend=False,
                    xaxis_title="",
                    yaxis_title="Hours",
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No study hour data available")
        else:
            st.info("Study hour data format not as expected")
    else:
        if dashboard_error:
            st.warning(f"Could not load data: {dashboard_error}")
        else:
            st.info("No dashboard data available")

with chart_col2:
    st.markdown("#### 😴 AVG SLEEP (hrs)")
    st.caption("Sleep patterns over the past week")
    
    if dashboard_data and len(dashboard_data) > 0:
        df = pd.DataFrame(dashboard_data)
        if 'avgSleep' in df.columns:
            df_filtered = df[df['avgSleep'].notna()]
            if not df_filtered.empty:
                # Use studentName or periodStart for x-axis
                x_col = 'studentName' if 'studentName' in df.columns else df_filtered.index
                fig = px.line(
                    df_filtered,
                    x=x_col,
                    y='avgSleep',
                    markers=True,
                    labels={'avgSleep': 'Avg Sleep Hours'}
                )
                fig.update_traces(line_color='#7C4DFF')
                fig.update_layout(height=300, xaxis_title="", yaxis_title="Hours")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No sleep data available")
        else:
            st.info("Sleep data format not as expected")
    else:
        st.info("No dashboard data available")

# Second row of charts
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown("#### 🎓 Student's GPA Distribution")
    st.caption("GPA breakdown across all students")
    
    if dashboard_data and len(dashboard_data) > 0:
        df = pd.DataFrame(dashboard_data)
        if 'GPA' in df.columns:
            df_filtered = df[df['GPA'].notna()]
            if not df_filtered.empty:
                # Create GPA ranges
                gpa_ranges = pd.cut(
                    df_filtered['GPA'].astype(float), 
                    bins=[0, 2.0, 2.5, 3.0, 3.5, 4.0], 
                    labels=['< 2.0', '2.0-2.5', '2.5-3.0', '3.0-3.5', '3.5-4.0']
                )
                gpa_counts = gpa_ranges.value_counts().sort_index()
                fig = px.pie(
                    values=gpa_counts.values, 
                    names=gpa_counts.index, 
                    hole=0.4,
                    color_discrete_sequence=['#EF5350', '#FF7043', '#FFA726', '#66BB6A', '#26A69A']
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No GPA data available")
        else:
            st.info("GPA data not found in response")
    else:
        st.info("No dashboard data available")

with chart_col4:
    st.markdown("#### 📊 Weekly Engagement Trends")
    st.caption("Student activity metrics")
    
    # Fetch engagement data from /analyst/engagement
    engagement_data = []
    try:
        response = requests.get(f"{API_BASE}/analyst/engagement", timeout=5)
        if response.status_code == 200:
            engagement_data = response.json()
    except:
        pass
    
    if engagement_data and len(engagement_data) > 0:
        df = pd.DataFrame(engagement_data)
        if 'daily_metric_entries' in df.columns:
            # Group by week if week_number exists
            if 'week_number' in df.columns:
                weekly = df.groupby('week_number').agg({
                    'daily_metric_entries': 'sum',
                    'total_study_hours': 'sum'
                }).reset_index()
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=weekly['week_number'],
                    y=weekly['daily_metric_entries'],
                    name='Metric Entries',
                    marker_color='#26A69A'
                ))
                fig.update_layout(
                    height=300,
                    xaxis_title="Week",
                    yaxis_title="Total Entries"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Week data not available for grouping")
        else:
            st.info("Engagement data format not as expected")
    else:
        st.info("No engagement data available")

st.divider()

# ============================================
# ENGAGEMENT TRENDS TABLE (User Story 1.2)
# ============================================
st.markdown("### 📈 Daily Engagement Trends")
st.caption("Monitor student activity to identify those falling behind")

# Filters
filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 14 Days", "Last 30 Days"]
    )

with filter_col2:
    risk_filter = st.selectbox(
        "Risk Status",
        ["All Students", "At Risk Only", "Good Standing"]
    )

with filter_col3:
    if st.button("🔄 Refresh Data"):
        st.rerun()

# Fetch engagement data from /analyst/engagement
engagement_data = []
engagement_error = None
try:
    response = requests.get(f"{API_BASE}/analyst/engagement", timeout=5)
    if response.status_code == 200:
        engagement_data = response.json()
    else:
        engagement_error = f"API returned status {response.status_code}"
except requests.exceptions.ConnectionError:
    engagement_error = "Cannot connect to API server"
except Exception as e:
    engagement_error = str(e)

if engagement_data and len(engagement_data) > 0:
    engagement_df = pd.DataFrame(engagement_data)
    
    # Display available columns info
    st.caption(f"Showing {len(engagement_df)} engagement records")
    
    # Select relevant columns if they exist
    display_cols = []
    col_mapping = {
        'student_name': 'Student',
        'metric_date': 'Date',
        'total_study_hours': 'Study Hours',
        'daily_metric_entries': 'Metric Entries',
        'events_attended': 'Events',
        'assignments_submitted': 'Assignments',
        'avg_assignment_score': 'Avg Score',
        'days_since_last_sync': 'Days Since Sync'
    }
    
    for col in col_mapping.keys():
        if col in engagement_df.columns:
            display_cols.append(col)
    
    if display_cols:
        display_df = engagement_df[display_cols].copy()
        display_df.columns = [col_mapping[c] for c in display_cols]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.dataframe(engagement_df, use_container_width=True, hide_index=True)
else:
    if engagement_error:
        st.warning(f"Could not load engagement data: {engagement_error}")
    else:
        st.info("No engagement data available")

st.divider()

# ============================================
# STUDENT REPORTS SECTION (User Story 1.6)
# ============================================
st.markdown("### 📋 Student Reports")
st.caption("View individual student reports for advisor presentations")

# Fetch all student reports from /analyst/students/reports
reports_data = []
try:
    response = requests.get(f"{API_BASE}/analyst/students/reports", timeout=5)
    if response.status_code == 200:
        reports_data = response.json()
except:
    pass

if reports_data and len(reports_data) > 0:
    reports_df = pd.DataFrame(reports_data)
    
    # Add status styling
    def get_status_color(status):
        if status == 'At Risk':
            return 'background-color: #FFCDD2'
        elif status == 'Warning':
            return 'background-color: #FFF9C4'
        return 'background-color: #C8E6C9'
    
    st.dataframe(reports_df, use_container_width=True, hide_index=True)
    
    # Individual student report viewer
    st.markdown("---")
    st.markdown("#### View Detailed Student Report")
    
    if 'studentID' in reports_df.columns:
        student_ids = reports_df['studentID'].tolist()
        student_names = reports_df['student_name'].tolist() if 'student_name' in reports_df.columns else student_ids
        
        student_options = {f"{name} (ID: {sid})": sid for name, sid in zip(student_names, student_ids)}
        selected = st.selectbox("Select Student", list(student_options.keys()))
        
        if selected and st.button("📄 View Full Report"):
            student_id = student_options[selected]
            try:
                response = requests.get(f"{API_BASE}/analyst/students/{student_id}/report", timeout=5)
                if response.status_code == 200:
                    report = response.json()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Basic Information**")
                        st.write(f"Name: {report.get('student_name', 'N/A')}")
                        st.write(f"Email: {report.get('email', 'N/A')}")
                        st.write(f"Major: {report.get('major', 'N/A')}")
                        st.write(f"Minor: {report.get('minor', 'N/A')}")
                        st.write(f"GPA: {report.get('GPA', 'N/A')}")
                    
                    with col2:
                        st.markdown("**Academic Status**")
                        st.write(f"Status: {report.get('status_summary', 'N/A')}")
                        st.write(f"Advisor: {report.get('advisor_name', 'N/A')}")
                        st.write(f"Enrolled Courses: {report.get('enrolled_courses', 'N/A')}")
                        st.write(f"Avg Assignment Score: {report.get('avg_assignment_score', 'N/A')}")
                else:
                    st.error("Could not fetch student report")
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("No student reports available")

st.divider()

# ============================================
# EXPORT SECTION (User Story 1.6)
# ============================================
st.markdown("### 📤 Export Reports")
st.caption("Generate and export reports for advisor presentations")

export_col1, export_col2, export_col3 = st.columns(3)

with export_col1:
    with st.container(border=True):
        st.markdown("**📊 Dashboard Summary**")
        st.caption("Export current dashboard metrics")
        if st.button("Export Dashboard CSV", use_container_width=True):
            if dashboard_data:
                df = pd.DataFrame(dashboard_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download",
                    csv,
                    f"dashboard_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            else:
                st.warning("No data available for export")

with export_col2:
    with st.container(border=True):
        st.markdown("**📈 Engagement Report**")
        st.caption("Export engagement trends data")
        if st.button("Export Engagement CSV", use_container_width=True):
            if engagement_data:
                df = pd.DataFrame(engagement_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download",
                    csv,
                    f"engagement_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            else:
                st.warning("No data available for export")

with export_col3:
    with st.container(border=True):
        st.markdown("**🎓 Student Reports**")
        st.caption("Export comprehensive student reports")
        if st.button("Export All Student Reports", use_container_width=True):
            if reports_data:
                df = pd.DataFrame(reports_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download",
                    csv,
                    f"student_reports_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            else:
                st.warning("No data available for export")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data Analyst: {st.session_state.get('user_name', 'Jordan Lee')}")