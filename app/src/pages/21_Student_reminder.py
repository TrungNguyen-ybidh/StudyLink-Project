import streamlit as st
import requests
from datetime import datetime, date, time
from modules.nav import SideBarLinks

# PAGE CONFIG
st.set_page_config(page_title="Reminders", page_icon="🔔", layout="wide")
SideBarLinks()

# Use Docker service name for container communication
API_BASE = "http://web-api:4000"
API = f"{API_BASE}/student/reminders"

# AUTH CHECK
if not st.session_state.get("authenticated", False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get("role") != "Student":
    st.warning("Access denied. Students only.")
    st.stop()

student_id = st.session_state.get("studentID", 1)
student_name = st.session_state.get("name", "Student")

# HEADER
st.title(f"🔔 Reminders for {student_name}")
st.write("Stay on top of deadlines and upcoming events!")


# ============================================
# API FUNCTIONS
# ============================================
@st.cache_data(ttl=10)
def fetch_reminders(sid):
    """Fetch all active reminders for a student."""
    try:
        response = requests.get(API, params={"studentID": sid}, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"API Error: {e}")
        return []

@st.cache_data(ttl=30)
def fetch_calendar_items(sid):
    """Fetch calendar items to link reminders to."""
    try:
        res = requests.get(f"{API_BASE}/student/calendar", params={"studentID": sid}, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except:
        return []

def create_reminder(payload):
    """Create a new reminder."""
    return requests.post(API, json=payload, timeout=10)

def update_reminder(reminder_id, payload):
    """Update an existing reminder."""
    return requests.put(f"{API}/{reminder_id}", json=payload, timeout=10)

def delete_reminder(reminder_id):
    """Delete a reminder."""
    return requests.delete(f"{API}/{reminder_id}", timeout=10)


# LOAD DATA
reminders = fetch_reminders(student_id)
calendar_items = fetch_calendar_items(student_id)

# Separate assignments and events for linking
assignments = [i for i in calendar_items if i.get("itemType") == "assignment"]
events = [i for i in calendar_items if i.get("itemType") == "event"]

# Debug expander
with st.expander("🔧 Debug Info"):
    st.write(f"Student ID: {student_id}")
    st.write(f"Total reminders: {len(reminders)}")
    st.write(f"Assignments available: {len(assignments)}")
    st.write(f"Events available: {len(events)}")
    if reminders:
        st.json(reminders[:2])

st.divider()


# ============================================
# DISPLAY REMINDERS
# ============================================
st.subheader("📋 Active Reminders")

if not reminders:
    st.info("No upcoming reminders. Add one below!")
else:
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Reminders", len(reminders))
    with col2:
        active_count = len([r for r in reminders if r.get('isActive')])
        st.metric("Active", active_count)
    with col3:
        st.metric("Inactive", len(reminders) - active_count)
    
    st.write("")
    
    # Display each reminder
    for r in reminders:
        reminder_id = r.get('reminderID')
        message = r.get('reminderMessage', 'No message')
        reminder_date = r.get('reminderDate', 'N/A')
        reminder_time = r.get('reminderTime', '')
        is_active = r.get('isActive', True)
        
        # Get linked item info
        linked_to = ""
        linked_date = ""
        if r.get('assignmentTitle'):
            linked_to = f"📝 {r['assignmentTitle']}"
            linked_date = r.get('assignmentDate', '')
        elif r.get('eventName'):
            linked_to = f"📅 {r['eventName']}"
            linked_date = r.get('eventDate', '')
        
        with st.container():
            # Main reminder card
            status_color = "#27ae60" if is_active else "#95a5a6"
            status_icon = "🟢" if is_active else "⚪"
            
            col1, col2 = st.columns([6, 2])
            
            with col1:
                st.markdown(f"""
                <div style="padding:15px; border-radius:10px; background:#f8f9fa; border-left:5px solid {status_color}; margin-bottom:5px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="font-size:16px;">{status_icon} {message}</strong>
                    </div>
                    <div style="margin-top:8px; color:#666;">
                        <span>📆 Reminder: {reminder_date}</span>
                        <span style="margin-left:15px;">⏰ {str(reminder_time)[:5] if reminder_time else 'N/A'}</span>
                    </div>
                    <div style="margin-top:5px; color:#888; font-size:13px;">
                        Linked to: {linked_to or 'Not linked'} {f'(Due: {linked_date})' if linked_date else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.write("")  # Spacing
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("✏️", key=f"edit_{reminder_id}", help="Edit reminder"):
                        st.session_state["edit_reminder_id"] = reminder_id
                        st.session_state["edit_reminder_data"] = r
                        st.rerun()
                with btn_col2:
                    if st.button("🗑️", key=f"delete_{reminder_id}", help="Delete reminder"):
                        res = delete_reminder(reminder_id)
                        if res.status_code == 200:
                            st.success("Reminder deleted!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Failed to delete: {res.text}")
        
        st.write("")  # Spacing between reminders

st.divider()


# ============================================
# EDIT REMINDER (if selected)
# ============================================
if "edit_reminder_id" in st.session_state:
    st.subheader(f"✏️ Edit Reminder #{st.session_state['edit_reminder_id']}")
    
    edit_data = st.session_state.get("edit_reminder_data", {})
    
    with st.form("edit_reminder_form"):
        new_message = st.text_input("Message", value=edit_data.get('reminderMessage', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            # Parse existing date
            try:
                existing_date = datetime.strptime(str(edit_data.get('reminderDate', ''))[:10], "%Y-%m-%d").date()
            except:
                existing_date = date.today()
            new_date = st.date_input("Reminder Date", value=existing_date)
        
        with col2:
            # Parse existing time
            try:
                time_str = str(edit_data.get('reminderTime', '00:00:00'))[:8]
                existing_time = datetime.strptime(time_str, "%H:%M:%S").time()
            except:
                existing_time = time(9, 0)
            new_time = st.time_input("Reminder Time", value=existing_time)
        
        new_active = st.checkbox("Active", value=edit_data.get('isActive', True))
        
        col1, col2 = st.columns(2)
        with col1:
            save_btn = st.form_submit_button("💾 Save Changes", type="primary")
        with col2:
            cancel_btn = st.form_submit_button("❌ Cancel")
        
        if save_btn:
            payload = {
                "message": new_message,
                "date": str(new_date),
                "time": new_time.strftime("%H:%M:%S"),
                "isActive": new_active
            }
            
            res = update_reminder(st.session_state['edit_reminder_id'], payload)
            
            if res.status_code == 200:
                st.success("Reminder updated!")
                del st.session_state["edit_reminder_id"]
                del st.session_state["edit_reminder_data"]
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Update failed: {res.text}")
        
        if cancel_btn:
            del st.session_state["edit_reminder_id"]
            del st.session_state["edit_reminder_data"]
            st.rerun()
    
    st.divider()


# ============================================
# ADD NEW REMINDER
# ============================================
st.subheader("➕ Add New Reminder")

with st.form("add_reminder_form"):
    message = st.text_input("Reminder Message", placeholder="e.g., Study for midterm exam")
    
    col1, col2 = st.columns(2)
    with col1:
        reminder_date = st.date_input("Reminder Date", value=date.today())
    with col2:
        reminder_time = st.time_input("Reminder Time", value=time(9, 0))
    
    st.markdown("#### 🔗 Link to:")
    link_type = st.radio("Link reminder to:", ["Assignment", "Event"], horizontal=True)
    
    assignment_id = None
    event_id = None
    
    if link_type == "Assignment":
        if assignments:
            assignment_options = {
                f"{a.get('assignmentTitle', 'Untitled')} (Due: {a.get('dueDate', 'N/A')})": a.get('assignmentID')
                for a in assignments
            }
            selected = st.selectbox("Select Assignment:", list(assignment_options.keys()))
            assignment_id = assignment_options[selected]
        else:
            st.warning("No assignments found. Create one in the Calendar first, or enter ID manually.")
            assignment_id = st.number_input("Assignment ID:", min_value=1, step=1, key="manual_assign_id")
    else:
        if events:
            event_options = {
                f"{e.get('assignmentTitle', 'Untitled')} (Date: {e.get('dueDate', 'N/A')})": e.get('assignmentID')
                for e in events
            }
            selected = st.selectbox("Select Event:", list(event_options.keys()))
            event_id = event_options[selected]
        else:
            st.warning("No events found. Create one in the Calendar or Events page first, or enter ID manually.")
            event_id = st.number_input("Event ID:", min_value=1, step=1, key="manual_event_id")
    
    submitted = st.form_submit_button("➕ Add Reminder", type="primary")
    
    if submitted:
        # Validation
        if not message:
            st.error("Please enter a reminder message.")
        elif link_type == "Assignment" and not assignment_id:
            st.error("Please select or enter an assignment ID.")
        elif link_type == "Event" and not event_id:
            st.error("Please select or enter an event ID.")
        else:
            payload = {
                "message": message,
                "date": str(reminder_date),
                "time": reminder_time.strftime("%H:%M:%S"),
                "assignmentID": assignment_id if link_type == "Assignment" else None,
                "eventID": event_id if link_type == "Event" else None
            }
            
            response = create_reminder(payload)
            
            if response.status_code == 201:
                st.success("Reminder created successfully!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(f"Error adding reminder: {response.text}")

st.divider()

# Refresh button
if st.button("🔄 Refresh Reminders"):
    st.cache_data.clear()
    st.rerun()