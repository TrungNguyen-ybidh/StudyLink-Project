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

# API base URL - connects to Flask backend
# metrics blueprint is registered with /data prefix
API_BASE = "http://web-api:4000"

st.title("Data Quality Tools")
st.caption("User Story 1.4 - Fix, correct, and maintain data integrity")

# Tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs(["Metrics Editor", "Error Tracking", "Assignments", "Audit Log"])

# ============================================
# TAB 1: Metrics Editor (User Story 1.4)
# ============================================
with tab1:
    st.subheader("Metrics Editor")
    st.markdown("Search, view, and correct metric entries to ensure data accuracy.")
    
    # Search filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        student_id_filter = st.text_input("Student ID", placeholder="e.g., 1", key="metric_student_filter")
    
    with col2:
        metric_category = st.selectbox(
            "Category",
            ["All", "Study", "Sleep", "Stress", "Attendance", "wellness", "academic"],
            key="metric_category_filter"
        )
    
    with col3:
        metric_type = st.selectbox(
            "Metric Type",
            ["All", "study_hr", "sleep", "stress", "attendance", "numeric"],
            key="metric_type_filter"
        )
    
    with col4:
        if st.button("Search Metrics", use_container_width=True):
            st.session_state['search_metrics'] = True
    
    # Fetch metrics from GET /data/metrics
    metrics = []
    metrics_error = None
    try:
        params = {}
        if student_id_filter:
            params['studentID'] = student_id_filter
        if metric_category != "All":
            params['category'] = metric_category
        if metric_type != "All":
            params['metricType'] = metric_type
        
        response = requests.get(f"{API_BASE}/data/metrics", params=params, timeout=5)
        if response.status_code == 200:
            metrics = response.json()
        else:
            metrics_error = f"API returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        metrics_error = "Cannot connect to API server"
    except Exception as e:
        metrics_error = str(e)
    
    # Display metrics table
    if metrics and len(metrics) > 0:
        df = pd.DataFrame(metrics)
        st.caption(f"Found {len(df)} metrics")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Edit metric section
        st.markdown("---")
        st.markdown("#### Edit Metric")
        
        metric_ids = df['metricID'].tolist() if 'metricID' in df.columns else []
        
        if metric_ids:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                edit_metric_id = st.selectbox("Select Metric ID to Edit", metric_ids, key="edit_metric_select")
            
            with col2:
                if edit_metric_id:
                    # Get current metric details
                    current_metric = df[df['metricID'] == edit_metric_id].iloc[0] if not df[df['metricID'] == edit_metric_id].empty else None
                    
                    if current_metric is not None:
                        st.write(f"**Current Value:** {current_metric.get('metricValue', 'N/A')}")
                        st.write(f"**Category:** {current_metric.get('category', 'N/A')}")
                        st.write(f"**Metric Name:** {current_metric.get('metricName', 'N/A')}")
            
            if edit_metric_id:
                with st.form("edit_metric_form"):
                    st.markdown("##### Update Metric Values")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_value = st.text_input("New Value*", key="new_metric_value")
                        new_category = st.selectbox(
                            "Category",
                            ["Study", "Sleep", "Stress", "Attendance", "wellness", "academic"],
                            key="new_metric_category"
                        )
                    
                    with col2:
                        new_privacy = st.selectbox(
                            "Privacy Level",
                            ["low", "medium", "high"],
                            key="new_privacy_level"
                        )
                    
                    submit_edit = st.form_submit_button("Save Changes", use_container_width=True)
                    
                    if submit_edit:
                        if not new_value:
                            st.error("Please provide a new value")
                        else:
                            try:
                                payload = {
                                    "metricValue": new_value,
                                    "category": new_category,
                                    "privacyLevel": new_privacy
                                }
                                response = requests.put(
                                    f"{API_BASE}/data/metrics/{edit_metric_id}",
                                    json=payload,
                                    timeout=5
                                )
                                
                                if response.status_code == 200:
                                    st.success(f"Metric {edit_metric_id} updated successfully!")
                                    st.rerun()
                                else:
                                    error_msg = response.json().get('error', 'Unknown error') if response.text else f"Status {response.status_code}"
                                    st.error(f"Failed to update metric: {error_msg}")
                            except requests.exceptions.ConnectionError:
                                st.error("Cannot connect to API server")
                            except Exception as e:
                                st.error(f"Error: {e}")
            
            # Delete metric option
            st.markdown("---")
            st.markdown("#### Delete Erroneous Metric")
            st.warning("Deletion is permanent. Only delete metrics that cannot be corrected.")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                delete_metric_id = st.selectbox("Select Metric to Delete", metric_ids, key="delete_metric_select")
            with col2:
                if st.button("Delete Metric", use_container_width=True, type="secondary"):
                    if delete_metric_id:
                        try:
                            response = requests.delete(f"{API_BASE}/data/metrics/{delete_metric_id}", timeout=5)
                            if response.status_code == 200:
                                st.success(f"Metric {delete_metric_id} deleted")
                                st.rerun()
                            else:
                                error_msg = response.json().get('error', 'Unknown error') if response.text else f"Status {response.status_code}"
                                st.error(f"Failed to delete: {error_msg}")
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to API server")
                        except Exception as e:
                            st.error(f"Error: {e}")
    else:
        if metrics_error:
            st.warning(f"Could not load metrics: {metrics_error}")
        else:
            st.info("No metrics found matching your filters. Try adjusting the search criteria.")
        
        # Create new metric section
        st.markdown("---")
        st.markdown("#### Create New Metric")
        
        with st.form("create_metric_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_student_id = st.number_input("Student ID*", min_value=1, step=1, key="new_student_id")
                new_metric_name = st.text_input("Metric Name*", placeholder="e.g., study_hr", key="new_metric_name")
                new_metric_value = st.text_input("Metric Value*", placeholder="e.g., 5.5", key="new_metric_value_create")
            with col2:
                new_category_create = st.selectbox("Category*", ["Study", "Sleep", "Stress", "Attendance"], key="new_category_create")
                new_course_id = st.number_input("Course ID (optional)", min_value=0, step=1, key="new_course_id")
                new_unit = st.text_input("Unit", placeholder="e.g., hours", key="new_unit")
            
            submit_create = st.form_submit_button("Create Metric", use_container_width=True)
            
            if submit_create:
                if not new_metric_name or not new_metric_value:
                    st.error("Please fill in all required fields")
                else:
                    try:
                        payload = {
                            "studentID": new_student_id,
                            "metricName": new_metric_name,
                            "metricValue": new_metric_value,
                            "category": new_category_create,
                            "courseID": new_course_id if new_course_id > 0 else None,
                            "unit": new_unit
                        }
                        response = requests.post(f"{API_BASE}/data/metrics", json=payload, timeout=5)
                        
                        if response.status_code in [200, 201]:
                            result = response.json()
                            st.success(f"Metric created with ID: {result.get('metricID')}")
                            st.rerun()
                        else:
                            error_msg = response.json().get('error', 'Unknown error') if response.text else f"Status {response.status_code}"
                            st.error(f"Failed to create metric: {error_msg}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to API server")
                    except Exception as e:
                        st.error(f"Error: {e}")

# ============================================
# TAB 2: Error Tracking (User Story 1.4)
# ============================================
with tab2:
    st.subheader("Data Error Tracking")
    st.markdown("Track, report, and resolve data quality issues.")
    
    # Fetch data errors from GET /data/data-errors
    errors = []
    errors_error = None
    try:
        response = requests.get(f"{API_BASE}/data/data-errors", timeout=5)
        if response.status_code == 200:
            errors = response.json()
        else:
            errors_error = f"API returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        errors_error = "Cannot connect to API server"
    except Exception as e:
        errors_error = str(e)
    
    # Error statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_errors = len(errors)
    pending = len([e for e in errors if e.get('errorStatus') in ['Pending', 'detected']]) if errors else 0
    resolved = len([e for e in errors if e.get('errorStatus') in ['Resolved', 'Corrected', 'corrected']]) if errors else 0
    
    with col1:
        st.metric("Total Errors", total_errors)
    with col2:
        st.metric("Pending", pending)
    with col3:
        st.metric("Resolved", resolved)
    with col4:
        rate = (resolved / max(total_errors, 1)) * 100
        st.metric("Resolution Rate", f"{rate:.0f}%")
    
    st.divider()
    
    # Display errors table
    if errors and len(errors) > 0:
        error_df = pd.DataFrame(errors)
        st.caption(f"Showing {len(error_df)} error records")
        st.dataframe(error_df, use_container_width=True, hide_index=True)
    else:
        if errors_error:
            st.warning(f"Could not load errors: {errors_error}")
        else:
            st.info("No data errors found in the system")
    
    st.divider()
    
    # Report new error
    st.markdown("#### Report New Data Error")
    
    with st.form("report_error_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            error_id = st.number_input("Error ID*", min_value=1, step=1, key="new_error_id")
            error_type = st.selectbox(
                "Error Type*",
                ["Incorrect Metric Value", "Missing Data", "Duplicate Entry", "Invalid Format", "Other"],
                key="new_error_type"
            )
        
        with col2:
            admin_id = st.number_input("Admin ID*", min_value=1, value=1, step=1, key="new_admin_id")
            error_status = st.selectbox(
                "Initial Status",
                ["detected", "Pending", "In Progress"],
                key="new_error_status"
            )
        
        submit_error = st.form_submit_button("Report Error", use_container_width=True)
        
        if submit_error:
            try:
                payload = {
                    "errorID": error_id,
                    "adminID": admin_id,
                    "errorType": error_type,
                    "errorStatus": error_status
                }
                response = requests.post(f"{API_BASE}/data/data-errors", json=payload, timeout=5)
                
                if response.status_code in [200, 201]:
                    st.success("Error reported successfully!")
                    st.rerun()
                else:
                    error_msg = response.json().get('error', 'Unknown error') if response.text else f"Status {response.status_code}"
                    st.error(f"Failed to report error: {error_msg}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API server")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Resolve error section
    if errors and len(errors) > 0:
        st.markdown("---")
        st.markdown("#### Resolve Error")
        
        pending_errors = [e for e in errors if e.get('errorStatus') in ['Pending', 'detected', 'In Progress']]
        
        if pending_errors:
            error_options = {
                f"Error {e.get('errorID')} - {e.get('errorType', 'Unknown')} ({e.get('errorStatus')})": (e.get('errorID'), e.get('adminID'))
                for e in pending_errors
            }
            
            col1, col2 = st.columns([2, 1])
            with col1:
                resolve_error_key = st.selectbox("Select Error to Resolve", list(error_options.keys()), key="resolve_error_select")
            with col2:
                new_status = st.selectbox("New Status", ["Resolved", "Corrected", "Closed"], key="resolve_status")
            
            if st.button("Update Status", use_container_width=True):
                if resolve_error_key:
                    error_id, admin_id = error_options[resolve_error_key]
                    try:
                        response = requests.put(
                            f"{API_BASE}/data/data-errors/{error_id}/{admin_id}",
                            json={"errorStatus": new_status},
                            timeout=5
                        )
                        if response.status_code == 200:
                            st.success(f"Error {error_id} status updated to {new_status}")
                            st.rerun()
                        else:
                            error_msg = response.json().get('error', 'Unknown error') if response.text else f"Status {response.status_code}"
                            st.error(f"Failed to update: {error_msg}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to API server")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.success("🎉 No pending errors to resolve!")

# ============================================
# TAB 3: Assignments (User Stories 1.2, 1.4, 1.6)
# ============================================
with tab3:
    st.subheader("Assignment Management")
    st.markdown("View and update assignment data")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        course_filter = st.text_input("Course ID", placeholder="e.g., 1", key="assignment_course_filter")
    
    with col2:
        status_filter = st.selectbox(
            "Status",
            ["All", "pending", "submitted", "graded"],
            key="assignment_status_filter"
        )
    
    with col3:
        type_filter = st.selectbox(
            "Type",
            ["All", "homework", "exam", "project", "quiz"],
            key="assignment_type_filter"
        )
    
    with col4:
        if st.button("Search Assignments", use_container_width=True, key="search_assignments"):
            st.session_state['search_assignments'] = True
    
    # Fetch assignments from GET /data/assignments
    assignments = []
    assignments_error = None
    try:
        params = {}
        if course_filter:
            params['courseID'] = course_filter
        if status_filter != "All":
            params['status'] = status_filter
        if type_filter != "All":
            params['type'] = type_filter
        
        response = requests.get(f"{API_BASE}/data/assignments", params=params, timeout=5)
        if response.status_code == 200:
            assignments = response.json()
        else:
            assignments_error = f"API returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        assignments_error = "Cannot connect to API server"
    except Exception as e:
        assignments_error = str(e)
    
    if assignments and len(assignments) > 0:
        assignments_df = pd.DataFrame(assignments)
        st.caption(f"Found {len(assignments_df)} assignments")
        st.dataframe(assignments_df, use_container_width=True, hide_index=True)
        
        # Edit assignment section
        st.markdown("---")
        st.markdown("#### Update Assignment")
        
        if 'assignmentID' in assignments_df.columns:
            assignment_ids = assignments_df['assignmentID'].tolist()
            
            col1, col2 = st.columns([1, 2])
            with col1:
                edit_assignment_id = st.selectbox("Select Assignment ID", assignment_ids, key="edit_assignment_select")
            
            with col2:
                if edit_assignment_id:
                    current_assignment = assignments_df[assignments_df['assignmentID'] == edit_assignment_id].iloc[0]
                    st.write(f"**Title:** {current_assignment.get('title', 'N/A')}")
                    st.write(f"**Current Score:** {current_assignment.get('scoreReceived', 'N/A')}")
                    st.write(f"**Status:** {current_assignment.get('status', 'N/A')}")
            
            if edit_assignment_id:
                with st.form("edit_assignment_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_score = st.number_input("New Score", min_value=0.0, max_value=100.0, step=0.5, key="new_assignment_score")
                        new_assignment_status = st.selectbox("Status", ["pending", "submitted", "graded"], key="new_assignment_status")
                    with col2:
                        new_weight = st.number_input("Weight (%)", min_value=0.0, max_value=100.0, step=1.0, key="new_assignment_weight")
                    
                    submit_assignment = st.form_submit_button("Update Assignment", use_container_width=True)
                    
                    if submit_assignment:
                        try:
                            payload = {}
                            if new_score > 0:
                                payload['scoreReceived'] = new_score
                            if new_assignment_status:
                                payload['status'] = new_assignment_status
                            if new_weight > 0:
                                payload['weight'] = new_weight
                            
                            if payload:
                                response = requests.put(
                                    f"{API_BASE}/data/assignments/{edit_assignment_id}",
                                    json=payload,
                                    timeout=5
                                )
                                
                                if response.status_code == 200:
                                    st.success(f"Assignment {edit_assignment_id} updated!")
                                    st.rerun()
                                else:
                                    error_msg = response.json().get('error', 'Unknown error') if response.text else f"Status {response.status_code}"
                                    st.error(f"Failed to update: {error_msg}")
                            else:
                                st.warning("No changes to save")
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to API server")
                        except Exception as e:
                            st.error(f"Error: {e}")
    else:
        if assignments_error:
            st.warning(f"Could not load assignments: {assignments_error}")
        else:
            st.info("No assignments found matching your filters")

# ============================================
# TAB 4: Audit Log
# ============================================
with tab4:
    st.subheader("Audit Log")
    st.markdown("Track all data corrections and modifications for compliance.")
    
    st.info("The audit log tracks all changes made through this interface. Corrections are automatically logged in the metric description field with [CORRECTED] tags.")
    
    # Date filter
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("From Date", value=datetime(2025, 1, 1), key="audit_start")
    with col2:
        end_date = st.date_input("To Date", value=datetime.now(), key="audit_end")
    with col3:
        if st.button("Filter", use_container_width=True, key="filter_audit"):
            st.session_state['filter_audit'] = True
    
    # Fetch metrics that have been corrected (contain [CORRECTED] in description)
    corrected_metrics = []
    try:
        response = requests.get(f"{API_BASE}/data/metrics", timeout=5)
        if response.status_code == 200:
            all_metrics = response.json()
            corrected_metrics = [m for m in all_metrics if m.get('description') and '[CORRECTED]' in str(m.get('description', ''))]
    except:
        pass
    
    if corrected_metrics:
        st.markdown("#### Corrected Metrics")
        corrected_df = pd.DataFrame(corrected_metrics)
        
        # Select relevant columns for audit display
        display_cols = ['metricID', 'studentID', 'metricName', 'metricValue', 'category', 'metricDate', 'description']
        available_cols = [c for c in display_cols if c in corrected_df.columns]
        
        if available_cols:
            st.dataframe(corrected_df[available_cols], use_container_width=True, hide_index=True)
        else:
            st.dataframe(corrected_df, use_container_width=True, hide_index=True)
        
        # Export audit log
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col2:
            csv = corrected_df.to_csv(index=False)
            st.download_button(
                label="📥 Export Audit Log",
                data=csv,
                file_name=f"audit_log_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("No corrected metrics found in the audit log")
    
    # Also show resolved errors as part of audit
    st.markdown("---")
    st.markdown("#### Resolved Data Errors")
    
    resolved_errors = []
    try:
        response = requests.get(f"{API_BASE}/data/data-errors", params={'errorStatus': 'Resolved'}, timeout=5)
        if response.status_code == 200:
            all_errors = response.json()
            resolved_errors = [e for e in all_errors if e.get('errorStatus') in ['Resolved', 'Corrected', 'corrected']]
    except:
        pass
    
    if resolved_errors:
        resolved_df = pd.DataFrame(resolved_errors)
        st.dataframe(resolved_df, use_container_width=True, hide_index=True)
    else:
        st.info("No resolved errors to display")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data Analyst: {st.session_state.get('user_name', 'Jordan Lee')}")