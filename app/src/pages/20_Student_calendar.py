import streamlit as st
import requests
import datetime as dt
from modules.nav import SideBarLinks

# Page Setup
st.set_page_config(page_title="Calendar", page_icon="📅", layout="wide")
SideBarLinks()

# Use Docker service name for API
API_BASE = "http://web-api:4000"
API = f"{API_BASE}/student/calendar"

# Authentication check
if not st.session_state.get("authenticated", False):
    st.warning("Please log in first.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied. Students only.")
    st.stop()

student_id = st.session_state.get("studentID")
student_name = st.session_state.get("studentName", "Student")
st.title(f"Calendar for {student_name}")

# COLORS for different assignment types
COLOR_MAP = {
    "exam": "#FF4B4B",    
    "quiz": "#FFD93D",
    "homework": "#3F8CFF",
    "project": "#67D17E",
    "academic": "#8A63D2",
    "personal": "#FF9F43",
    "club": "#54A0FF",
    "work": "#5F27CD",
    "other": "#636e72"
}

def get_color(item):
    t = (item.get("assignmentType") or "academic").lower()
    return COLOR_MAP.get(t, "#8A63D2")


# ============================================
# API FUNCTIONS
# ============================================
@st.cache_data(ttl=10)
def fetch_calendar(sid):
    try:
        r = requests.get(f"{API}?studentID={sid}", timeout=10)
        if r.status_code == 200:
            return r.json()
        return []
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

def create_calendar_item(payload):
    return requests.post(API, json=payload, timeout=10)

def update_item(item_type, item_id, payload):
    return requests.put(f"{API}/{item_type}/{item_id}", json=payload, timeout=10)

def delete_item(item_type, item_id):
    return requests.delete(f"{API}/{item_type}/{item_id}", timeout=10)


# LOAD DATA
calendar_items = fetch_calendar(student_id)

# ============================================
# WEEKLY GRID VIEW
# ============================================
st.markdown("### Weekly Calendar View")

today = dt.date.today()
monday = today - dt.timedelta(days=today.weekday())
week_dates = [monday + dt.timedelta(days=i) for i in range(7)]
labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Organize items by day of week
events_by_day = {i: [] for i in range(7)}

for item in calendar_items:
    try:
        due_date_str = item.get("dueDate")
        if due_date_str:
            d = dt.datetime.strptime(str(due_date_str)[:10], "%Y-%m-%d").date()
            if monday <= d <= monday + dt.timedelta(days=6):
                day_idx = (d - monday).days
                events_by_day[day_idx].append(item)
    except Exception:
        continue

# CSS for calendar styling
st.markdown("""
<style>
.cal-header { text-align:center; font-weight:bold; font-size:14px; padding:8px; background:#f0f2f6; border-radius:4px; }
.cal-cell { min-height:100px; padding:5px; border:1px solid #e0e0e0; border-radius:4px; background:#fafafa; }
.cal-event { border-radius:4px; padding:3px 6px; color:white; font-size:11px; margin:2px 0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
</style>
""", unsafe_allow_html=True)

# Day headers with dates
cols = st.columns(7)
for i, (label, date) in enumerate(zip(labels, week_dates)):
    with cols[i]:
        is_today = date == today
        bg = "#e3f2fd" if is_today else "#f0f2f6"
        st.markdown(f"<div class='cal-header' style='background:{bg};'>{label}<br>{date.strftime('%m/%d')}</div>", unsafe_allow_html=True)

# Calendar grid
cols = st.columns(7)
for day in range(7):
    with cols[day]:
        st.markdown("<div class='cal-cell'>", unsafe_allow_html=True)
        day_events = events_by_day[day]
        if day_events:
            for ev in day_events[:4]:
                color = get_color(ev)
                title = (ev.get("assignmentTitle") or "Event")[:15]
                st.markdown(f"<div class='cal-event' style='background:{color};' title='{ev.get('assignmentTitle', '')}'>{title}</div>", unsafe_allow_html=True)
            if len(day_events) > 4:
                st.markdown(f"<small>+{len(day_events)-4} more</small>", unsafe_allow_html=True)
        else:
            st.markdown("<span style='color:#ccc; font-size:12px;'>No items</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Legend
st.markdown("**Legend:**")
legend_html = " ".join([f"<span style='background:{color}; color:white; padding:2px 8px; border-radius:4px; font-size:11px; margin-right:5px;'>{name}</span>" for name, color in COLOR_MAP.items()])
st.markdown(legend_html, unsafe_allow_html=True)

st.divider()


# ============================================
# LIST VIEW OF ALL ITEMS
# ============================================
st.markdown("### All Calendar Items")

if not calendar_items:
    st.info("No calendar items found.")
else:
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_type = st.selectbox("Filter by type:", ["All", "assignment", "event"])
    with col2:
        sort_order = st.selectbox("Sort by:", ["Due Date (Ascending)", "Due Date (Descending)"])
    
    filtered = calendar_items
    if filter_type != "All":
        filtered = [i for i in calendar_items if i.get("itemType") == filter_type]
    
    filtered = sorted(filtered, key=lambda x: x.get("dueDate") or "", reverse=("Descending" in sort_order))
    
    st.write(f"Showing {len(filtered)} items")
    
    for item in filtered:
        item_type = item.get("itemType", "assignment")
        item_id = item.get("assignmentID")
        title = item.get("assignmentTitle", "Untitled")
        due_date = item.get("dueDate", "N/A")
        due_time = item.get("dueTime", "")
        status = item.get("status", "")
        course = item.get("courseName", "")
        color = get_color(item)
        
        with st.container():
            col1, col2, col3 = st.columns([5, 2, 1])
            with col1:
                st.markdown(f"""
                <div style="border-left:4px solid {color}; padding-left:10px;">
                    <strong>{icon} {title}</strong><br>
                    <small style="color:#666;">
                        Due: {due_date} {str(due_time)[:5] if due_time else ''} 
                        {f'• Course: {course}' if course else ''}
                        {f'• Status: {status}' if status else ''}
                    </small>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.caption(f"Type: {item.get('assignmentType', 'N/A')}")
            with col3:
                if st.button("Delete", key=f"del_{item_type}_{item_id}"):
                    res = delete_item(item_type, item_id)
                    if res.status_code == 200:
                        st.success("Deleted!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(res.text)
        st.divider()

st.divider()


# ============================================
# ADD NEW ITEM
# ============================================
st.markdown("### Add New Item")

tab1, tab2 = st.tabs(["Add Event", "Add Assignment"])

with tab1:
    with st.form("add_event_form"):
        st.subheader("New Event")
        name = st.text_input("Event Name", key="ev_name")
        event_type = st.selectbox("Event Type", ["academic", "personal", "club", "work"], key="ev_type")
        
        col1, col2 = st.columns(2)
        with col1:
            ev_date = st.date_input("Date", key="ev_date")
            start = st.time_input("Start Time", key="ev_start")
        with col2:
            location = st.text_input("Location (optional)", key="ev_loc")
            end = st.time_input("End Time (optional)", value=None, key="ev_end")

        if st.form_submit_button("Create Event", type="primary"):
            if not name:
                st.error("Event name is required")
            else:
                payload = {
                    "type": "event",
                    "name": name,
                    "eventType": event_type,
                    "date": str(ev_date),
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
                    st.error(f"Error: {res.text}")

with tab2:
    with st.form("add_assignment_form"):
        st.subheader("New Assignment")
        
        # Fetch courses for dropdown
        try:
            courses_res = requests.get(f"{API_BASE}/student/courses", params={"studentID": student_id}, timeout=5)
            courses = courses_res.json() if courses_res.status_code == 200 else []
        except:
            courses = []
        
        if courses:
            course_options = {f"{c['courseCode']} - {c['courseName']}": c['courseID'] for c in courses}
            selected_course = st.selectbox("Course", list(course_options.keys()))
            course_id = course_options[selected_course]
        else:
            course_id = st.number_input("Course ID", min_value=1, key="ass_course")
        
        title = st.text_input("Assignment Title", key="ass_title")
        atype = st.selectbox("Assignment Type", ["homework", "quiz", "exam", "project"], key="ass_type")
        
        col1, col2 = st.columns(2)
        with col1:
            ass_date = st.date_input("Due Date", key="ass_date")
            time_val = st.time_input("Due Time", key="ass_time")
        with col2:
            max_score = st.number_input("Max Score", min_value=1, value=100, key="ass_max")

        if st.form_submit_button("Create Assignment", type="primary"):
            if not title:
                st.error("Assignment title is required")
            else:
                payload = {
                    "type": "assignment",
                    "courseID": course_id,
                    "title": title,
                    "assignmentType": atype,
                    "assignmentDate": str(ass_date),
                    "assignmentTime": time_val.strftime("%H:%M:%S"),
                    "maxScore": max_score
                }
                res = create_calendar_item(payload)
                if res.status_code == 201:
                    st.success("Assignment created!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Error: {res.text}")


# ============================================
# UPDATE SECTION
# ============================================
st.markdown("### ✏️ Update Item")

with st.expander("Update an existing item"):
    update_type = st.radio("Item Type:", ["event", "assignment"], horizontal=True, key="upd_type")
    
    items_to_update = [i for i in calendar_items if i.get("itemType") == update_type]
    
    if items_to_update:
        item_options = {f"{i.get('assignmentTitle', 'Untitled')} (ID: {i.get('assignmentID')})": i.get('assignmentID') for i in items_to_update}
        selected_item = st.selectbox("Select item to update:", list(item_options.keys()))
        update_id = item_options[selected_item]
        
        if update_type == "event":
            new_name = st.text_input("New Name")
            new_date = st.date_input("New Date", key="upd_ev_date")
            new_start = st.time_input("New Start Time", key="upd_ev_start")
            new_loc = st.text_input("New Location")
            
            if st.button("Update Event", type="primary"):
                payload = {}
                if new_name: payload["name"] = new_name
                payload["date"] = str(new_date)
                payload["startTime"] = new_start.strftime("%H:%M:%S")
                if new_loc: payload["location"] = new_loc
                
                res = update_item("event", update_id, payload)
                if res.status_code == 200:
                    st.success("Updated!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(res.text)
        else:
            new_title = st.text_input("New Title")
            new_status = st.selectbox("Status", ["pending", "submitted", "graded", "reviewing"])
            new_score = st.number_input("Score Received", min_value=0, value=0)
            
            if st.button("Update Assignment", type="primary"):
                payload = {"status": new_status}
                if new_title: payload["title"] = new_title
                if new_score > 0: payload["scoreReceived"] = new_score
                
                res = update_item("assignment", update_id, payload)
                if res.status_code == 200:
                    st.success("Updated!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(res.text)
    else:
        st.info(f"No {update_type}s found to update.")

# Refresh button
st.divider()
if st.button("🔄 Refresh Calendar"):
    st.cache_data.clear()
    st.rerun()