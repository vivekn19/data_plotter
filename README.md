# Target ID Analyzer

A Python-based data analysis tool that processes multiple Excel/CSV files to identify common "Target IDs" and generates scalable, interactive Clustered Heatmaps and UpSet Plots.

## Features
- **Optimized Data Processing**: Cached loading and vectorized matrix transformation for 64+ files.
- **Hierarchical Clustering**: Uses the **Jaccard metric** for accurate presence/absence similarity.
- **Interactive Visualizations**: Clustered Heatmaps (Seaborn) and UpSet Plots (Upsetplot).
- **Streamlit Interface**: Real-time filtering with a frequency threshold slider and dynamic figure scaling.
- **High-Resolution Exports**: Download results as high-quality PDF or PNG.

## Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional) Install Watchdog for better Streamlit performance:
   ```bash
   pip install watchdog
   ```

## Usage
Run the application:
```bash
python3 -m streamlit run app.py
```

Place your `.xlsx` or `.csv` files in the `data/` directory. By default, the tool looks for a column named "Target ID".

## Technology Stack
- **Data**: pandas, numpy
- **Clustering**: scipy, scikit-learn
- **Visualization**: seaborn, matplotlib, plotly, upsetplot
- **UI Framework**: streamlit
