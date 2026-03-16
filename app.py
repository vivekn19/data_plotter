import matplotlib
matplotlib.use('Agg') # Force non-interactive backend for stability on macOS
import streamlit as st
import os
import pandas as pd
import subprocess
import platform
from processor import load_and_process_files, filter_matrix
from visualizer import create_clustered_heatmap, create_upset_plot, create_venn_diagram, export_plot_to_bytes

# Page configuration
st.set_page_config(
    page_title="Target ID Analyzer | Enterprise", 
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def local_css(file_name, theme="dark"):
    if os.path.exists(file_name):
        with open(file_name) as f:
            css_content = f.read()
            # Wrap the entire view in the theme class
            st.markdown(f"""
                <style>
                    {css_content}
                </style>
                <script>
                    var container = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
                    if (container) {{
                        container.className = 'stAppViewContainer theme-{theme}';
                    }}
                    var sidebar = window.parent.document.querySelector('[data-testid="stSidebar"]');
                    if (sidebar) {{
                        sidebar.className = 'stSidebar theme-{theme}';
                    }}
                </script>
            """, unsafe_allow_html=True)

# Initialize Session State
if 'theme' not in st.session_state:
    st.session_state.theme = "dark"

# --- CORE HELPERS ---
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
            cmd = f'osascript -e \'set theFiles to {script}\' -e \'repeat with aFile in theFiles\' -e \'log (POSIX path of aFile)\' -e \'end repeat\''
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
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

# --- UI LOGIC HELPERS ---
def metric_ribbon(files_count, unique_ids, method="Jaccard"):
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-item">
                <div class="metric-value">{files_count}</div>
                <div class="metric-label">Processed Files</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">{unique_ids}</div>
                <div class="metric-label">Unique Targets</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">{method}</div>
                <div class="metric-label">Analysis Method</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def section_header(title, icon="🔹"):
    st.markdown(f"<div style='display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;'><span style='font-size: 1.2rem;'>{icon}</span><span style='font-weight: 600; font-size: 1rem;'>{title}</span></div>", unsafe_allow_html=True)

def branded_loading(text="Processing Analysis..."):
    st.markdown(f"""
        <div class="branded-loader">
            <div class="skeleton-loader"></div>
            <p style='margin-top: 1rem; color: #10B981; font-weight: 600;'>{text}</p>
        </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR REDESIGN ---
with st.sidebar:
    st.markdown(f"""
        <div style='text-align: center; padding: 1.5rem 0;'>
            <h1 style='color: #10B981; margin-bottom: 0; font-size: 1.8rem; letter-spacing: 2px;'>DATA ANALYZER</h1>
            <p style='color: #6b7280; font-size: 0.7rem; font-weight: 600;'>ENTERPRISE BIOTECH SUITE</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Theme Selection
    with st.container():
        section_header("Appearance", "🌗")
        theme_mode = st.selectbox("Application Theme", ["Dark Mode", "Light Mode"], 
                                  index=0 if st.session_state.theme == "dark" else 1,
                                  label_visibility="collapsed")
        new_theme = "dark" if theme_mode == "Dark Mode" else "light"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()

    # Load CSS with current theme
    local_css("/Users/vivekpillai/sania/assets/style.css", theme=st.session_state.theme)
    
    # Selection Card (Native Container)
    with st.container():
        section_header("Data Selection", "📂")
        mode = st.radio("Selection Mode", ["Folder", "Specific Files"], label_visibility="collapsed")
        
        if mode == "Folder":
            data_dir = st.text_input("Directory Path", value=st.session_state.get('data_dir', os.path.join(os.getcwd(), "data")), label_visibility="collapsed")
            if st.button("📁 Browse Directory", use_container_width=True):
                selected = select_folder()
                if selected:
                    st.session_state.data_dir = selected
                    st.session_state.selected_files = None
                    st.rerun()
            st.session_state.data_dir = data_dir
        else:
            if st.button("📄 Select Multiple Files", use_container_width=True):
                files = select_files()
                if files:
                    st.session_state.selected_files = files
                    st.session_state.data_dir = None
            
            if st.session_state.get('selected_files'):
                st.markdown(f'<div style="margin: 0.5rem 0;"><span class="status-badge badge-success">✓ {len(st.session_state.selected_files)} Files</span></div>', unsafe_allow_html=True)
                if st.button("Clear Selection", type="secondary", use_container_width=True):
                    st.session_state.selected_files = None
                    st.rerun()

    # Configuration Card (Native Container)
    with st.container():
        section_header("Analysis Config", "⚙️")
        target_col = st.text_input("Target ID Column", value="Target ID", label_visibility="collapsed")
        
        if st.button("🚀 EXECUTE ANALYSIS", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

# --- MAIN APP FLOW ---

# Header Hero
st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1 style='font-size: 2.8rem; margin-bottom: 0.2rem; font-weight: 800;'>Target ID <span style='color: #10B981;'>Intelligence</span></h1>
        <p style='color: #6b7280; font-size: 1.1rem; max-width: 800px;'>High-throughput cross-dataset intersection and similarity analysis for discovery-phase screening.</p>
    </div>
""", unsafe_allow_html=True)

# Data Ingestion
if st.session_state.get('selected_files'):
    matrix, processed_files = load_and_process_files(target_col=target_col, file_paths=st.session_state.selected_files)
else:
    if not st.session_state.get('data_dir') or not os.path.exists(st.session_state.get('data_dir', "")):
        st.error(f"Selection Required: Please select a valid directory or files in the sidebar.")
        st.stop()
    matrix, processed_files = load_and_process_files(directory_path=st.session_state.data_dir, target_col=target_col)

if matrix.empty:
    st.info("No valid datasets detected. Please verify your source selection and column name.")
    st.stop()

# Stats Ribbon
metric_ribbon(len(processed_files), matrix.shape[0])

# --- REFINED FILTERBAR (Native Container) ---
with st.container():
    section_header("Analysis Controls", "🔍")
    col1, col2 = st.columns([2, 1])
    with col1:
        max_freq = int(matrix.sum(axis=1).max())
        min_occurrence = st.slider("Minimum Occurrence Threshold", 1, max_freq, 1, 
                                    help="Filter targets appearing in fewer than this many files.")
    with col2:
        st.write("") # Spacer
        show_grid = st.checkbox("Enable Heatmap Grid", value=True)

    filtered_matrix = filter_matrix(matrix, min_occurrence)

    # Result Summary Badge
    st.markdown(f"""
        <div style='margin-top: 1rem;'>
            <span class="status-badge badge-info" style="background-color: rgba(59, 130, 246, 0.1); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3);">Intersection: {filtered_matrix.shape[0]} Targets</span>
            <span class="status-badge badge-success">Confidence: ≥ {min_occurrence} Slices</span>
        </div>
    """, unsafe_allow_html=True)

if filtered_matrix.empty:
    st.warning("Filters too restrictive. No data meets current threshold.")
    st.stop()

# --- TABBED NAVIGATION (UNDERLINE STYLE) ---
tab1, tab2, tab3, tab4 = st.tabs(["🔥 HEATMAP", "📊 UPSET PLOT", "⭕ VENN DIAGRAM", "📄 RAW DATA"])

with tab1:
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    heatmap_placeholder = st.empty()
    with heatmap_placeholder.container():
        branded_loading("Rendering Clustered Heatmap...")
    
    fig_heatmap = create_clustered_heatmap(filtered_matrix, show_grid=show_grid)
    if fig_heatmap:
        heatmap_placeholder.pyplot(fig_heatmap)
        
        col1, col2 = st.columns(2)
        with col1:
            pdf_data = export_plot_to_bytes(fig_heatmap, 'pdf')
            st.download_button("💾 DOWNLOAD PDF", pdf_data, "heatmap.pdf", "application/pdf", use_container_width=True, key="h_pdf")
        with col2:
            png_data = export_plot_to_bytes(fig_heatmap, 'png')
            st.download_button("🖼️ DOWNLOAD PNG", png_data, "heatmap.png", "image/png", use_container_width=True, key="h_png")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    upset_placeholder = st.empty()
    with upset_placeholder.container():
        branded_loading("Optimizing Set Intersections...")
    
    fig_upset = create_upset_plot(filtered_matrix)
    if fig_upset:
        upset_placeholder.pyplot(fig_upset)
        
        col1, col2 = st.columns(2)
        with col1:
            pdf_upset = export_plot_to_bytes(fig_upset, 'pdf')
            st.download_button("💾 DOWNLOAD PDF", pdf_upset, "upset.pdf", "application/pdf", use_container_width=True, key="u_pdf")
        with col2:
            png_upset = export_plot_to_bytes(fig_upset, 'png')
            st.download_button("🖼️ DOWNLOAD PNG", png_upset, "upset.png", "image/png", use_container_width=True, key="u_png")
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    st.markdown("<p style='color: #111827; font-weight: 600; font-size: 1.1rem; margin-bottom: 1rem;'>Targeted Comparative Analysis</p>", unsafe_allow_html=True)
    
    with st.form("venn_form"):
        venn_cols = st.multiselect("Select datasets for Venn Comparison (Max 3)", 
                                    options=filtered_matrix.columns.tolist(),
                                    max_selections=3)
        submit_venn = st.form_submit_button("📊 GENERATE VENN DIAGRAM", use_container_width=True)
    
    if submit_venn or (st.session_state.get('venn_active') and not submit_venn):
        if len(venn_cols) in [2, 3]:
            st.session_state.venn_active = True
            st.session_state.venn_cols = venn_cols
            fig_venn = create_venn_diagram(filtered_matrix, venn_cols)
            if fig_venn:
                st.pyplot(fig_venn)
                
                col1, col2 = st.columns(2)
                with col1:
                    pdf_venn = export_plot_to_bytes(fig_venn, 'pdf')
                    st.download_button("💾 DOWNLOAD PDF", pdf_venn, "venn.pdf", "application/pdf", key="vpdf", use_container_width=True)
                with col2:
                    png_venn = export_plot_to_bytes(fig_venn, 'png')
                    st.download_button("🖼️ DOWNLOAD PNG", png_venn, "venn.png", "image/png", key="vpng", use_container_width=True)
        else:
            if submit_venn:
                st.warning("Selection required: Choose 2 or 3 files.")
            st.session_state.venn_active = False
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="graph-container" style="background-color: #0d1117; border: 1px solid rgba(255,255,255,0.05); padding: 5px;">', unsafe_allow_html=True)
    st.dataframe(filtered_matrix, use_container_width=True)
    csv = filtered_matrix.to_csv().encode('utf-8')
    st.download_button("📥 EXPORT BINARY MATRIX (CSV)", csv, "target_matrix.csv", "text/csv", use_container_width=True, key="raw_csv")
    st.markdown('</div>', unsafe_allow_html=True)
