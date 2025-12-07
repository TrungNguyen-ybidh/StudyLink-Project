import streamlit as st
import requests
from datetime import datetime
from modules.nav import SideBarLinks


# PAGE CONFIG
st.set_page_config(page_title="Reminders", page_icon="🔔", layout="wide")
SideBarLinks()

API = "http://localhost:4000/student/reminders"


# AUTH CHECK
if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied. Students only.")
    st.stop()

student_id = st.session_state.get("studentID")
student_name = st.session_state.get("user_name", "Student")


# HEADER
st.markdown(f"## 🔔 Reminders for **{student_name}**")
st.write("Stay on top of deadlines and upcoming events!")

st.divider()


# FETCH REMINDERS
@st.cache_data(ttl=5)
def fetch_reminders(student_id):
    try:
        url = f"{API}/reminders?studentID={student_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


student_id = st.session_state.get("user_id", 1)


reminders = fetch_reminders(student_id)


# DISPLAY REMINDERS
st.subheader("📋 Active Reminders")

if not reminders:
    st.info("No upcoming reminders.")
else:
    for r in reminders:
        with st.container():
            st.markdown(
                f"""
                <div style="padding:15px; border-radius:10px; background:#f8f9fa; border:1px solid #ddd;">
                    <strong>🔔 {r['reminderMessage']}</strong><br>
                    <span style='color:gray;'>{r['reminderDate']} • {r['reminderTime']}</span><br>
                </div>
                """,
                unsafe_allow_html=True
            )
            col1, col2 = st.columns([0.15, 0.15])
            with col1:
                if st.button("Edit", key=f"edit_{r['reminderID']}"):
                    st.session_state["edit_id"] = r["reminderID"]
                    st.rerun()
            with col2:
                if st.button("Delete", key=f"delete_{r['reminderID']}"):
                    requests.delete(f"{API}/reminders/{r['reminderID']}")
                    st.success("Reminder deleted!")
                    st.cache_data.clear()
                    st.rerun()

st.divider()


# ADD REMINDER
st.subheader("➕ Add New Reminder")

with st.form("add_reminder_form"):
    message = st.text_input("Reminder Message")
    date = st.date_input("Reminder Date")
    time = st.time_input("Reminder Time")

    st.markdown("#### Link to:")
    option = st.radio("Reminder For:", ["Assignment", "Event"], horizontal=True)

    assignment_id = None
    event_id = None

    if option == "Assignment":
        assignment_id = st.number_input("Assignment ID", min_value=1, step=1)
    else:
        event_id = st.number_input("Event ID", min_value=1, step=1)

    submitted = st.form_submit_button("Add Reminder", type="primary")

    if submitted:
        payload = {
            "message": message,
            "date": date.strftime("%Y-%m-%d"),
            "time": time.strftime("%H:%M:%S"),
            "assignmentID": assignment_id,
            "eventID": event_id
        }

        response = requests.post(f"{API}/reminders", json=payload)

        if response.status_code == 201:
            st.success("Reminder created successfully!")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("Error adding reminder.")


st.divider()


# UPDATE REMINDER
if "edit_id" in st.session_state:
    reminder_id = st.session_state["edit_id"]
    st.subheader(f"✏️ Edit Reminder #{reminder_id}")

    with st.form("edit_reminder_form"):
        new_message = st.text_input("New Message")
        new_date = st.date_input("New Date")
        new_time = st.time_input("New Time")
        active = st.checkbox("Active?", value=True)

        submitted_edit = st.form_submit_button("Save Changes", type="primary")

        if submitted_edit:
            payload = {
                "message": new_message,
                "date": new_date.strftime("%Y-%m-%d"),
                "time": new_time.strftime("%H:%M:%S"),
                "isActive": active
            }

            response = requests.put(
                f"{API}/reminders/{reminder_id}",
                json=payload
            )

            if response.status_code == 200:
                st.success("Reminder updated!")
                del st.session_state["edit_id"]
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Error updating reminder.")
