import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(
    page_title="System Admin Home",
    page_icon="🛠️",
    layout="wide"
)

SideBarLinks()

# no real login
if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get("role") != "System Admin":
    st.warning("Access denied. This page is for System Administrators only.")
    st.stop()

user_name = st.session_state.get("user_name", "System Administrator")

# styling
st.markdown(
    """
    <style>
      .admin-header{
        background: linear-gradient(135deg,#0f172a 0%,#334155 100%);
        padding:1.5rem;
        border-radius:16px;
        color:white;
        margin-bottom:1.25rem;
      }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="admin-header">
      <h1 style="margin:0;">🛠️ Welcome, {user_name}!</h1>
      <p style="margin:0.5rem 0 0; opacity:0.9;">
        System Administrator — StudyLink Operations
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Quick links to other pages
st.subheader("🚀 Quick Actions")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 🔄 Calendar Sync")
    st.write("Connect and verify student calendar sync status.")
    st.caption("Covers User Story 2.1")
    if st.button("Open Calendar Sync", use_container_width=True):
        st.switch_page("pages/42_Admin_Calendar_Sync.py")

with c2:
    st.markdown("### 🗂️ Term & Course Catalog")
    st.write("Create terms, upload courses, and preview the catalog.")
    st.caption("Covers User Story 2.2")
    if st.button("Open Term/Course Catalog", use_container_width=True):
        st.switch_page("pages/41_Admin_Term_Course_Catalog.py")

with c3:
    st.markdown("### 🧹 Data Quality & Plan Rebuild")
    st.write("Log data issues and rebuild selected student study plans.")
    st.caption("Covers User Story 2.4")
    if st.button("Open Data Quality", use_container_width=True):
        st.switch_page("pages/43_Admin_Ops_Quality_Reports.py")

st.divider()

# user stories
with st.expander("ℹ️ System Administrator User Stories (Phase 2)"):
    st.markdown("""
- **2.1** Connect students’ calendars and verify a sync so class times appear reliably.
- **2.2** Upload and preview the term and course list so the semester is set up correctly.
- **2.3** Import sleep/grade files on a schedule so plans adjust to real-life patterns without exposing private details.
- **2.4** Fix data issues and rebuild selected students’ plans so no one is blocked by bad data and personal changes are kept.
- **2.5** Run a daily schedule health check so overlaps/missing study time are caught early.
- **2.6** Export a weekly usage summary with a simple chart and CSV for adoption/outcome tracking.
    """)
