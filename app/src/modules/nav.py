# modules/nav.py
# Navigation module for StudyLink application

import streamlit as st

def SideBarLinks(show_home=True):
    """
    Creates sidebar navigation links based on user role.
    Call this function at the top of each page to display consistent navigation.
    """
    
    # Add logo (create assets folder and add your logo)
    # st.sidebar.image("assets/logo.png", width=200)
    
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
        st.sidebar.page_link("pages/01_Data_Analyst_homepage.py", label="🏠 Data Analyst Home")
        st.sidebar.page_link("pages/02_Data_Analyst_Dashboard.py", label="📊 Dashboard & Analytics")
    
    elif role == 'Student':
        st.sidebar.markdown("### 🎓 Student Portal")
        st.sidebar.page_link("pages/10_Student_Home.py", label="🏠 Student Home")
        st.sidebar.page_link("pages/11_Calendar.py", label="📅 Calendar")
        st.sidebar.page_link("pages/12_Grades.py", label="📝 Grades")
        st.sidebar.page_link("pages/13_Study_Plan.py", label="📚 Study Plan")
    
    elif role == 'Advisor':
        st.sidebar.markdown("### 👨‍🏫 Advisor Portal")
        st.sidebar.page_link("pages/04_Advisor_Dashboard.py", label="🏠 Advisor Dashboard")
    
    elif role == 'Admin':
        st.sidebar.markdown("### ⚙️ Admin Portal")
        st.sidebar.page_link("pages/40_Admin_Home.py", label="🏠 Admin Home")
        st.sidebar.page_link("pages/41_System_Status.py", label="📊 System Status")
        st.sidebar.page_link("pages/42_Data_Management.py", label="📁 Data Management")
        st.sidebar.page_link("pages/43_User_Management.py", label="👥 User Management")
    
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