import streamlit as st
import requests
import datetime as dt
from modules.nav import SideBarLinks


# Page Setup
st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")
SideBarLinks()

API_URL = "http://localhost:4000/calendar"   # update this if your backend URL differs


# Authentication check
if not st.session_state.get("authenticated", False):
    st.warning("Please log in first.")
    st.stop()

student_id = st.session_state.get("studentID")
if not student_id:
    st.warning("No Student ID found. Please log in again.")
    st.stop()


# Color Mapping for Event Types
COLOR_MAP = {
    "exam": "#FF4B4B",         # red
    "quiz": "#FFD93D",         # yellow
    "homework": "#3F8CFF",     # blue
    "project": "#67D17E",      # green
    "academic": "#8A63D2",     # purple
    "other": "#000000"         # black
}


# Helper: map event/assignment to color
def get_color(item):
    """Decide color based on assignmentType or default academic type."""
    event_type = item.get("assignmentType", "academic").lower()
    return COLOR_MAP.get(event_type, "#8A63D2") 


# Fetch Calendar Data from API
def fetch_calendar():
    try:
        resp = requests.get(f"{API_URL}?studentID={student_id}")
        if resp.status_code == 200:
            return resp.json()
        return []
    except:
        st.error("Failed to reach calendar API.")
        return []


calendar_items = fetch_calendar()


# Determine current week (Mon–Sun)
today = dt.date.today()
monday = today - dt.timedelta(days=today.weekday())
week_days = [monday + dt.timedelta(days=i) for i in range(7)]

day_labels = ["M", "T", "W", "Th", "F", "S", "Su"]


# Transform API data to events grouped by weekday
events_by_day = {d: [] for d in range(7)}  # 0=Mon, 6=Sun

for item in calendar_items:

    # Parse date
    try:
        event_date = dt.datetime.strptime(item["dueDate"], "%Y-%m-%d").date()
    except:
        continue

    # Include only events in this week
    if monday <= event_date <= monday + dt.timedelta(days=6):
        weekday_index = event_date.weekday()
        events_by_day[weekday_index].append(item)


# HEADER + ICONS
colA, colB, colC, colD = st.columns([1, 10, 1, 1])
with colA: st.markdown("👤")
with colB: st.title("Weekly Calendar")
with colC: st.markdown("⚙️")
with colD: st.markdown("🔔")

st.write("---")


# WEEKLY CALENDAR GRID
cols_header = st.columns(7)

# Header row: day labels
for i, lbl in enumerate(day_labels):
    with cols_header[i]:
        st.markdown(
            f"<div style='text-align:center; font-weight:bold; "
            f"font-size:18px;'>{lbl}</div>",
            unsafe_allow_html=True
        )

# Render event blocks
max_rows = max(len(v) for v in events_by_day.values())
max_rows = max(max_rows, 6)  # always render at least 6 rows

for r in range(max_rows):
    row_cols = st.columns(7)

    for i in range(7):
        with row_cols[i]:

            if r < len(events_by_day[i]):
                ev = events_by_day[i][r]
                color = get_color(ev)
                title = ev.get("assignmentTitle", "Event")

                st.markdown(
                    f"""
                    <div style="
                        background-color:{color};
                        height:18px;
                        border-radius:5px;
                        margin:4px;
                        text-align:center;
                        color:white;
                        font-size:10px;
                    ">{title[:8]}</div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown("<div style='height:22px;'></div>", unsafe_allow_html=True)


st.write("---")


# EVENT DETAIL (placeholder)
st.subheader("Event Details")
st.info("Click an event in the grid (feature coming soon).")


# Home Button
st.write("")
center = st.columns([4, 2, 4])[1]
with center:
    st.markdown(
        """
        <div style="
            text-align:center;
            background-color:#6A5ACD;
            color:white;
            width:80px;
            height:80px;
            border-radius:50%;
            display:flex;
            align-items:center;
            justify-content:center;
            font-size:36px;
            margin:auto;
        ">
            🏠
        </div>
        """,
        unsafe_allow_html=True
    )
