import matplotlib
matplotlib.use('Agg') # Force non-interactive backend for stability on macOS
import streamlit as st
import os
import pandas as pd
import subprocess
import platform
from processor import load_and_process_files, filter_matrix
from visualizer import create_clustered_heatmap, create_upset_plot, export_plot_to_bytes

# Page configuration
st.set_page_config(page_title="Target ID Analyzer", layout="wide")

st.title("🧬 Target ID Analyzer")
st.markdown("""
Extracts and compares Target IDs from multiple Excel/CSV files to identify commonalities 
using Clustered Heatmaps (Jaccard) and UpSet Plots.
""")

# Sidebar settings
st.sidebar.header("Configuration")

# Folder and File selection helpers
def select_folder():
    current_os = platform.system()
    try:
        if current_os == "Darwin":  # macOS
            script = 'POSIX path of (choose folder with prompt "Select Data Folder")'
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        elif current_os == "Windows":
            cmd = "Add-Type -AssemblyName System.Windows.Forms; $f = New-Object System.Windows.Forms.FolderBrowserDialog; if($f.ShowDialog() -eq 'OK'){ $f.SelectedPath }"
            result = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        return None
    except Exception as e:
        st.error(f"Folder picker failed: {e}")
        return None

def select_files():
    current_os = platform.system()
    try:
        if current_os == "Darwin":  # macOS
            script = 'choose file with prompt "Select Data Files" of type {"xlsx", "xls", "csv"} with multiple selections allowed'
            # AppleScript returns paths separated by commas or special characters, we need to handle list
            cmd = f'osascript -e \'set theFiles to {script}\' -e \'repeat with aFile in theFiles\' -e \'log (POSIX path of aFile)\' -e \'end repeat\''
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                # Filter stderr where logs usually go for osascript repeat
                paths = [p.strip() for p in result.stderr.split('\n') if p.strip()]
                return paths
        elif current_os == "Windows":
            cmd = "Add-Type -AssemblyName System.Windows.Forms; $f = New-Object System.Windows.Forms.OpenFileDialog; $f.Multiselect = $true; $f.Filter = 'Excel/CSV (*.xlsx;*.xls;*.csv)|*.xlsx;*.xls;*.csv'; if($f.ShowDialog() -eq 'OK'){ $f.FileNames }"
            result = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True)
            if result.returncode == 0:
                return [p.strip() for p in result.stdout.split('\n') if p.strip()]
        return None
    except Exception as e:
        st.error(f"File picker failed: {e}")
        return None

# Initialize session state
if 'data_dir' not in st.session_state:
    st.session_state.data_dir = os.path.join(os.getcwd(), "data")
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = None

st.sidebar.markdown("### 1. Data Selection")
mode = st.sidebar.radio("Selection Mode", ["Folder", "Specific Files"])

if mode == "Folder":
    col1, col2 = st.sidebar.columns([4, 1])
    with col1:
        data_dir = st.text_input("Data Directory Path", value=st.session_state.data_dir)
    with col2:
        st.write("") # Padding
        if st.button("📁", help="Browse Folder"):
            selected = select_folder()
            if selected:
                st.session_state.data_dir = selected
                st.session_state.selected_files = None # Clear file selection
                st.rerun()
    st.session_state.data_dir = data_dir
else:
    if st.sidebar.button("📄 Select Multiple Files"):
        files = select_files()
        if files:
            st.session_state.selected_files = files
            st.session_state.data_dir = None # Clear folder selection
            
    if st.session_state.selected_files:
        st.sidebar.success(f"Selected {len(st.session_state.selected_files)} files.")
        if st.sidebar.button("Clear Selection"):
            st.session_state.selected_files = None
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 2. File Configuration")
target_col = st.sidebar.text_input("Target ID Column Name", value="Target ID")

if st.sidebar.button("🚀 Load and Run Analysis"):
    st.cache_data.clear()

# Load data based on selection
if st.session_state.selected_files:
    matrix, processed_files = load_and_process_files(target_col=target_col, file_paths=st.session_state.selected_files)
else:
    if not os.path.exists(st.session_state.data_dir):
        st.error(f"Directory '{st.session_state.data_dir}' not found.")
        st.stop()
    matrix, processed_files = load_and_process_files(directory_path=st.session_state.data_dir, target_col=target_col)

if matrix.empty:
    st.info("No valid files or data found in the directory. Please check the path and column name.")
    st.stop()

st.sidebar.success(f"Processed {len(processed_files)} files.")

# Filtering
max_freq = int(matrix.sum(axis=1).max())
min_occurrence = st.sidebar.slider("Minimum Occurrence Threshold", 1, max_freq, 1)
show_grid = st.sidebar.checkbox("Show Grid Lines", value=True)

filtered_matrix = filter_matrix(matrix, min_occurrence)

st.write(f"### Filtering Results")
st.write(f"Showing **{filtered_matrix.shape[0]}** unique Target IDs appearing in **{min_occurrence}** or more files.")

if filtered_matrix.empty:
    st.warning("No IDs meet the current threshold.")
    st.stop()

# Visualization Tabs
tab1, tab2, tab3 = st.tabs(["🔥 Clustered Heatmap", "📊 UpSet Plot", "📄 Raw Data"])

with tab1:
    st.header("Clustered Heatmap (Jaccard)")
    with st.spinner("Generating heatmap..."):
        fig_heatmap = create_clustered_heatmap(filtered_matrix, show_grid=show_grid)
        if fig_heatmap:
            st.pyplot(fig_heatmap)
            
            col1, col2 = st.columns(2)
            with col1:
                pdf_data = export_plot_to_bytes(fig_heatmap, 'pdf')
                st.download_button("Download Heatmap (PDF)", pdf_data, "heatmap.pdf", "application/pdf")
            with col2:
                png_data = export_plot_to_bytes(fig_heatmap, 'png')
                st.download_button("Download Heatmap (PNG)", png_data, "heatmap.png", "image/png")

with tab2:
    st.header("UpSet Plot")
    with st.spinner("Generating UpSet plot..."):
        fig_upset = create_upset_plot(filtered_matrix)
        if fig_upset:
            st.pyplot(fig_upset)
            
            col1, col2 = st.columns(2)
            with col1:
                pdf_upset = export_plot_to_bytes(fig_upset, 'pdf')
                st.download_button("Download UpSet (PDF)", pdf_upset, "upset.pdf", "application/pdf")
            with col2:
                png_upset = export_plot_to_bytes(fig_upset, 'png')
                st.download_button("Download UpSet (PNG)", png_upset, "upset.png", "image/png")

with tab3:
    st.header("Binary Occurrence Matrix")
    st.dataframe(filtered_matrix)
    csv = filtered_matrix.to_csv().encode('utf-8')
    st.download_button("Download CSV", csv, "matrix.csv", "text/csv")
