# modules/nav.py
# Navigation module for StudyLink application

import streamlit as st

def SideBarLinks(show_home=True):
    """
    Creates sidebar navigation links based on user role.
    Call this function at the top of each page to display consistent navigation.
    """
    
    st.sidebar.markdown("## 📚 StudyLink")
    
    # Home link
    if show_home:
        st.sidebar.page_link("Home.py", label="🏠 Home")
    
    st.sidebar.divider()
    
    # Check if user is authenticated
    if not st.session_state.get('authenticated', False):
        st.sidebar.warning("Please log in to access features")
        return
    
    # Display user info
    user_name = st.session_state.get('user_name', 'User')
    role = st.session_state.get('role', 'Unknown')
    
    st.sidebar.markdown(f"**👤 {user_name}**")
    st.sidebar.caption(f"Role: {role}")
    st.sidebar.divider()
    
    # Role-based navigation
    if role == 'Data Analyst':
        st.sidebar.markdown("### 📊 Analytics")
        st.sidebar.page_link("pages/01_Data_Analyst_homepage.py", label="🏠 Analyst Home")
        st.sidebar.page_link("pages/02_Data_Analyst_Dashboard.py", label="📊 Dashboard")
        st.sidebar.page_link("pages/03_Dataset_Management.py", label="📁 Dataset Management")
        st.sidebar.page_link("pages/05_Data_Analyst_tools.py", label="🔧 Data Quality Tools")
    
    elif role == 'Student':
        st.sidebar.markdown("### 🎓 Student Portal")
        st.sidebar.page_link("pages/19_Student_homepage.py", label="🏠 Student Home")
        st.sidebar.page_link("pages/20_Student_calendar.py", label="📅 Calendar")
        st.sidebar.page_link("pages/21_Student_reminder.py", label="⏰ Reminder")
        st.sidebar.page_link("pages/22_Student_grades.py", label="📊 Grades")
        st.sidebar.page_link("pages/23_Student_courses.py", label="📝 Courses")
        st.sidebar.page_link("pages/24_Student_events.py", label="🎭 Events")
        st.sidebar.page_link("pages/25_Student_workload.py", label="📈 Workload")
    
    elif role == 'Advisor':
        st.sidebar.markdown("### 👨‍🏫 Advisor Portal")
        st.sidebar.page_link("pages/04_Advisor_Dashboard.py", label="🏠 Advisor Dashboard")
    
    elif role == 'System Admin':
        st.sidebar.markdown("### ⚙️ Admin Portal")
        st.sidebar.page_link("pages/40_Admin_Home.py", label="🏠 Admin Home")
        st.sidebar.page_link("pages/41_Admin_Term_Course_Catalog.py", label="📊 Course Catalog")
        st.sidebar.page_link("pages/42_Admin_Calendar_Sync.py", label="📁 Calendar Sync")
        st.sidebar.page_link("pages/43_Admin_Ops_Quality_Reports.py", label="📊 Quality Reports")
    
    # Logout button at bottom
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("Home.py")


def HomeNav():
    """
    Simple navigation for home page - just shows login options.
    """
    st.sidebar.markdown("## 📚 StudyLink")
    st.sidebar.markdown("Please select a role to login.")


def AuthenticatedHeader():
    """
    Display authenticated user header with user info.
    """
    if st.session_state.get('authenticated', False):
        col1, col2 = st.columns([4, 1])
        with col2:
            st.markdown(f"**{st.session_state.get('user_name', 'User')}**")
            st.caption(st.session_state.get('role', ''))