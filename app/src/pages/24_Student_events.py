import streamlit as st
import requests
from datetime import datetime, date, time
from modules.nav import SideBarLinks

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Events",
    page_icon="📅",
    layout="wide"
)

SideBarLinks()

API = "http://localhost:4000/student/events"


# AUTH CHECK
if not st.session_state.get("authenticated", False):
    st.warning("Please log in first.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied. Students only.")
    st.stop()

student_id = st.session_state.get("studentID")
student_name = st.session_state.get("user_name", "Student")


# HELPERS TO PARSE DATE/TIME FROM API
def parse_date(d):
    """API returns 'YYYY-MM-DD' as string → convert to date object"""
    if isinstance(d, date):
        return d
    try:
        return datetime.strptime(d, "%Y-%m-%d").date()
    except Exception:
        return date.today()


def parse_time(t):
    """API returns 'HH:MM:SS' or 'HH:MM' as string → convert to time object"""
    if t is None:
        return time(0, 0)
    if isinstance(t, time):
        return t
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(t, fmt).time()
        except Exception:
            continue
    return time(0, 0)


# FETCH EVENTS (GET)
@st.cache_data(ttl=5)
def get_events(student_id):
    try:
        res = requests.get(API, params={"studentID": student_id})
        return res.json() if res.status_code == 200 else []
    except:
        return []


events = get_events(student_id)


# PAGE HEADER
st.markdown("""
    <h1 style="margin-bottom:0;">📅 Event Manager</h1>
    <p style="margin-top:0; color:#666;">
        View, add, update, and delete your personal, club, work, or academic events.
    </p>
""", unsafe_allow_html=True)

st.markdown("---")


# ADD NEW EVENT (POST)
st.subheader("➕ Add New Event")

with st.form("add_event_form"):
    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Event Name")
        event_type = st.selectbox("Type", ["personal", "club", "work", "academic"])

    with col2:
        date_val = st.date_input("Event Date")
        start_time = st.time_input("Start Time")
        end_time = st.time_input("End Time")

    location = st.text_input("Location (optional)")

    submitted = st.form_submit_button("Create Event")

    if submitted:
        payload = {
            "studentID": student_id,
            "name": name,
            "type": event_type,
            "date": str(date_val),
            "startTime": str(start_time),
            "endTime": str(end_time),
            "location": location
        }

        res = requests.post(API, json=payload)

        if res.status_code == 201:
            st.success("Event created!")
            st.cache_data.clear()
        else:
            st.error(f"Failed to add event: {res.text}")

st.markdown("---")


# DISPLAY + UPDATE (PUT) + DELETE (DELETE)
st.subheader("📋 Your Events")

if not events:
    st.info("No events found.")
else:
    for event in events:
        event_id = event["eventID"]
        event_name = event["eventName"]
        event_type = event["eventType"]
        event_date = parse_date(event["date"])
        event_start = parse_time(event["startTime"])
        event_end = parse_time(event.get("endTime"))
        event_location = event.get("location", "")

        with st.container(border=True):
            colA, colB, colC = st.columns([5, 3, 2])

            # DETAILS
            with colA:
                st.markdown(f"""
                    <h4 style="margin-bottom:0;">{event_name} ({event_type})</h4>
                    <p style="margin:0; color:#666;">
                        {event_date} • {event_start.strftime('%H:%M')}–{event_end.strftime('%H:%M') if event_end else 'N/A'}
                    </p>
                    <p style="margin:0; color:#888;">
                        Location: {event_location or 'N/A'}
                    </p>
                """, unsafe_allow_html=True)

            # UPDATE (PUT)
            with colB:
                with st.expander("✏️ Edit Event"):
                    new_name = st.text_input(
                        "Event Name",
                        value=event_name,
                        key=f"name_{event_id}"
                    )
                    new_type = st.selectbox(
                        "Type",
                        ["personal", "club", "work", "academic"],
                        index=["personal", "club", "work", "academic"].index(event_type)
                        if event_type in ["personal", "club", "work", "academic"] else 0,
                        key=f"type_{event_id}"
                    )
                    new_date = st.date_input(
                        "Date",
                        value=event_date,
                        key=f"date_{event_id}"
                    )
                    new_start = st.time_input(
                        "Start Time",
                        value=event_start,
                        key=f"start_{event_id}"
                    )
                    new_end = st.time_input(
                        "End Time",
                        value=event_end,
                        key=f"end_{event_id}"
                    )
                    new_location = st.text_input(
                        "Location",
                        value=event_location,
                        key=f"location_{event_id}"
                    )

                    if st.button("Save Changes", key=f"update_{event_id}", type="primary"):
                        payload = {
                            "name": new_name,
                            "type": new_type,
                            "date": str(new_date),
                            "startTime": str(new_start),
                            "endTime": str(new_end),
                            "location": new_location
                        }

                        res = requests.put(f"{API}/{event_id}", json=payload)

                        if res.status_code == 200:
                            st.success("Event updated successfully!")
                            st.cache_data.clear()
                        else:
                            st.error(f"Update failed: {res.text}")

            # DELETE
            with colC:
                if st.button("🗑️ Delete", key=f"delete_{event_id}"):
                    res = requests.delete(f"{API}/{event_id}")

                    if res.status_code == 200:
                        st.success("Event deleted!")
                        st.cache_data.clear()
                    else:
                        st.error(f"Delete failed: {res.text}")