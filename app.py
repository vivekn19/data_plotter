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

# Folder selection helper
def select_folder():
    current_os = platform.system()
    try:
        if current_os == "Darwin":  # macOS
            script = 'POSIX path of (choose folder with prompt "Select Data Folder")'
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        elif current_os == "Windows":
            # Native folder picker via PowerShell for Windows stability
            cmd = (
                "Add-Type -AssemblyName System.Windows.Forms; "
                "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
                "$f.ShowNewFolderButton = $true; "
                "$result = $f.ShowDialog(); "
                "if($result -eq 'OK'){ $f.SelectedPath }"
            )
            result = subprocess.run(['powershell', '-Command', cmd], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        else:
            # Linux fallback (if zenity is installed)
            try:
                result = subprocess.run(['zenity', '--file-selection', '--directory'], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass
        return None
    except Exception as e:
        st.error(f"Folder picker failed: {e}")
        return None

# Initialize session state for directory
if 'data_dir' not in st.session_state:
    st.session_state.data_dir = os.path.join(os.getcwd(), "data")

col1, col2 = st.sidebar.columns([3, 1])
with col1:
    data_dir = st.text_input("Data Directory Path", value=st.session_state.data_dir)
with col2:
    st.write("") # Padding
    if st.button("📁", help="Browse Folder"):
        selected = select_folder()
        if selected:
            st.session_state.data_dir = selected
            st.rerun()

target_col = st.sidebar.text_input("Target ID Column Name", value="Target ID")

if st.sidebar.button("Load Data"):
    st.cache_data.clear()
    st.session_state.data_dir = data_dir # Update from text input just in case

# Main logic
if not os.path.exists(data_dir):
    st.error(f"Directory '{data_dir}' not found. Please create it and add your 64 files.")
    st.stop()

# Load data
matrix, processed_files = load_and_process_files(data_dir, target_col)

if matrix.empty:
    st.info("No valid files or data found in the directory. Please check the path and column name.")
    st.stop()

st.sidebar.success(f"Processed {len(processed_files)} files.")

# Filtering
max_freq = int(matrix.sum(axis=1).max())
min_occurrence = st.sidebar.slider("Minimum Occurrence Threshold", 1, max_freq, 1)

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
        fig_heatmap = create_clustered_heatmap(filtered_matrix)
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
