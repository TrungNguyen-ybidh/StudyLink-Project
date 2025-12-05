import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Data Quality Tools",
    page_icon="🔧",
    layout="wide"
)

SideBarLinks()

# Authentication check
if not st.session_state.get('authenticated', False):
    st.warning("Please log in from the Home page.")
    st.stop()

if st.session_state.get('role') != 'Data Analyst':
    st.warning("Access denied. This page is for Data Analysts only.")
    st.stop()

# API base URL
API_BASE = "http://web-api:4000"

st.title("🔧 Data Quality Tools")
st.caption("User Story 1.4 - Fix, correct, and maintain data integrity")

# Tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs(["📊 Metrics Editor", "⚠️ Error Tracking", "👥 Student Corrections", "📋 Audit Log"])

# ============================================
# TAB 1: Metrics Editor (User Story 1.4)
# ============================================
with tab1:
    st.subheader("📊 Metrics Editor")
    st.markdown("Search, view, and correct metric entries to ensure data accuracy.")
    
    # Search filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Fetch students for filter
        try:
            response = requests.get(f"{API_BASE}/students")
            students = response.json() if response.status_code == 200 else []
        except:
            students = []
        
        student_options = {"All Students": None}
        if students:
            for s in students:
                student_options[f"{s.get('fName', '')} {s.get('lName', '')}"] = s.get('studentID')
        else:
            student_options.update({"John Doe": 1, "Jane Lee": 2, "Mark Chan": 3})
        
        selected_student = st.selectbox("Student", options=list(student_options.keys()))
    
    with col2:
        metric_category = st.selectbox(
            "Category",
            ["All", "Study", "Sleep", "Stress", "Attendance"]
        )
    
    with col3:
        metric_type = st.selectbox(
            "Metric Type",
            ["All", "study_hr", "sleep", "stress", "attendance"]
        )
    
    with col4:
        if st.button("🔍 Search Metrics", use_container_width=True):
            st.session_state['search_metrics'] = True
    
    # Fetch metrics based on filters
    try:
        params = {}
        if student_options[selected_student]:
            params['studentID'] = student_options[selected_student]
        if metric_category != "All":
            params['category'] = metric_category
        if metric_type != "All":
            params['metricType'] = metric_type
        
        response = requests.get(f"{API_BASE}/data/metrics", params=params)
        if response.status_code == 200:
            metrics = response.json()
        else:
            metrics = []
    except Exception as e:
        st.error(f"Error fetching metrics: {e}")
        metrics = []
    
    # Display metrics table
    if metrics:
        df = pd.DataFrame(metrics)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Edit metric section
        st.markdown("---")
        st.markdown("#### Edit Metric")
        
        metric_ids = df['metricID'].tolist() if 'metricID' in df.columns else []
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            edit_metric_id = st.selectbox("Select Metric ID to Edit", metric_ids)
        
        with col2:
            if edit_metric_id:
                # Get current metric details
                current_metric = df[df['metricID'] == edit_metric_id].iloc[0] if not df[df['metricID'] == edit_metric_id].empty else None
                
                if current_metric is not None:
                    st.write(f"**Current Value:** {current_metric.get('metricValue', 'N/A')}")
                    st.write(f"**Category:** {current_metric.get('category', 'N/A')}")
        
        if edit_metric_id:
            with st.form("edit_metric_form"):
                st.markdown("##### Update Metric Values")
                
                col1, col2 = st.columns(2)
                with col1:
                    new_value = st.text_input("New Value*")
                    new_category = st.selectbox(
                        "Category",
                        ["Study", "Sleep", "Stress", "Attendance"]
                    )
                
                with col2:
                    correction_note = st.text_area(
                        "Correction Note*",
                        placeholder="Reason for correction..."
                    )
                
                submit_edit = st.form_submit_button("💾 Save Changes", use_container_width=True)
                
                if submit_edit:
                    if not new_value or not correction_note:
                        st.error("Please fill in all required fields")
                    else:
                        try:
                            payload = {
                                "metricValue": new_value,
                                "category": new_category,
                                "correctionNote": correction_note
                            }
                            response = requests.put(
                                f"{API_BASE}/data/metrics/{edit_metric_id}",
                                json=payload
                            )
                            
                            if response.status_code == 200:
                                st.success(f"✅ Metric {edit_metric_id} updated successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to update metric: {response.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        # Delete metric option
        st.markdown("---")
        st.markdown("#### Delete Erroneous Metric")
        st.warning("⚠️ Deletion is permanent. Only delete metrics that cannot be corrected.")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            delete_metric_id = st.selectbox("Select Metric to Delete", metric_ids, key="delete_select")
        with col2:
            if st.button("🗑️ Delete Metric", use_container_width=True, type="secondary"):
                if delete_metric_id:
                    try:
                        response = requests.delete(f"{API_BASE}/data/metrics/{delete_metric_id}")
                        if response.status_code == 200:
                            st.success(f"Metric {delete_metric_id} deleted")
                            st.rerun()
                        else:
                            st.error("Failed to delete metric")
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("No metrics found. Showing sample data.")
        sample_metrics = pd.DataFrame({
            'metricID': [1, 2, 3],
            'studentID': [1, 2, 3],
            'metricName': ['study_hr', 'sleep', 'stress'],
            'metricValue': ['3', '7', '5'],
            'category': ['Study', 'Sleep', 'Stress'],
            'metricDate': ['2025-01-01', '2025-01-01', '2025-01-01']
        })
        st.dataframe(sample_metrics, use_container_width=True, hide_index=True)

# ============================================
# TAB 2: Error Tracking (User Story 1.4)
# ============================================
with tab2:
    st.subheader("⚠️ Data Error Tracking")
    st.markdown("Track, report, and resolve data quality issues.")
    
    # Fetch data errors
    try:
        response = requests.get(f"{API_BASE}/data/data-errors")
        if response.status_code == 200:
            errors = response.json()
        else:
            errors = []
    except:
        errors = []
    
    # Error statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_errors = len(errors) if errors else 3
    pending = len([e for e in errors if e.get('errorStatus') == 'Pending']) if errors else 2
    resolved = len([e for e in errors if e.get('errorStatus') in ['Resolved', 'Corrected']]) if errors else 1
    
    with col1:
        st.metric("Total Errors", total_errors)
    with col2:
        st.metric("Pending", pending, delta=None)
    with col3:
        st.metric("Resolved", resolved, delta="+1 today")
    with col4:
        st.metric("Resolution Rate", f"{(resolved/max(total_errors,1))*100:.0f}%")
    
    st.divider()
    
    # Display errors table
    if errors:
        error_df = pd.DataFrame(errors)
        st.dataframe(error_df, use_container_width=True, hide_index=True)
    else:
        sample_errors = pd.DataFrame({
            'errorID': [1, 2, 3],
            'errorType': ['Incorrect Metric Value', 'Missing Data', 'Duplicate Entry'],
            'errorStatus': ['Pending', 'Pending', 'Corrected'],
            'detectedAt': ['2025-01-10', '2025-01-11', '2025-01-09'],
            'adminID': [1, 1, 2]
        })
        st.dataframe(sample_errors, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Report new error
    st.markdown("#### Report New Data Error")
    
    with st.form("report_error_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            error_type = st.selectbox(
                "Error Type*",
                ["Incorrect Metric Value", "Missing Data", "Duplicate Entry", "Invalid Format", "Other"]
            )
            related_metric = st.number_input("Related Metric ID (if applicable)", min_value=0, step=1)
        
        with col2:
            error_description = st.text_area(
                "Description*",
                placeholder="Describe the data error..."
            )
            severity = st.select_slider(
                "Severity",
                options=["Low", "Medium", "High", "Critical"]
            )
        
        submit_error = st.form_submit_button("📝 Report Error", use_container_width=True)
        
        if submit_error:
            if not error_description:
                st.error("Please provide an error description")
            else:
                try:
                    payload = {
                        "errorType": error_type,
                        "description": error_description,
                        "severity": severity,
                        "relatedMetricID": related_metric if related_metric > 0 else None
                    }
                    response = requests.post(f"{API_BASE}/data/data-errors", json=payload)
                    
                    if response.status_code in [200, 201]:
                        st.success("✅ Error reported successfully!")
                    else:
                        st.error("Failed to report error")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Resolve error section
    st.markdown("---")
    st.markdown("#### Resolve Error")
    
    error_ids = [e.get('errorID') for e in errors if e.get('errorStatus') == 'Pending'] if errors else [1, 2]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        resolve_error_id = st.selectbox("Select Error to Resolve", error_ids)
    with col2:
        admin_id = st.number_input("Admin ID", min_value=1, value=1)
    
    resolution_notes = st.text_input("Resolution Notes")
    
    if st.button("✅ Mark as Resolved", use_container_width=True):
        if resolve_error_id:
            try:
                response = requests.put(
                    f"{API_BASE}/data/data-errors/{resolve_error_id}/{admin_id}",
                    json={"resolutionNotes": resolution_notes}
                )
                if response.status_code == 200:
                    st.success(f"Error {resolve_error_id} marked as resolved")
                    st.rerun()
                else:
                    st.error("Failed to resolve error")
            except Exception as e:
                st.error(f"Error: {e}")

# ============================================
# TAB 3: Student Corrections
# ============================================
with tab3:
    st.subheader("👥 Student Data Corrections")
    st.markdown("Update student records to fix incorrect information.")
    
    # Fetch students
    try:
        response = requests.get(f"{API_BASE}/students")
        students = response.json() if response.status_code == 200 else []
    except:
        students = []
    
    if students:
        student_df = pd.DataFrame(students)
        st.dataframe(student_df, use_container_width=True, hide_index=True)
        
        student_options = {f"{s.get('fName', '')} {s.get('lName', '')} (ID: {s.get('studentID')})": s for s in students}
    else:
        sample_students = pd.DataFrame({
            'studentID': [1, 2, 3],
            'fName': ['John', 'Jane', 'Mark'],
            'lName': ['Doe', 'Lee', 'Chan'],
            'email': ['john@example.com', 'jane@example.com', 'mark@example.com'],
            'GPA': [3.50, 3.80, 3.20],
            'major': ['CS', 'Biology', 'Business'],
            'riskFlag': [0, 0, 1]
        })
        st.dataframe(sample_students, use_container_width=True, hide_index=True)
        student_options = {
            "John Doe (ID: 1)": {'studentID': 1, 'fName': 'John', 'lName': 'Doe', 'GPA': 3.50, 'riskFlag': 0},
            "Jane Lee (ID: 2)": {'studentID': 2, 'fName': 'Jane', 'lName': 'Lee', 'GPA': 3.80, 'riskFlag': 0},
            "Mark Chan (ID: 3)": {'studentID': 3, 'fName': 'Mark', 'lName': 'Chan', 'GPA': 3.20, 'riskFlag': 1}
        }
    
    st.markdown("---")
    st.markdown("#### Edit Student Record")
    
    selected_student_edit = st.selectbox(
        "Select Student to Edit",
        options=list(student_options.keys()),
        key="student_edit_select"
    )
    
    if selected_student_edit:
        student_data = student_options[selected_student_edit]
        
        with st.form("edit_student_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_gpa = st.number_input(
                    "GPA",
                    min_value=0.0,
                    max_value=4.0,
                    value=float(student_data.get('GPA', 0)),
                    step=0.01
                )
                new_risk = st.checkbox(
                    "Risk Flag",
                    value=bool(student_data.get('riskFlag', 0))
                )
            
            with col2:
                new_major = st.text_input(
                    "Major",
                    value=student_data.get('major', '')
                )
                new_minor = st.text_input(
                    "Minor",
                    value=student_data.get('minor', '')
                )
            
            correction_reason = st.text_area("Reason for Correction*")
            
            submit_student = st.form_submit_button("💾 Update Student Record", use_container_width=True)
            
            if submit_student:
                if not correction_reason:
                    st.error("Please provide a reason for the correction")
                else:
                    try:
                        payload = {
                            "GPA": new_gpa,
                            "riskFlag": 1 if new_risk else 0,
                            "major": new_major,
                            "minor": new_minor,
                            "correctionNote": correction_reason
                        }
                        response = requests.put(
                            f"{API_BASE}/students/{student_data.get('studentID')}",
                            json=payload
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ Student record updated successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to update: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

# ============================================
# TAB 4: Audit Log
# ============================================
with tab4:
    st.subheader("📋 Audit Log")
    st.markdown("Track all data corrections and modifications for compliance.")
    
    # Date filter
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("From Date", value=datetime(2025, 1, 1))
    with col2:
        end_date = st.date_input("To Date", value=datetime.now())
    with col3:
        if st.button("🔍 Filter", use_container_width=True):
            st.session_state['filter_audit'] = True
    
    # Sample audit log
    audit_log = pd.DataFrame({
        'Timestamp': ['2025-01-15 14:30', '2025-01-14 10:15', '2025-01-13 16:45', '2025-01-12 09:00'],
        'Action': ['Metric Updated', 'Error Resolved', 'Student GPA Corrected', 'Dataset Archived'],
        'User': ['Jordan Lee', 'Jordan Lee', 'Jordan Lee', 'Jordan Lee'],
        'Details': [
            'Metric #2 sleep value: 7 → 6.5',
            'Error #3 marked as resolved',
            'Student #1 GPA: 3.50 → 3.65',
            'Dataset "Legacy Data 2024" archived'
        ],
        'Affected Record': ['metric:2', 'error:3', 'student:1', 'dataset:5']
    })
    
    st.dataframe(audit_log, use_container_width=True, hide_index=True)
    
    # Export audit log
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    with col2:
        csv = audit_log.to_csv(index=False)
        st.download_button(
            label="📥 Export Audit Log",
            data=csv,
            file_name=f"audit_log_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )