import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

SideBarLinks()

st.title(f"Welcome Advisor, {st.session_state['first_name']}.")
st.write("")
st.write("### What would you like to do today?")

## View All Students
if st.button('View All Students', 
             type='primary',
             use_container_width=True):
  ## st.switch_page('pages/05_View_All_Students.py')
    st.info("This feature cannot be implemented till Student page is there")

