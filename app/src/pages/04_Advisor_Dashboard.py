import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(
    page_title="Advisor Dashboard",
    page_icon="👨‍🏫",
    layout="wide"
)

SideBarLinks()

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get('role') != 'Advisor':
    st.warning("Access denied. This page is for Advisors only.")
    st.stop()

st.title(f"Welcome Advisor, {st.session_state.get('user_name', 'Advisor')}!")
st.write("")
st.write("What would you like to do today?")

## View All Students
if st.button('View My Students', 
             type='primary',
             use_container_width=True):
       st.switch_page("pages/11_Advisor_Students.py")

## View My Reports
if st.button('View My Reports', 
             type='primary',
             use_container_width=True):
       st.switch_page("pages/12_Advisor_Reports.py")
       
