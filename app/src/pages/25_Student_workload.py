import streamlit as st
import requests
from modules.nav import SideBarLinks

# PAGE CONFIG
st.set_page_config(page_title="Workload Analysis", page_icon="📈", layout="wide")
SideBarLinks()

# Use Docker service name for container communication
API_BASE = "http://web-api:4000"
API_WORKLOAD = f"{API_BASE}/student/workload"
API_SUMMARY = f"{API_BASE}/student/workload/summary"

# AUTH CHECK
if not st.session_state.get("authenticated", False):
    st.warning("Please log in first.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied. Students only.")
    st.stop()

student_id = st.session_state.get("studentID", 1)
student_name = st.session_state.get("name", "Student")


# ============================================
# API FUNCTIONS
# ============================================
@st.cache_data(ttl=10)
def fetch_workload(sid):
    """Fetch weekly workload analysis for a student."""
    try:
        res = requests.get(API_WORKLOAD, params={"studentID": sid}, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        st.error(f"Workload API Error: {e}")
        return []

@st.cache_data(ttl=10)
def fetch_summary(sid):
    """Fetch study summary for a student."""
    try:
        res = requests.get(API_SUMMARY, params={"studentID": sid}, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        st.error(f"Summary API Error: {e}")
        return []


# LOAD DATA
workload = fetch_workload(student_id)
summary = fetch_summary(student_id)


# PAGE HEADER
st.title(f"Workload Analysis for {student_name}")
st.write("Understand your weekly workload and study patterns to plan better.")

st.divider()


# ============================================
# WEEKLY WORKLOAD OVERVIEW
# ============================================
st.subheader("This Week's Workload Forecast")

# Workload intensity colors
INTENSITY_STYLES = {
    "Low-intensity": {"color": "#A8E6CF", "emoji": "😌", "bg": "#E8F8F5"},
    "Moderate": {"color": "#FFD93D", "emoji": "📚", "bg": "#FEF9E7"},
    "High-intensity": {"color": "#FF6B6B", "emoji": "🔥", "bg": "#FDEDEC"}
}

if not workload:
    st.info("No workload data available for this week.")
else:
    # Calculate overall stats
    total_assignments = sum(w.get('totalAssignments', 0) for w in workload)
    total_events = sum(w.get('totalEvents', 0) for w in workload)
    high_days = len([w for w in workload if w.get('workloadCategory') == 'High-intensity'])
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Assignments", total_assignments)
    with col2:
        st.metric("Total Events", total_events)
    with col3:
        st.metric("High-Intensity Days", high_days)
    with col4:
        avg_items = (total_assignments + total_events) / 7 if workload else 0
        st.metric("Avg Items/Day", f"{avg_items:.1f}")
    
    st.write("")
    
    # Weekly grid view
    st.markdown("#### Daily Breakdown")
    
    # Create 7 columns for days
    cols = st.columns(7)
    
    # Sort workload by day number
    sorted_workload = sorted(workload, key=lambda x: x.get('dayNum', 0))
    
    for i, day_data in enumerate(sorted_workload):
        if i < 7:
            weekday = day_data.get('weekday', 'Unknown')
            assignments = day_data.get('totalAssignments', 0)
            events = day_data.get('totalEvents', 0)
            category = day_data.get('workloadCategory', 'Low-intensity')
            suggestion = day_data.get('suggestedAction', '')
            
            style = INTENSITY_STYLES.get(category, INTENSITY_STYLES['Low-intensity'])
            
            with cols[i]:
                st.markdown(f"""
                <div style="background:{style['bg']}; border:2px solid {style['color']}; 
                            border-radius:12px; padding:15px; text-align:center; min-height:200px;">
                    <h4 style="margin:0; color:#333;">{weekday[:3]}</h4>
                    <div style="font-size:30px; margin:10px 0;">{style['emoji']}</div>
                    <p style="margin:5px 0; font-size:13px; color:#666;">
                        {assignments} assignments<br>
                        {events} events
                    </p>
                    <span style="background:{style['color']}; color:{'#333' if category != 'High-intensity' else '#fff'}; 
                                padding:3px 8px; border-radius:10px; font-size:11px;">
                        {category}
                    </span>
                </div>
                """, unsafe_allow_html=True)
    
    st.write("")
    
    # Detailed daily breakdown
    st.markdown("#### Detailed Daily View")
    
    for day_data in sorted_workload:
        weekday = day_data.get('weekday', 'Unknown')
        assignments = day_data.get('totalAssignments', 0)
        events = day_data.get('totalEvents', 0)
        category = day_data.get('workloadCategory', 'Low-intensity')
        suggestion = day_data.get('suggestedAction', '')
        
        style = INTENSITY_STYLES.get(category, INTENSITY_STYLES['Low-intensity'])
        
        with st.container():
            col1, col2 = st.columns([4, 2])
            
            with col1:
                st.markdown(f"""
                <div style="background:{style['bg']}; padding:15px; border-radius:10px; 
                            border-left:5px solid {style['color']}; margin-bottom:10px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:24px;">{style['emoji']}</span>
                        <div>
                            <h4 style="margin:0;">{weekday}</h4>
                            <p style="margin:5px 0 0 0; color:#666; font-size:14px;">
                                {assignments} assignment(s) • {events} event(s)
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="padding:15px; text-align:center;">
                    <span style="background:{style['color']}; color:{'#333' if category != 'High-intensity' else '#fff'}; 
                                padding:5px 15px; border-radius:15px; font-size:12px;">
                        {category}
                    </span>
                    <p style="margin:10px 0 0 0; color:#888; font-size:12px; font-style:italic;">
                        {suggestion}
                    </p>
                </div>
                """, unsafe_allow_html=True)

st.divider()


# ============================================
# STUDY SUMMARY HISTORY
# ============================================
st.subheader("Study Summary History")

if not summary:
    st.info("No study summary data available yet.")
else:
    # Display summary stats
    if len(summary) > 0:
        latest = summary[0]
        
        st.markdown("#### Latest Period Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_hrs = latest.get('totalStudyHrs', 0) or 0
            st.metric("Total Study Hours", f"{total_hrs:.1f} hrs")
        with col2:
            avg_hrs = latest.get('avgStudyHrs', 0) or 0
            st.metric("Avg Study/Day", f"{avg_hrs:.1f} hrs")
        with col3:
            avg_sleep = latest.get('avgSleep', 0) or 0
            st.metric("Avg Sleep", f"{avg_sleep:.1f} hrs")
        with col4:
            gpa = latest.get('GPA', 0) or 0
            st.metric("Current GPA", f"{gpa:.2f}")
        
        st.write("")
    
    # Historical data
    st.markdown("#### Historical Summary")
    
    for s in summary:
        period_start = s.get('periodStart', 'N/A')
        period_end = s.get('periodEnd', 'N/A')
        total_hrs = s.get('totalStudyHrs', 0) or 0
        avg_hrs = s.get('avgStudyHrs', 0) or 0
        avg_sleep = s.get('avgSleep', 0) or 0
        gpa = s.get('GPA', 0) or 0
        fname = s.get('fName', '')
        lname = s.get('lName', '')
        
        # Color based on study hours
        if avg_hrs >= 4:
            color = "#27ae60"
        elif avg_hrs >= 2:
            color = "#f39c12"
        else:
            color = "#e74c3c"
        
        with st.container():
            st.markdown(f"""
            <div style="padding:15px; border-radius:10px; background:#f8f9fa; 
                        border-left:4px solid {color}; margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong style="font-size:14px;">{str(period_start)[:10]} → {str(period_end)[:10]}</strong>
                    </div>
                    <div style="text-align:right;">
                        <span style="background:{color}; color:white; padding:3px 10px; border-radius:10px; font-size:12px;">
                            {avg_hrs:.1f} hrs/day
                        </span>
                    </div>
                </div>
                <div style="margin-top:10px; display:flex; gap:30px; color:#666; font-size:13px;">
                    <span>Total: {total_hrs:.1f} hrs</span>
                    <span>Sleep: {avg_sleep:.1f} hrs</span>
                    <span>GPA: {gpa:.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.divider()


# ============================================
# TIPS SECTION
# ============================================
st.subheader("Productivity Tips")

with st.expander("View Study Tips"):
    st.markdown("""
    ### Based on your workload analysis:
    
    **For High-Intensity Days:**
    - Prioritize the most important tasks first
    - Use the Pomodoro technique (25 min work, 5 min break)
    - Minimize distractions during study blocks
    - Stay hydrated and take short walks
    
    **For Moderate Days:**
    - Review and organize notes from recent classes
    - Start on upcoming assignments to stay ahead
    - Schedule study groups or office hours
    
    **For Low-Intensity Days:**
    - Catch up on rest if needed
    - Do light review or reading
    - Plan ahead for busy days coming up
    - Exercise and self-care activities
    
    **General Tips:**
    - Aim for 7-8 hours of sleep
    - Review your calendar every morning
    - Break large tasks into smaller chunks
    - Celebrate completing difficult tasks
    """)

# Refresh button
st.divider()
if st.button("Refresh Workload Data"):
    st.cache_data.clear()
    st.rerun()