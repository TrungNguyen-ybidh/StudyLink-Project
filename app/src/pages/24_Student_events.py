import streamlit as st
import requests
from datetime import datetime, date, time
from modules.nav import SideBarLinks

# PAGE CONFIG
st.set_page_config(page_title="Events", page_icon="🎭", layout="wide")
SideBarLinks()

# Use Docker service name for container communication
API_BASE = "http://web-api:4000"
API = f"{API_BASE}/student/events"

# AUTH CHECK
if not st.session_state.get("authenticated", False):
    st.warning("Please log in first.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied. Students only.")
    st.stop()

student_id = st.session_state.get("studentID", 1)
student_name = st.session_state.get("name", "Student")


# ============================================
# HELPER FUNCTIONS
# ============================================
def parse_date(d):
    """Convert API date string to date object."""
    if d is None:
        return date.today()
    if isinstance(d, date):
        return d
    try:
        return datetime.strptime(str(d)[:10], "%Y-%m-%d").date()
    except:
        return date.today()

def parse_time(t):
    """Convert API time string to time object."""
    if t is None:
        return time(0, 0)
    if isinstance(t, time):
        return t
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(str(t)[:8], fmt).time()
        except:
            continue
    return time(0, 0)


# ============================================
# API FUNCTIONS
# ============================================
@st.cache_data(ttl=10)
def fetch_events(sid, event_type=None):
    """Fetch all events for a student."""
    try:
        params = {"studentID": sid}
        if event_type:
            params["type"] = event_type
        res = requests.get(API, params=params, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

def create_event(payload):
    """Create a new event."""
    return requests.post(API, json=payload, timeout=10)

def update_event(event_id, payload):
    """Update an existing event."""
    return requests.put(f"{API}/{event_id}", json=payload, timeout=10)

def delete_event(event_id):
    """Delete an event."""
    return requests.delete(f"{API}/{event_id}", timeout=10)


# LOAD DATA
events = fetch_events(student_id)

# Event type colors and icons
EVENT_STYLES = {
    "personal": {"color": "#FF9F43", "icon": "👤"},
    "club": {"color": "#54A0FF", "icon": "🎯"},
    "work": {"color": "#5F27CD", "icon": "💼"},
    "academic": {"color": "#10AC84", "icon": "📚"},
    "workshop": {"color": "#EE5A24", "icon": "🔧"},
    "study": {"color": "#3498db", "icon": "📖"},
    "meeting": {"color": "#9b59b6", "icon": "🤝"}
}

def get_event_style(event_type):
    return EVENT_STYLES.get(event_type, {"color": "#95a5a6", "icon": "📅"})


# PAGE HEADER
st.title(f"🎭 Events for {student_name}")
st.write("Manage your personal, club, work, and academic events.")

# Debug expander
with st.expander("🔧 Debug Info"):
    st.write(f"Student ID: {student_id}")
    st.write(f"Total events: {len(events)}")
    if events:
        st.json(events[:2])

st.divider()


# ============================================
# EVENT STATS
# ============================================
if events:
    col1, col2, col3, col4 = st.columns(4)
    
    # Count by type
    type_counts = {}
    for e in events:
        t = e.get('eventType', 'other')
        type_counts[t] = type_counts.get(t, 0) + 1
    
    with col1:
        st.metric("Total Events", len(events))
    with col2:
        st.metric("Personal", type_counts.get('personal', 0))
    with col3:
        st.metric("Academic", type_counts.get('academic', 0) + type_counts.get('study', 0))
    with col4:
        st.metric("Work/Club", type_counts.get('work', 0) + type_counts.get('club', 0))

st.divider()


# ============================================
# DISPLAY EVENTS
# ============================================
st.subheader("📋 Your Events")

# Filter options
col1, col2 = st.columns(2)
with col1:
    filter_type = st.selectbox(
        "Filter by Type:",
        ["All Types", "personal", "club", "work", "academic", "workshop", "study", "meeting"]
    )
with col2:
    sort_option = st.selectbox(
        "Sort by:",
        ["Date (Upcoming First)", "Date (Latest First)", "Type"]
    )

# Apply filters
filtered_events = events.copy()
if filter_type != "All Types":
    filtered_events = [e for e in events if e.get('eventType') == filter_type]

# Sort events
if "Upcoming First" in sort_option:
    filtered_events = sorted(filtered_events, key=lambda x: x.get('date', ''))
elif "Latest First" in sort_option:
    filtered_events = sorted(filtered_events, key=lambda x: x.get('date', ''), reverse=True)
else:
    filtered_events = sorted(filtered_events, key=lambda x: x.get('eventType', ''))

st.write(f"Showing {len(filtered_events)} events")

if not filtered_events:
    st.info("No events found. Create one below!")
else:
    for event in filtered_events:
        event_id = event.get('eventID')
        event_name = event.get('eventName', 'Untitled Event')
        event_type = event.get('eventType', 'other')
        event_date = event.get('date', 'N/A')
        event_start = event.get('startTime', '')
        event_end = event.get('endTime', '')
        event_location = event.get('location', '')
        
        style = get_event_style(event_type)
        
        with st.container():
            col1, col2, col3 = st.columns([5, 2, 1])
            
            with col1:
                st.markdown(f"""
                <div style="padding:15px; border-radius:10px; background:#ffffff; 
                            border:1px solid #e0e0e0; border-left:5px solid {style['color']}; margin-bottom:5px;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span style="font-size:24px;">{style['icon']}</span>
                        <div>
                            <h4 style="margin:0; color:#333;">{event_name}</h4>
                            <p style="margin:5px 0 0 0; color:#666; font-size:13px;">
                                📆 {event_date} • ⏰ {str(event_start)[:5] if event_start else 'TBA'}
                                {f" - {str(event_end)[:5]}" if event_end else ""}
                                {f" • 📍 {event_location}" if event_location else ""}
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style="text-align:center; padding-top:15px;">
                    <span style="background:{style['color']}; color:white; padding:4px 12px; 
                                border-radius:15px; font-size:12px; text-transform:uppercase;">
                        {event_type}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.write("")  # Spacing
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("✏️", key=f"edit_{event_id}", help="Edit event"):
                        st.session_state["edit_event_id"] = event_id
                        st.session_state["edit_event_data"] = event
                        st.rerun()
                with btn_col2:
                    if st.button("🗑️", key=f"delete_{event_id}", help="Delete event"):
                        res = delete_event(event_id)
                        if res.status_code == 200:
                            st.success("Event deleted!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {res.text}")
        
        st.write("")  # Spacing

st.divider()


# ============================================
# EDIT EVENT (if selected)
# ============================================
if "edit_event_id" in st.session_state:
    st.subheader(f"✏️ Edit Event #{st.session_state['edit_event_id']}")
    
    edit_data = st.session_state.get("edit_event_data", {})
    
    with st.form("edit_event_form"):
        new_name = st.text_input("Event Name", value=edit_data.get('eventName', ''))
        
        new_type = st.selectbox(
            "Event Type",
            ["personal", "club", "work", "academic", "workshop", "study", "meeting"],
            index=["personal", "club", "work", "academic", "workshop", "study", "meeting"].index(
                edit_data.get('eventType', 'personal')
            ) if edit_data.get('eventType') in ["personal", "club", "work", "academic", "workshop", "study", "meeting"] else 0
        )
        
        col1, col2 = st.columns(2)
        with col1:
            new_date = st.date_input("Date", value=parse_date(edit_data.get('date')))
            new_start = st.time_input("Start Time", value=parse_time(edit_data.get('startTime')))
        with col2:
            new_location = st.text_input("Location", value=edit_data.get('location', ''))
            new_end = st.time_input("End Time", value=parse_time(edit_data.get('endTime')))
        
        col1, col2 = st.columns(2)
        with col1:
            save_btn = st.form_submit_button("💾 Save Changes", type="primary")
        with col2:
            cancel_btn = st.form_submit_button("❌ Cancel")
        
        if save_btn:
            payload = {
                "name": new_name,
                "type": new_type,
                "date": str(new_date),
                "startTime": new_start.strftime("%H:%M:%S"),
                "endTime": new_end.strftime("%H:%M:%S") if new_end else None,
                "location": new_location
            }
            
            res = update_event(st.session_state['edit_event_id'], payload)
            
            if res.status_code == 200:
                st.success("Event updated!")
                del st.session_state["edit_event_id"]
                del st.session_state["edit_event_data"]
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Update failed: {res.text}")
        
        if cancel_btn:
            del st.session_state["edit_event_id"]
            del st.session_state["edit_event_data"]
            st.rerun()
    
    st.divider()


# ============================================
# ADD NEW EVENT
# ============================================
st.subheader("➕ Add New Event")

with st.form("add_event_form"):
    name = st.text_input("Event Name", placeholder="e.g., Team Meeting, Study Group, Gym")
    
    event_type = st.selectbox(
        "Event Type",
        ["personal", "club", "work", "academic", "workshop", "study", "meeting"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        event_date = st.date_input("Event Date", value=date.today())
        start_time = st.time_input("Start Time", value=time(9, 0))
    with col2:
        location = st.text_input("Location (optional)", placeholder="e.g., Room 101, Online")
        end_time = st.time_input("End Time (optional)", value=time(10, 0))
    
    submitted = st.form_submit_button("➕ Create Event", type="primary")
    
    if submitted:
        if not name:
            st.error("Please enter an event name.")
        else:
            payload = {
                "studentID": student_id,
                "name": name,
                "type": event_type,
                "date": str(event_date),
                "startTime": start_time.strftime("%H:%M:%S"),
                "endTime": end_time.strftime("%H:%M:%S") if end_time else None,
                "location": location
            }
            
            res = create_event(payload)
            
            if res.status_code == 201:
                st.success("Event created successfully!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Error creating event: {res.text}")

# Refresh button
st.divider()
if st.button("🔄 Refresh Events"):
    st.cache_data.clear()
    st.rerun()