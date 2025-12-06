import os
import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="System Admin | Terms & Courses", page_icon="📚", layout="wide")
SideBarLinks()

if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get("role") != "System Admin":
    st.warning("Access denied. This page is for System Administrators only.")
    st.stop()

API_BASE = os.getenv("API_BASE_URL", "http://web-api:4000").rstrip("/")

def call_api(method, path, json_body=None, params=None):
    try:
        r = requests.request(method, f"{API_BASE}{path}", json=json_body, params=params, timeout=20)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"raw": r.text}
    except Exception as e:
        return 0, {"error": str(e)}

st.markdown("## 📚 Term & Course Catalog")
st.caption("User Story 2.2 — Upload/preview term and course list, remove incorrect entries")

# ---- TERMS: GET/POST /terms ----
st.subheader("Terms")

tA, tB = st.columns(2)

with tA:
    if st.button("View Terms", use_container_width=True):
        code, data = call_api("GET", "/terms")
        st.write(f"Status: {code}")
        st.session_state["terms_cache"] = data if isinstance(data, list) else []
        st.json(data)

with tB:
    with st.form("create_term"):
        name = st.text_input("name", value="Spring 2026")
        start_date = st.date_input("startDate")
        end_date = st.date_input("endDate")
        submit = st.form_submit_button("Create New Term", use_container_width=True)

    if submit:
        body = {"name": name, "startDate": str(start_date), "endDate": str(end_date)}
        code, data = call_api("POST", "/terms", json_body=body)
        st.write(f"Status: {code}")
        st.json(data)

st.divider()

# ---- COURSES: GET/POST /terms/{term_id}/courses + DELETE /terms/{term_id}/courses/{course_id} ----
st.subheader("Courses (by Term)")

terms = st.session_state.get("terms_cache", [])
term_ids = []
if isinstance(terms, list):
    for t in terms:
        if isinstance(t, dict) and t.get("termID") is not None:
            term_ids.append(int(t["termID"]))
        elif isinstance(t, (list, tuple)) and len(t) > 0:
            term_ids.append(int(t[0]))

term_id = st.selectbox("termID (load terms first if you want a dropdown)", term_ids) if term_ids else st.number_input("termID", min_value=1, step=1, value=1)

c1, c2 = st.columns(2)

with c1:
    if st.button("View Courses for Term", use_container_width=True):
        code, data = call_api("GET", f"/terms/{int(term_id)}/courses")
        st.write(f"Status: {code}")
        st.session_state["courses_cache"] = data if isinstance(data, list) else []
        st.json(data)

with c2:
    with st.form("add_course"):
        courseCode = st.text_input("courseCode", value="CS3200")
        courseName = st.text_input("courseName", value="Database Design")
        credits = st.number_input("credits", min_value=0, step=1, value=4)
        department = st.text_input("department", value="CS")
        location = st.text_input("location (optional)", value="")
        instructor = st.text_input("instructor (optional)", value="")
        date_val = st.text_input("date (YYYY-MM-DD, optional)", value="")
        startTime = st.text_input("startTime (HH:MM:SS, optional)", value="")
        endTime = st.text_input("endTime (HH:MM:SS, optional)", value="")
        submit_course = st.form_submit_button("Create New Course", use_container_width=True)

    if submit_course:
        body = {
            "courseCode": courseCode,
            "courseName": courseName,
            "credits": int(credits),
            "department": department,
            "location": location or None,
            "instructor": instructor or None,
            "date": date_val or None,
            "startTime": startTime or None,
            "endTime": endTime or None,
        }
        code, data = call_api("POST", f"/terms/{int(term_id)}/courses", json_body=body)
        st.write(f"Status: {code}")
        st.json(data)

st.divider()

course_id = st.number_input("course_id to delete", min_value=1, step=1, value=1)
if st.button("Delete Course From Term", use_container_width=True):
    code, data = call_api("DELETE", f"/terms/{int(term_id)}/courses/{int(course_id)}")
    st.write(f"Status: {code}")
    st.json(data)
