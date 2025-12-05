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

# API base URL
API_BASE = "http://web-api:4000"

st.title("📊 Analytics Dashboard")
st.caption(f"Welcome back, {st.session_state.get('user_name', 'Analyst')}!")

# ============================================
# TOP METRICS SUMMARY (User Story 1.1)
# ============================================
st.markdown("### 📈 Platform Overview")

# Fetch aggregate summary
try:
    response = requests.get(f"{API_BASE}/data/dashboard/summary")
    if response.status_code == 200:
        summary = response.json()
    else:
        summary = None
except:
    summary = None

# Display summary metrics
col1, col2, col3, col4, col5 = st.columns(5)

if summary:
    with col1:
        st.metric("Total Students", summary.get('totalStudents', 0))
    with col2:
        st.metric("Average GPA", f"{summary.get('avgGPA', 0):.2f}")
    with col3:
        st.metric("Avg Study Hours", f"{summary.get('avgStudyHours', 0):.1f} hrs")
    with col4:
        st.metric("Avg Sleep", f"{summary.get('avgSleepHours', 0):.1f} hrs")
    with col5:
        st.metric("Students At Risk", summary.get('studentsAtRisk', 0), delta=None, delta_color="inverse")
else:
    # Sample data fallback
    with col1:
        st.metric("Total Students", 156)
    with col2:
        st.metric("Average GPA", "3.42")
    with col3:
        st.metric("Avg Study Hours", "4.2 hrs")
    with col4:
        st.metric("Avg Sleep", "6.8 hrs")
    with col5:
        st.metric("Students At Risk", 12, delta="+2 this week", delta_color="inverse")

st.divider()

# ============================================
# MAIN DASHBOARD CHARTS (User Story 1.1)
# ============================================
# Fetch dashboard data
try:
    response = requests.get(f"{API_BASE}/data/dashboard")
    if response.status_code == 200:
        dashboard_data = response.json()
    else:
        dashboard_data = []
except:
    dashboard_data = []

# Create two columns for charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### 📚 Study Time (hrs)")
    st.caption("Study time trends from the past week")
    
    if dashboard_data:
        df = pd.DataFrame(dashboard_data)
        if 'avgStudyHrs' in df.columns:
            fig = px.bar(
                df, 
                x='studentName' if 'studentName' in df.columns else df.index,
                y='avgStudyHrs',
                color='avgStudyHrs',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                showlegend=False,
                xaxis_title="",
                yaxis_title="Hours",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Sample data
        sample_dates = pd.date_range(end=datetime.now(), periods=12, freq='D')
        sample_study = [3.5, 4.2, 3.8, 5.1, 4.5, 3.2, 4.8, 5.2, 4.1, 3.9, 4.6, 5.0]
        sample_last_week = [3.2, 3.8, 3.5, 4.8, 4.2, 3.0, 4.5, 4.9, 3.8, 3.6, 4.3, 4.7]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=sample_dates[-6:],
            y=sample_study[-6:],
            name='Last 6 days',
            marker_color='#1E88E5'
        ))
        fig.add_trace(go.Bar(
            x=sample_dates[-6:],
            y=sample_last_week[-6:],
            name='Previous Week',
            marker_color='#90CAF9'
        ))
        fig.update_layout(
            barmode='group',
            height=300,
            xaxis_title="",
            yaxis_title="Hours",
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if st.button("📄 View Report", key="study_report"):
        st.info("Generating study time report...")

with chart_col2:
    st.markdown("#### 😴 AVG SLEEP (hrs)")
    st.caption("Sleep patterns over the past week")
    
    if dashboard_data:
        df = pd.DataFrame(dashboard_data)
        if 'avgSleep' in df.columns:
            fig = px.line(
                df,
                x='periodStart' if 'periodStart' in df.columns else df.index,
                y='avgSleep',
                markers=True
            )
            fig.update_traces(line_color='#7C4DFF')
            fig.update_layout(height=300, xaxis_title="", yaxis_title="Hours")
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Sample sleep data
        sample_dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
        sample_sleep = [7.2, 6.8, 7.5, 6.5, 7.0, 7.8, 6.9]
        sample_sleep_prev = [6.9, 6.5, 7.2, 6.2, 6.8, 7.5, 6.6]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sample_dates,
            y=sample_sleep,
            mode='lines+markers',
            name='Last 6 days',
            line=dict(color='#7C4DFF', width=2),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=sample_dates,
            y=sample_sleep_prev,
            mode='lines+markers',
            name='Previous Week',
            line=dict(color='#B39DDB', width=2, dash='dot'),
            marker=dict(size=6)
        ))
        fig.update_layout(
            height=300,
            xaxis_title="",
            yaxis_title="Hours",
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if st.button("📄 View Report", key="sleep_report"):
        st.info("Generating sleep report...")

# Second row of charts
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown("#### 🎓 Student's GPA Distribution")
    st.caption("GPA breakdown across all students")
    
    if dashboard_data:
        df = pd.DataFrame(dashboard_data)
        if 'GPA' in df.columns:
            gpa_ranges = pd.cut(df['GPA'], bins=[0, 2.5, 3.0, 3.5, 4.0], labels=['< 2.5', '2.5-3.0', '3.0-3.5', '3.5-4.0'])
            gpa_counts = gpa_ranges.value_counts()
            fig = px.pie(values=gpa_counts.values, names=gpa_counts.index, hole=0.4)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    else:
        # Sample GPA distribution
        gpa_data = {
            'Range': ['2.5 - 3.0', '3.0 - 3.5', '3.5 - 4.0'],
            'Count': [40, 32, 28],
            'Percentage': ['40%', '32%', '28%']
        }
        fig = px.pie(
            values=gpa_data['Count'],
            names=gpa_data['Range'],
            hole=0.4,
            color_discrete_sequence=['#FF7043', '#FFA726', '#66BB6A']
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    if st.button("📄 View Report", key="gpa_report"):
        st.info("Generating GPA report...")

with chart_col4:
    st.markdown("#### 📊 Weekly Engagement Trends")
    st.caption("Student activity over the past 4 weeks")
    
    # Sample engagement data
    weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
    metric_entries = [245, 312, 289, 356]
    events_attended = [45, 52, 48, 61]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weeks,
        y=metric_entries,
        name='Metric Entries',
        marker_color='#26A69A'
    ))
    fig.add_trace(go.Scatter(
        x=weeks,
        y=[m/5 for m in metric_entries],  # Scale for visibility
        mode='lines+markers',
        name='Avg per Student',
        yaxis='y2',
        line=dict(color='#FF7043', width=2)
    ))
    fig.update_layout(
        height=300,
        yaxis=dict(title='Total Entries'),
        yaxis2=dict(title='Avg per Student', overlaying='y', side='right'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

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
        ["Last 7 Days", "Last 14 Days", "Last 30 Days", "Custom"]
    )

with filter_col2:
    risk_filter = st.selectbox(
        "Risk Status",
        ["All Students", "At Risk Only", "Good Standing"]
    )

with filter_col3:
    major_filter = st.selectbox(
        "Major",
        ["All Majors", "Computer Science", "Biology", "Business", "Psychology"]
    )

# Fetch engagement data
try:
    response = requests.get(f"{API_BASE}/data/engagement")
    if response.status_code == 200:
        engagement_data = response.json()
    else:
        engagement_data = []
except:
    engagement_data = []

if engagement_data:
    engagement_df = pd.DataFrame(engagement_data)
    st.dataframe(engagement_df, use_container_width=True, hide_index=True)
else:
    # Sample engagement data
    sample_engagement = pd.DataFrame({
        'Student': ['John Doe', 'Jane Lee', 'Mark Chan', 'Sarah Kim', 'Tom Wilson'],
        'Date': ['2025-01-15', '2025-01-15', '2025-01-15', '2025-01-15', '2025-01-15'],
        'Study Hours': [4.5, 3.2, 1.5, 5.0, 2.8],
        'Metric Entries': [8, 6, 2, 10, 4],
        'Events Attended': [2, 1, 0, 3, 1],
        'Assignments': [3, 2, 1, 4, 2],
        'Avg Score': [92.5, 88.0, 75.0, 95.5, 82.0],
        'Days Since Sync': [0, 1, 5, 0, 2],
        'Status': ['Good', 'Good', 'At Risk', 'Good', 'Warning']
    })
    
    # Color code status
    def highlight_status(val):
        if val == 'At Risk':
            return 'background-color: #FFCDD2'
        elif val == 'Warning':
            return 'background-color: #FFF9C4'
        return 'background-color: #C8E6C9'
    
    st.dataframe(
        sample_engagement.style.applymap(highlight_status, subset=['Status']),
        use_container_width=True,
        hide_index=True
    )

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
                st.info("No data available for export")

with export_col2:
    with st.container(border=True):
        st.markdown("**📈 Engagement Report**")
        st.caption("Export engagement trends data")
        if st.button("Export Engagement CSV", use_container_width=True):
            st.info("Generating engagement report...")

with export_col3:
    with st.container(border=True):
        st.markdown("**🎓 Student Reports**")
        st.caption("Export comprehensive student reports")
        if st.button("Export All Student Reports", use_container_width=True):
            try:
                response = requests.get(f"{API_BASE}/data/students/reports")
                if response.status_code == 200:
                    reports = response.json()
                    df = pd.DataFrame(reports)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📥 Download",
                        csv,
                        f"student_reports_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
                else:
                    st.error("Failed to fetch reports")
            except Exception as e:
                st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data Analyst: {st.session_state.get('user_name', 'Jordan Lee')}")