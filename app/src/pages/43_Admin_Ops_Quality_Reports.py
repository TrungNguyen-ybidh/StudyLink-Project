import os
import io
import requests
import pandas as pd
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="System Admin | Ops & Reports", page_icon="🧹", layout="wide")
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
        r = requests.request(method, f"{API_BASE}{path}", json=json_body, params=params, timeout=30)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"raw": r.text}
    except Exception as e:
        return 0, {"error": str(e)}

st.markdown("## 🧹 Admin Ops (Imports - Quality - Health- Usage)")
st.caption("Covers User Stories 2.3–2.6 and uses all remaining endpoints")

tab1, tab2, tab3, tab4 = st.tabs(
    ["2.3 Import Metrics", "2.4 Log Error and Rebuild", "2.5 Overlaps", "2.6 Weekly Usage"]
)

with tab1:
    st.subheader("POST /imports/metrics")
    admin_id = st.number_input("adminID", min_value=1, step=1, value=1)
    job_type = st.text_input("jobType", value="Metric Import")

    df = pd.DataFrame([{
        "studentID": 1,
        "courseID": None,
        "category": "Sleep",
        "privacyLevel": "private",
        "description": "nightly sleep hours",
        "unit": "hours",
        "metricType": "numeric",
        "metricName": "sleep_hours",
        "metricValue": "7.5",
    }])

    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if st.button("Run Import", use_container_width=True):
        metrics = []
        for _, row in edited.iterrows():
            m = {k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()}
            if m.get("studentID") is not None:
                m["studentID"] = int(m["studentID"])
            if m.get("courseID") is not None:
                m["courseID"] = int(m["courseID"])
            metrics.append(m)

        body = {"adminID": int(admin_id), "jobType": job_type, "metrics": metrics}
        code, data = call_api("POST", "/imports/metrics", json_body=body)
        st.write(f"Status: {code}")
        st.json(data)
        if isinstance(data, dict) and data.get("jobID") is not None:
            st.session_state["last_job_id"] = int(data["jobID"])

with tab2:
    st.subheader("POST /jobs/{job_id}/errors")
    job_id = st.number_input("job_id", min_value=1, step=1, value=int(st.session_state.get("last_job_id", 1)))
    admin_id2 = st.number_input("adminID (for error log)", min_value=1, step=1, value=1)
    error_type = st.text_input("errorType", value="Incorrect Metric Value")
    error_status = st.text_input("errorStatus", value="open")

    if st.button("Log Error", use_container_width=True):
        body = {"adminID": int(admin_id2), "errorType": error_type, "errorStatus": error_status}
        code, data = call_api("POST", f"/jobs/{int(job_id)}/errors", json_body=body)
        st.write(f"Status: {code}")
        st.json(data)

    st.divider()

    st.subheader("POST /students/{student_id}/plans/rebuild")
    student_id = st.number_input("student_id", min_value=1, step=1, value=1)

    blocks_df = pd.DataFrame([{
        "blockType": "study",
        "isLocked": False,
        "startTime": "2025-01-10 13:00:00",
        "endTime": "2025-01-10 15:00:00",
    }])
    blocks = st.data_editor(blocks_df, num_rows="dynamic", use_container_width=True)
    notes = st.text_input("notes (optional)", value="Rebuild after data fix")
    current_credits = st.number_input("currentCredits (optional)", min_value=0, step=1, value=16)

    if st.button("Rebuild Plan", use_container_width=True):
        body = {
            "notes": notes,
            "currentCredits": int(current_credits),
            "blocks": blocks.to_dict(orient="records"),
        }
        code, data = call_api("POST", f"/students/{int(student_id)}/plans/rebuild", json_body=body)
        st.write(f"Status: {code}")
        st.json(data)

with tab3:
    st.subheader("GET /students/{student_id}/health/overlaps")
    student_id = st.number_input("student_id (overlap check)", min_value=1, step=1, value=1)
    if st.button("Run Overlap Check", use_container_width=True):
        code, data = call_api("GET", f"/students/{int(student_id)}/health/overlaps")
        st.write(f"Status: {code}")
        st.json(data)

with tab4:
    st.subheader("GET /usage/weekly")
    start = st.date_input("start")
    end = st.date_input("end")

    if st.button("Fetch Weekly Usage", use_container_width=True):
        params = {"start": f"{start} 00:00:00", "end": f"{end} 23:59:59"}
        code, data = call_api("GET", "/usage/weekly", params=params)
        st.write(f"Status: {code}")

        if isinstance(data, list):
            st.dataframe(data, use_container_width=True, hide_index=True)
            df = pd.DataFrame(data)

            if "periodStart" in df.columns and "totalStudyHrs" in df.columns:
                try:
                    df["periodStart"] = pd.to_datetime(df["periodStart"], errors="coerce")
                    df = df.dropna(subset=["periodStart"]).sort_values("periodStart").set_index("periodStart")
                    if len(df) > 0:
                        st.line_chart(df[["totalStudyHrs"]])
                except Exception:
                    pass

            buf = io.StringIO()
            df.to_csv(buf, index=False)
            st.download_button(
                "Download CSV",
                data=buf.getvalue(),
                file_name="weekly_usage_summary.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.json(data)
