import os
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="System Admin | Calendar Sync", page_icon="🗓️", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get("role") != "System Admin":
    st.warning("Access denied. This page is for System Administrators only.")
    st.stop()

API_BASE = os.getenv("API_BASE_URL", "http://web-api:4000").rstrip("/")

def call_api(method, path, json_body = None, params=None):
    try:
        r = requests.request(method, f"{API_BASE}{path}", json = json_body, params= params, timeout=20)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"raw": r.text}
    except Exception as e:
        return 0, {"error": str(e)}

st.markdown("## 🗓️ Calendar Connection & Sync")
st.caption("User Story 2.1 — Connect calendars and verify sync status")

student_id = st.number_input("Student ID", min_value =1, step=1, value=1)

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("GET /students/{id}/calendar", use_container_width=True):
        code, data = call_api("GET", f"/students/{int(student_id)}/calendar")
        st.write(f"Status: {code}")
        st.json(data)

with c2:
    external_calendar_id = st.number_input("externalCalendarID", min_value=1, step=1, value=1)
    sync_status = st.selectbox("syncStatus", ["pending", "synced", "failed"], index=0)
    if st.button("PUT /students/{id}/calendar", use_container_width=True):
        body = {"externalCalendarID": int(external_calendar_id), "syncStatus": sync_status}
        code, data = call_api("PUT", f"/students/{int(student_id)}/calendar", json_body=body)
        st.write(f"Status: {code}")
        st.json(data)

with c3:
    if st.button("DELETE /students/{id}/calendar", use_container_width=True):
        code, data = call_api("DELETE", f"/students/{int(student_id)}/calendar")
        st.write(f"Status: {code}")
        st.json(data)
