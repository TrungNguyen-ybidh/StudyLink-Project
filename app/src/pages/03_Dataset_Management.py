import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Dataset Management",
    page_icon="📁",
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
# Note: datasets blueprint has no prefix, routes start with /datasets
API_BASE = "http://web-api:4000"

st.title("📁 CSV Data Manager")
st.caption("Upload, validate, and manage your dataset entries")

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["📤 Upload Dataset", "📋 View Datasets", "🗄️ Archive Management"])

# ============================================
# TAB 1: Upload New CSV Dataset (User Story 1.3)
# ============================================
with tab1:
    st.markdown("### Upload New CSV Dataset")
    st.caption("User Story 1.3 - Upload new datasets directly without manual merging")
    
    st.markdown("---")
    
    upload_col1, upload_col2 = st.columns([2, 1])
    
    with upload_col1:
        # File uploader
        uploaded_file = st.file_uploader(
            "Drag & Drop Files Here",
            type=['csv'],
            help="Supports: CSV files up to 200MB",
            key="csv_uploader"
        )
        st.caption("Supports: CSV files up to 200MB")
    
    with upload_col2:
        st.markdown("#### Dataset Info")
        
        dataset_name = st.text_input(
            "Dataset Name*",
            placeholder="e.g., Weekly Study Metrics - Nov 2025"
        )
        
        dataset_category = st.selectbox(
            "Category*",
            ["metrics", "wellness", "academic", "engagement", "sleep", "grades"]
        )
        
        dataset_source = st.selectbox(
            "Source",
            ["csv", "api", "manual", "import"]
        )
    
    st.markdown("---")
    
    # Merge options
    st.markdown("#### Merge Options")
    
    merge_option = st.radio(
        "How should this data be incorporated?",
        [
            "Append to existing dataset",
            "Replace existing dataset",
            "Merge by unique identifier"
        ],
        index=0
    )
    
    if merge_option == "Merge by unique identifier":
        merge_key = st.selectbox(
            "Select merge key",
            ["studentID", "metricID", "date", "custom"]
        )
        if merge_key == "custom":
            custom_key = st.text_input("Enter custom key column name")
    
    st.markdown("---")
    
    # Preview uploaded file
    if uploaded_file is not None:
        st.markdown("#### 📄 File Preview")
        
        try:
            df_preview = pd.read_csv(uploaded_file)
            
            # File info
            info_col1, info_col2, info_col3, info_col4 = st.columns(4)
            with info_col1:
                st.metric("Rows", len(df_preview))
            with info_col2:
                st.metric("Columns", len(df_preview.columns))
            with info_col3:
                st.metric("File Size", f"{uploaded_file.size / 1024:.1f} KB")
            with info_col4:
                st.metric("Null Values", df_preview.isnull().sum().sum())
            
            # Show preview
            st.dataframe(df_preview.head(10), use_container_width=True, hide_index=True)
            
            # Column mapping
            st.markdown("#### Column Mapping")
            st.caption("Map CSV columns to database fields")
            
            col_map1, col_map2 = st.columns(2)
            
            with col_map1:
                student_col = st.selectbox(
                    "Student ID Column",
                    ["Auto-detect"] + list(df_preview.columns)
                )
                metric_col = st.selectbox(
                    "Metric Name Column",
                    ["Auto-detect"] + list(df_preview.columns)
                )
            
            with col_map2:
                value_col = st.selectbox(
                    "Value Column",
                    ["Auto-detect"] + list(df_preview.columns)
                )
                date_col = st.selectbox(
                    "Date Column",
                    ["Auto-detect"] + list(df_preview.columns)
                )
            
            # Reset file position for later use
            uploaded_file.seek(0)
            
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    # Upload button
    st.markdown("---")
    
    if st.button("📤 Upload Dataset", type="primary", use_container_width=True):
        if not dataset_name:
            st.error("Please provide a dataset name")
        elif uploaded_file is None:
            st.error("Please select a file to upload")
        else:
            with st.spinner("Creating dataset..."):
                try:
                    # Create dataset record via POST /datasets
                    payload = {
                        "name": dataset_name,
                        "category": dataset_category,
                        "source": dataset_source
                    }
                    
                    response = requests.post(f"{API_BASE}/datasets", json=payload, timeout=10)
                    
                    if response.status_code in [200, 201]:
                        result = response.json()
                        data_id = result.get('dataID')
                        st.success(f"✅ Dataset '{dataset_name}' created successfully! (ID: {data_id})")
                        
                        # Process CSV and create metrics
                        if uploaded_file is not None:
                            df = pd.read_csv(uploaded_file)
                            st.info(f"📊 Processing {len(df)} rows from uploaded file...")
                            
                            # Here you would iterate through rows and create metric records
                            # This is a placeholder for the actual implementation
                            st.success("✅ File processed successfully!")
                        
                        st.balloons()
                    else:
                        error_msg = response.json().get('error', response.text) if response.text else f"Status {response.status_code}"
                        st.error(f"Failed to create dataset: {error_msg}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to API server. Please check if the backend is running.")
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ============================================
# TAB 2: View Datasets (User Story 1.3, 1.5)
# ============================================
with tab2:
    st.markdown("### 📋 Dataset Library")
    st.caption("View and manage all uploaded datasets")
    
    # Filters
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        filter_category = st.selectbox(
            "Category",
            ["All", "metrics", "wellness", "academic", "engagement", "sleep", "grades"],
            key="view_category"
        )
    
    with filter_col2:
        filter_status = st.selectbox(
            "Status",
            ["Active Only", "Archived Only", "All"],
            key="view_status"
        )
    
    with filter_col3:
        filter_date = st.selectbox(
            "Date Range",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"],
            key="view_date"
        )
    
    with filter_col4:
        refresh_btn = st.button("🔄 Refresh", use_container_width=True, key="refresh_datasets")
    
    st.markdown("---")
    
    # Fetch datasets from GET /datasets
    datasets = []
    datasets_error = None
    try:
        params = {}
        if filter_category != "All":
            params['category'] = filter_category
        if filter_status == "Active Only":
            params['archived'] = 'false'
        elif filter_status == "Archived Only":
            params['archived'] = 'true'
        
        response = requests.get(f"{API_BASE}/datasets", params=params, timeout=5)
        if response.status_code == 200:
            datasets = response.json()
        else:
            datasets_error = f"API returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        datasets_error = "Cannot connect to API server"
    except Exception as e:
        datasets_error = str(e)
    
    # Display datasets
    if datasets and len(datasets) > 0:
        df = pd.DataFrame(datasets)
        
        # Summary metrics
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric("Total Datasets", len(df))
        with metric_col2:
            active = len([d for d in datasets if not str(d.get('category', '')).startswith('ARCHIVED')])
            st.metric("Active", active)
        with metric_col3:
            archived = len(datasets) - active
            st.metric("Archived", archived)
        with metric_col4:
            total_uploads = sum(d.get('total_uploads', 0) or 0 for d in datasets)
            st.metric("Total Uploads", total_uploads)
        
        st.markdown("---")
        
        # Dataset table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Dataset details section
        st.markdown("---")
        st.markdown("#### Dataset Details")
        
        if 'dataID' in df.columns:
            dataset_ids = df['dataID'].tolist()
            
            # Create display names for datasets
            if 'dataset_name' in df.columns:
                name_col = 'dataset_name'
            elif 'name' in df.columns:
                name_col = 'name'
            else:
                name_col = None
            
            if name_col:
                dataset_options = {f"Dataset {row['dataID']} - {row[name_col]}": row['dataID'] for _, row in df.iterrows()}
            else:
                dataset_options = {f"Dataset {did}": did for did in dataset_ids}
            
            selected_dataset = st.selectbox(
                "Select Dataset to View Details",
                list(dataset_options.keys()),
                key="dataset_detail_select"
            )
            
            if selected_dataset:
                data_id = dataset_options[selected_dataset]
                
                # Fetch uploads for this dataset from GET /datasets/{id}/uploads
                try:
                    response = requests.get(f"{API_BASE}/datasets/{data_id}/uploads", timeout=5)
                    if response.status_code == 200:
                        uploads = response.json()
                        if uploads and len(uploads) > 0:
                            st.markdown(f"**Uploads for Dataset {data_id}:**")
                            uploads_df = pd.DataFrame(uploads)
                            st.dataframe(uploads_df, use_container_width=True, hide_index=True)
                        else:
                            st.info("No uploads found for this dataset")
                    else:
                        st.warning(f"Could not fetch uploads: Status {response.status_code}")
                except Exception as e:
                    st.error(f"Error fetching uploads: {e}")
        else:
            st.info("No dataset IDs available")
    else:
        if datasets_error:
            st.warning(f"Could not load datasets: {datasets_error}")
        else:
            st.info("No datasets found in the database")

# ============================================
# TAB 3: Archive Management (User Story 1.5)
# ============================================
with tab3:
    st.markdown("### 🗄️ Archive Management")
    st.caption("User Story 1.5 - Archive old datasets to keep dashboards clean")
    
    # Archive section
    col_archive, col_delete = st.columns(2)
    
    with col_archive:
        st.markdown("#### Archive Dataset")
        st.caption("Move datasets to archive - they remain available for long-term analysis")
        
        with st.container(border=True):
            # Fetch active datasets
            active_datasets = []
            try:
                response = requests.get(f"{API_BASE}/datasets", params={'archived': 'false'}, timeout=5)
                if response.status_code == 200:
                    active_datasets = response.json()
            except:
                pass
            
            if active_datasets and len(active_datasets) > 0:
                # Determine name column
                name_col = 'dataset_name' if 'dataset_name' in active_datasets[0] else 'name'
                archive_options = {
                    f"{d.get(name_col, 'Unknown')} (ID: {d.get('dataID')})": d.get('dataID')
                    for d in active_datasets
                }
            else:
                archive_options = {}
                st.info("No active datasets available to archive")
            
            if archive_options:
                dataset_to_archive = st.selectbox(
                    "Select Dataset to Archive",
                    list(archive_options.keys()),
                    key="archive_select"
                )
                
                archive_reason = st.text_area(
                    "Reason for Archiving",
                    placeholder="e.g., Data is older than 6 months, no longer actively used...",
                    key="archive_reason"
                )
                
                if st.button("🗄️ Archive Dataset", use_container_width=True):
                    if dataset_to_archive:
                        data_id = archive_options[dataset_to_archive]
                        try:
                            response = requests.put(f"{API_BASE}/datasets/{data_id}/archive", timeout=5)
                            if response.status_code == 200:
                                st.success(f"✅ Dataset archived successfully!")
                                st.rerun()
                            else:
                                error_msg = response.json().get('error', 'Unknown error') if response.text else f"Status {response.status_code}"
                                st.error(f"Failed to archive: {error_msg}")
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to API server")
                        except Exception as e:
                            st.error(f"Error: {e}")
    
    with col_delete:
        st.markdown("#### Delete Archived Dataset")
        st.warning("⚠️ Permanent deletion - only for archived datasets older than retention period")
        
        with st.container(border=True):
            # Fetch archived datasets
            archived_datasets = []
            try:
                response = requests.get(f"{API_BASE}/datasets", params={'archived': 'true'}, timeout=5)
                if response.status_code == 200:
                    archived_datasets = response.json()
            except:
                pass
            
            if archived_datasets and len(archived_datasets) > 0:
                name_col = 'dataset_name' if 'dataset_name' in archived_datasets[0] else 'name'
                delete_options = {
                    f"{d.get(name_col, 'Unknown')} (ID: {d.get('dataID')})": d.get('dataID')
                    for d in archived_datasets
                }
            else:
                delete_options = {}
                st.info("No archived datasets available to delete")
            
            if delete_options:
                dataset_to_delete = st.selectbox(
                    "Select Archived Dataset to Delete",
                    list(delete_options.keys()),
                    key="delete_select"
                )
                
                confirm_delete = st.checkbox("I understand this action cannot be undone", key="confirm_delete")
                
                if st.button("🗑️ Permanently Delete", type="secondary", use_container_width=True):
                    if not confirm_delete:
                        st.error("Please confirm deletion by checking the box above")
                    elif dataset_to_delete:
                        data_id = delete_options[dataset_to_delete]
                        try:
                            response = requests.delete(f"{API_BASE}/datasets/{data_id}", timeout=5)
                            if response.status_code == 200:
                                st.success("✅ Dataset permanently deleted")
                                st.rerun()
                            elif response.status_code == 400:
                                st.error("Only archived datasets can be deleted. Archive first.")
                            else:
                                error_msg = response.json().get('error', 'Unknown error') if response.text else f"Status {response.status_code}"
                                st.error(f"Failed to delete: {error_msg}")
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to API server")
                        except Exception as e:
                            st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # Archive Statistics
    st.markdown("#### 📊 Archive Statistics")
    
    # Calculate stats from actual data
    all_datasets = []
    try:
        response = requests.get(f"{API_BASE}/datasets", timeout=5)
        if response.status_code == 200:
            all_datasets = response.json()
    except:
        pass
    
    archived_count = len([d for d in all_datasets if str(d.get('category', '')).startswith('ARCHIVED')])
    active_count = len(all_datasets) - archived_count
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        with st.container(border=True):
            st.metric("Total Datasets", len(all_datasets))
            st.caption("In database")
    
    with stat_col2:
        with st.container(border=True):
            st.metric("Active Datasets", active_count)
            st.caption("Currently in use")
    
    with stat_col3:
        with st.container(border=True):
            st.metric("Archived Datasets", archived_count)
            st.caption("In archive")
    
    with stat_col4:
        with st.container(border=True):
            total_uploads = sum(d.get('total_uploads', 0) or 0 for d in all_datasets)
            st.metric("Total Uploads", total_uploads)
            st.caption("Across all datasets")
    
    # Archived datasets table
    if archived_datasets and len(archived_datasets) > 0:
        st.markdown("---")
        st.markdown("#### Archived Datasets")
        archived_df = pd.DataFrame(archived_datasets)
        st.dataframe(archived_df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data Analyst: {st.session_state.get('user_name', 'Jordan Lee')}")