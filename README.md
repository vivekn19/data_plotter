# Target ID Analyzer

A robust, interactive Python suite designed to cross-reference and visualize Target ID occurrences across large datasets. This tool was built to handle 60+ Excel/CSV files simultaneously, providing researchers with clear, publication-quality insights into data overlaps and intersections.

---

## 🎨 Overview

When working with dozens of experimental datasets, identifying common proteins or targets manually is nearly impossible. The **Target ID Analyzer** automates this process. It constructs a binary occurrence matrix from your files and applies hierarchical clustering to reveal hidden relationships between your samples.

### Key Capabilities
*   **Intelligent Cross-Referencing**: Instantly identifies shared Target IDs across an unlimited number of files.
*   **Scientific Precision**: Uses the **Jaccard Metric** for clustering—the industry standard for binary (presence/absence) data.
*   **Interactive Analytics**: Explore your data via dynamic Heatmaps and UpSet Plots.
*   **Publication Ready**: Export high-resolution (300 DPI) PDF and PNG versions of your visualizations for papers or presentations.

---

## 🚀 Quick Start

If you are already familiar with Python, follow these three steps:

1.  **Clone & Navigate**:
    ```bash
    git clone https://github.com/vivekn19/data_plotter.git && cd data_plotter
    ```
2.  **Environment Setup**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Launch Interface**:
    ```bash
    python3 -m streamlit run app.py
    ```

---

## 🛠 Detailed Installation Guide

### 1. Prerequisites
Ensure you have **Python 3.9+** installed. You can verify this by running `python3 --version` in your terminal. If you don't have it, download it from [python.org](https://www.python.org/).

### 2. Organizing Your Data
1.  Locate the `/data` folder within the project directory.
2.  Drop your Excel (`.xlsx`) or CSV (`.csv`) files here. 
3.  **Note**: Ensure your files contain a column for your identifiers. The tool defaults to looking for a column named **"Target ID"**, but you can customize this in the interface.

---

## 📊 Using the Analyzer

Once the application launches in your browser, the workflow is straightforward:

### Data Loading
In the left sidebar, click **"Load Data"**. The tool will process all files in the background, cleaning whitespace and normalizing text to ensure accurate matching.

### Refining the View
Use the **Minimum Occurrence Threshold** slider to filter out noise. For example, setting the threshold to **10** will only display Target IDs that appear in 10 or more files, making large-scale heatmaps much easier to interpret.

### Exploring the Plots
The data is organized into four specialized tabs:
*   **Clustered Heatmap**: Files and Target IDs are automatically rearranged to place similar samples next to each other, revealing "blocks" of shared data.
*   **UpSet Plot**: A modern alternative to Venn Diagrams optimized for large numbers of sets. It visualizes the frequency of specific file intersections.
*   **Venn Diagram**: A classic visualization specifically for focused 2-way or 3-way comparisons.
*   **Raw Matrix**: Access the underlying binary data in the "Raw Data" tab and download it as a CSV.

---

## 💾 Technical Notes
*   **Performance**: Uses `@st.cache_data` and vectorized Pandas operations to ensure the UI remains responsive, even with thousands of identifiers.
*   **Clustering**: Leverages `scipy.cluster.hierarchy` for average-linkage clustering based on Jaccard distances.
*   **Fallbacks**: If clustering is not mathematically possible (e.g., identical rows), the tool gracefully falls back to a standard heatmap to ensure you never lose visibility of your data.

---

## 🤝 Support
If you encounter any issues or have feature requests, please open an issue in the repository or reach out to the project maintainer. 
