import streamlit as st
import requests
import datetime as dt
from modules.nav import SideBarLinks


# Page Setup
st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")
SideBarLinks()

API = "http://localhost:8501/calendar"


# Authentication check
if not st.session_state.get("authenticated", False):
    st.warning("Please log in first.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied. Students only.")
    st.stop()

student_id = st.session_state.get("studentID")
student_name = st.session_state.get("user_name", "Student")


# COLORS
COLOR_MAP = {
    "exam": "#FF4B4B",    
    "quiz": "#FFD93D",
    "homework": "#3F8CFF",
    "project": "#67D17E",
    "academic": "#8A63D2",
    "other": "#000000"
}

def get_color(item):
    t = item.get("assignmentType", "academic").lower()
    return COLOR_MAP.get(t, "#8A63D2")


# API CALLS

@st.cache_data(ttl=5)
def fetch_calendar(student_id):
    try:
        r = requests.get(f"{API}?studentID={student_id}")
        return r.json() if r.status_code == 200 else []
    except:
        return []


def create_calendar_item(payload):
    return requests.post(API, json=payload)


def update_item(item_type, item_id, payload):
    return requests.put(f"{API}/{item_type}/{item_id}", json=payload)


def delete_item(item_type, item_id):
    return requests.delete(f"{API}/{item_type}/{item_id}")


# LOAD DATA
calendar_items = fetch_calendar(student_id)


# ======================================================
# WEEKLY GRID (Guaranteed to render)
# ======================================================

today = dt.date.today()
monday = today - dt.timedelta(days=today.weekday())
labels = ["M", "T", "W", "Th", "F", "S", "Su"]

events_by_day = {i: [] for i in range(7)}  # Always initialize

# Add items if data exists
if calendar_items:
    for item in calendar_items:
        try:
            d = dt.datetime.strptime(item["dueDate"], "%Y-%m-%d").date()
        except:
            continue

        if monday <= d <= monday + dt.timedelta(days=6):
            events_by_day[d.weekday()].append(item)


# SECTION HEADER
st.markdown("### 📅 Weekly Calendar View")

# ========== CSS to force visible grid ==========
st.markdown("""
<style>
.grid-cell {
    border: 1px solid #ddd;
    border-radius: 6px;
    height: 55px;
    padding: 4px;
    background: #fafafa;
}
.event-box {
    border-radius: 4px;
    padding: 2px 4px;
    color: white;
    font-size: 11px;
    text-align: center;
    margin-top: 2px;
}
.day-label {
    text-align:center; 
    font-weight:bold; 
    font-size:18px;
    margin-bottom:6px;
}
</style>
""", unsafe_allow_html=True)

# Day Headers
cols_hdr = st.columns(7)
for i, lbl in enumerate(labels):
    cols_hdr[i].markdown(f"<div class='day-label'>{lbl}</div>", unsafe_allow_html=True)

# ========== Render 6 rows always ==========
NUM_ROWS = 6

for r in range(NUM_ROWS):
    cols = st.columns(7)
    for day in range(7):
        with cols[day]:

            st.markdown("<div class='grid-cell'>", unsafe_allow_html=True)

            # Event in this box?
            if r < len(events_by_day[day]):
                ev = events_by_day[day][r]
                color = get_color(ev)
                title = ev.get("assignmentTitle", "Event")

                st.markdown(
                    f"<div class='event-box' style='background:{color};'>{title[:10]}</div>",
                    unsafe_allow_html=True
                )

            else:
                # empty cell stays visible due to CSS box
                st.markdown("&nbsp;", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)



# SECTION: ADD NEW ITEM
st.subheader("➕ Add Event or Assignment")

with st.form("add_item_form"):
    item_type = st.radio("Item Type:", ["Event", "Assignment"], horizontal=True)

    if item_type == "Event":
        name = st.text_input("Event Name")
        event_type = st.selectbox("Event Type", ["academic", "other"])
        date = st.date_input("Date")
        start = st.time_input("Start Time")
        end = st.time_input("End Time (optional)", value=None)
        location = st.text_input("Location (optional)")

        submitted = st.form_submit_button("Create Event")

        if submitted:
            payload = {
                "type": "event",
                "name": name,
                "eventType": event_type,
                "date": str(date),
                "startTime": start.strftime("%H:%M:%S"),
                "endTime": end.strftime("%H:%M:%S") if end else None,
                "location": location,
                "studentID": student_id
            }
            res = create_calendar_item(payload)
            if res.status_code == 201:
                st.success("Event created!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(res.text)

    else:
        course_id = st.number_input("Course ID", min_value=1)
        title = st.text_input("Assignment Title")
        atype = st.selectbox("Assignment Type", ["homework", "quiz", "exam", "project"])
        date = st.date_input("Due Date")
        time = st.time_input("Due Time")
        max_score = st.number_input("Max Score", min_value=1)

        submitted = st.form_submit_button("Create Assignment")

        if submitted:
            payload = {
                "type": "assignment",
                "courseID": course_id,
                "title": title,
                "assignmentType": atype,
                "assignmentDate": str(date),
                "assignmentTime": time.strftime("%H:%M:%S"),
                "maxScore": max_score
            }
            res = create_calendar_item(payload)
            if res.status_code == 201:
                st.success("Assignment created!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(res.text)


st.write("---")


# SECTION: UPDATE ITEMS
st.subheader("✏️ Update a Calendar Item")

with st.expander("Update Item Details"):
    update_type = st.radio("Update:", ["Event", "Assignment"], horizontal=True)
    update_id = st.number_input("Item ID to update", step=1)

    if update_type == "Event":
        name = st.text_input("New Name (optional)")
        etype = st.text_input("New Event Type (optional)")
        date = st.date_input("New Date", value=None)
        stime = st.time_input("New Start Time", value=None)
        etime = st.time_input("New End Time", value=None)
        loc = st.text_input("New Location")

        if st.button("Update Event"):
            payload = {}
            if name: payload["name"] = name
            if etype: payload["type"] = etype
            if date: payload["date"] = str(date)
            if stime: payload["startTime"] = stime.strftime("%H:%M:%S")
            if etime: payload["endTime"] = etime.strftime("%H:%M:%S")
            if loc: payload["location"] = loc

            res = update_item("event", update_id, payload)
            if res.status_code == 200:
                st.success("Event updated!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(res.text)

    else:
        title = st.text_input("New Assignment Title")
        atype = st.text_input("New Assignment Type")
        date = st.date_input("New Due Date", value=None)
        time = st.time_input("New Due Time", value=None)
        max_s = st.number_input("New Max Score", value=0)
        score = st.number_input("Score Received", value=0)
        status = st.selectbox("Status", ["pending", "completed"])

        if st.button("Update Assignment"):
            payload = {}
            if title: payload["title"] = title
            if atype: payload["assignmentType"] = atype
            if date: payload["assignmentDate"] = str(date)
            if time: payload["assignmentTime"] = time.strftime("%H:%M:%S")
            if max_s > 0: payload["maxScore"] = max_s
            payload["scoreReceived"] = score
            payload["status"] = status

            res = update_item("assignment", update_id, payload)
            if res.status_code == 200:
                st.success("Assignment updated!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(res.text)


# SECTION: DELETE ITEMS
st.subheader("🗑️ Delete a Calendar Item")

with st.expander("Delete an Item"):
    delete_type = st.radio("Delete:", ["Event", "Assignment"], horizontal=True)
    item_id = st.number_input("Item ID", step=1)

    if st.button("Delete Now"):
        t = "event" if delete_type == "Event" else "assignment"
        res = delete_item(t, item_id)
        if res.status_code == 200:
            st.success("Item deleted!")
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(res.text)


st.write("---")