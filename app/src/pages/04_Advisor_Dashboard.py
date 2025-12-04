import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

SideBarLinks()

st.title(f"Welcome Advisor, {st.session_state['first_name']}.")
st.write("")
st.write("### What would you like to do today?")

