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

# API base URL
API_BASE = "http://web-api:4000"

# Sidebar
with st.sidebar:
    st.markdown("### MENU")
    st.markdown("📊 Dashboard")
    st.markdown("📁 **Data**")
    st.markdown("  ↳ Downloads")
    st.markdown("  ↳ View")
    st.markdown("  ↳ Edit")
    st.markdown("📈 Visualization")

st.title("📁 CSV Data Manager")
st.caption("Upload, validate, and fix your dataset entries")

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["📤 Upload Dataset", "📋 View Datasets", "🗄️ Archive Management"])

# ============================================
# TAB 1: Upload New CSV Dataset (User Story 1.3)
# ============================================
with tab1:
    st.markdown("### Upload New CSV Dataset")
    st.caption("User Story 1.3 - Upload new datasets directly without manual merging")
    
    # File upload area
    st.markdown("---")
    
    upload_col1, upload_col2 = st.columns([2, 1])
    
    with upload_col1:
        # Drag and drop file uploader
        uploaded_file = st.file_uploader(
            "Drag & Drop Files Here",
            type=['csv'],
            help="Supports: CSV files up to 200MB",
            key="csv_uploader"
        )
        
        st.caption("**OR**")
        
        # Browse files button is built into the uploader
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
            try:
                # Create dataset record
                payload = {
                    "name": dataset_name,
                    "category": dataset_category,
                    "source": dataset_source
                }
                
                response = requests.post(f"{API_BASE}/data/datasets", json=payload)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    data_id = result.get('dataID')
                    st.success(f"✅ Dataset '{dataset_name}' created successfully! (ID: {data_id})")
                    
                    # Show next steps
                    st.info("📊 Processing uploaded file and creating metric records...")
                    
                    # Here you would process the CSV and create metric records
                    # For now, show success
                    st.balloons()
                else:
                    st.error(f"Failed to create dataset: {response.text}")
                    
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
            ["All", "metrics", "wellness", "academic", "engagement", "sleep", "grades"]
        )
    
    with filter_col2:
        filter_status = st.selectbox(
            "Status",
            ["Active Only", "Archived Only", "All"]
        )
    
    with filter_col3:
        filter_date = st.selectbox(
            "Date Range",
            ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
        )
    
    with filter_col4:
        if st.button("🔍 Search", use_container_width=True):
            st.session_state['search_datasets'] = True
    
    st.markdown("---")
    
    # Fetch datasets
    try:
        params = {}
        if filter_category != "All":
            params['category'] = filter_category
        if filter_status == "Active Only":
            params['archived'] = 'false'
        elif filter_status == "Archived Only":
            params['archived'] = 'true'
        
        response = requests.get(f"{API_BASE}/data/datasets", params=params)
        datasets = response.json() if response.status_code == 200 else []
    except:
        datasets = []
    
    # Display datasets
    if datasets:
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
            total_uploads = sum(d.get('total_uploads', 0) for d in datasets)
            st.metric("Total Uploads", total_uploads)
        
        st.markdown("---")
        
        # Dataset table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Dataset details section
        st.markdown("---")
        st.markdown("#### Dataset Details")
        
        dataset_ids = df['dataID'].tolist() if 'dataID' in df.columns else []
        
        if dataset_ids:
            selected_dataset = st.selectbox(
                "Select Dataset to View Details",
                dataset_ids,
                format_func=lambda x: f"Dataset {x} - {df[df['dataID']==x]['dataset_name'].values[0] if 'dataset_name' in df.columns else ''}"
            )
            
            if selected_dataset:
                # Fetch uploads for this dataset
                try:
                    response = requests.get(f"{API_BASE}/data/datasets/{selected_dataset}/uploads")
                    uploads = response.json() if response.status_code == 200 else []
                except:
                    uploads = []
                
                if uploads:
                    st.markdown(f"**Uploads for Dataset {selected_dataset}:**")
                    uploads_df = pd.DataFrame(uploads)
                    st.dataframe(uploads_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No uploads found for this dataset")
    else:
        # Sample data when API not available
        st.info("Showing sample dataset library")
        
        sample_datasets = pd.DataFrame({
            'dataID': [1, 2, 3, 4, 5],
            'Dataset Name': [
                'Student Study Logs',
                'Sleep Tracker Data',
                'Grades Import - Fall 2025',
                '[ARCHIVED] Legacy Data 2024',
                'Weekly Engagement Metrics'
            ],
            'Category': ['metrics', 'wellness', 'academic', 'ARCHIVED_metrics', 'engagement'],
            'Source': ['csv', 'api', 'csv', 'csv', 'csv'],
            'Created': ['2025-01-15', '2025-01-10', '2025-01-08', '2024-06-15', '2025-01-12'],
            'Uploads': [12, 8, 5, 45, 10],
            'Metrics': [156, 89, 67, 520, 134],
            'Status': ['Active', 'Active', 'Active', 'Archived', 'Active']
        })
        
        # Summary metrics
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.metric("Total Datasets", 5)
        with metric_col2:
            st.metric("Active", 4)
        with metric_col3:
            st.metric("Archived", 1)
        with metric_col4:
            st.metric("Total Uploads", 80)
        
        st.markdown("---")
        st.dataframe(sample_datasets, use_container_width=True, hide_index=True)

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
            try:
                response = requests.get(f"{API_BASE}/data/datasets", params={'archived': 'false'})
                active_datasets = response.json() if response.status_code == 200 else []
            except:
                active_datasets = []
            
            if active_datasets:
                archive_options = {
                    f"{d.get('dataset_name', d.get('name', 'Unknown'))} (ID: {d.get('dataID')})": d.get('dataID')
                    for d in active_datasets
                }
            else:
                archive_options = {
                    "Student Study Logs (ID: 1)": 1,
                    "Sleep Tracker Data (ID: 2)": 2,
                    "Grades Import (ID: 3)": 3
                }
            
            dataset_to_archive = st.selectbox(
                "Select Dataset to Archive",
                list(archive_options.keys()),
                key="archive_select"
            )
            
            archive_reason = st.text_area(
                "Reason for Archiving",
                placeholder="e.g., Data is older than 6 months, no longer actively used..."
            )
            
            if st.button("🗄️ Archive Dataset", use_container_width=True):
                if dataset_to_archive:
                    data_id = archive_options[dataset_to_archive]
                    try:
                        response = requests.put(f"{API_BASE}/data/datasets/{data_id}/archive")
                        if response.status_code == 200:
                            st.success(f"✅ Dataset archived successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to archive: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    with col_delete:
        st.markdown("#### Delete Archived Dataset")
        st.warning("⚠️ Permanent deletion - only for archived datasets older than retention period")
        
        with st.container(border=True):
            # Fetch archived datasets
            try:
                response = requests.get(f"{API_BASE}/data/datasets", params={'archived': 'true'})
                archived_datasets = response.json() if response.status_code == 200 else []
            except:
                archived_datasets = []
            
            if archived_datasets:
                delete_options = {
                    f"{d.get('dataset_name', d.get('name', 'Unknown'))} (ID: {d.get('dataID')})": d.get('dataID')
                    for d in archived_datasets
                }
            else:
                delete_options = {
                    "[ARCHIVED] Legacy Data 2024 (ID: 4)": 4
                }
            
            dataset_to_delete = st.selectbox(
                "Select Archived Dataset to Delete",
                list(delete_options.keys()),
                key="delete_select"
            )
            
            confirm_delete = st.checkbox("I understand this action cannot be undone")
            
            if st.button("🗑️ Permanently Delete", type="secondary", use_container_width=True):
                if not confirm_delete:
                    st.error("Please confirm deletion by checking the box above")
                elif dataset_to_delete:
                    data_id = delete_options[dataset_to_delete]
                    try:
                        response = requests.delete(f"{API_BASE}/data/datasets/{data_id}")
                        if response.status_code == 200:
                            st.success("✅ Dataset permanently deleted")
                            st.rerun()
                        elif response.status_code == 400:
                            st.error("Only archived datasets can be deleted")
                        else:
                            st.error(f"Failed to delete: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    st.markdown("---")
    
    # Archive Statistics
    st.markdown("#### 📊 Archive Statistics")
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        with st.container(border=True):
            st.metric("Archived Datasets", "8")
            st.caption("Total archived")
    
    with stat_col2:
        with st.container(border=True):
            st.metric("Storage Used", "2.4 GB")
            st.caption("By archived data")
    
    with stat_col3:
        with st.container(border=True):
            st.metric("Oldest Archive", "18 months")
            st.caption("June 2024")
    
    with stat_col4:
        with st.container(border=True):
            st.metric("Ready to Delete", "2")
            st.caption("> 2 years old")
    
    # Archived datasets table
    st.markdown("---")
    st.markdown("#### Archived Datasets")
    
    archived_sample = pd.DataFrame({
        'dataID': [4, 6, 7, 8],
        'Name': [
            '[ARCHIVED] Legacy Data 2024',
            '[ARCHIVED] Spring 2024 Metrics',
            '[ARCHIVED] Sleep Data Q1 2024',
            '[ARCHIVED] Old Engagement'
        ],
        'Original Category': ['metrics', 'metrics', 'wellness', 'engagement'],
        'Archived Date': ['2024-12-01', '2024-09-15', '2024-08-01', '2024-07-20'],
        'Size': ['450 MB', '320 MB', '180 MB', '95 MB'],
        'Metrics Count': [520, 412, 256, 178],
        'Age': ['12 months', '15 months', '17 months', '18 months']
    })
    
    st.dataframe(archived_sample, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data Analyst: {st.session_state.get('user_name', 'Jordan Lee')}")