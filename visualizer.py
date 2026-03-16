import seaborn as sns
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist
import pandas as pd
import numpy as np
from upsetplot import from_indicators, plot as upset_plot
import io

def create_clustered_heatmap(matrix: pd.DataFrame):
    """
    Generates a Clustered Heatmap using Jaccard metric for similarity.
    Returns a matplotlib figure.
    """
    if matrix.empty:
        return None

    # Calculate dynamic height: ~0.3 inch per row, min 5, max 30
    num_rows = matrix.shape[0]
    fig_height = max(5, min(30, num_rows * 0.3))
    
    # Clustering can fail if the matrix is too small or contains identical rows
    try:
        # Hierarchical clustering using Jaccard metric
        row_linkage = linkage(pdist(matrix, metric='jaccard'), method='average')
        col_linkage = linkage(pdist(matrix.T, metric='jaccard'), method='average')

        # Create the ClusterMap
        g = sns.clustermap(
            matrix,
            row_linkage=row_linkage,
            col_linkage=col_linkage,
            cmap="YlGnBu",
            figsize=(12, fig_height),
            cbar_pos=(0.02, 0.8, 0.03, 0.15),
            yticklabels=True,
            xticklabels=True
        )
    except Exception as e:
        # Fallback to a plain heatmap if clustering fails
        fig, ax = plt.subplots(figsize=(12, fig_height))
        sns.heatmap(matrix, cmap="YlGnBu", ax=ax, yticklabels=True, xticklabels=True)
        ax.set_title(f"Heatmap (Clustering Failed: {e})")
        return fig
    
    plt.setp(g.ax_heatmap.get_yticklabels(), rotation=0)
    plt.setp(g.ax_heatmap.get_xticklabels(), rotation=90)
    
    return g.fig

def create_upset_plot(matrix: pd.DataFrame):
    """
    Generates an UpSet Plot from the binary occurrence matrix.
    """
    if matrix.empty:
        return None

    # Transform matrix for upsetplot library
    # The columns are the "sets". Ensure data is boolean.
    upset_data = from_indicators(lambda x: x == 1, data=matrix.astype(bool))
    
    fig = plt.figure(figsize=(15, 8))
    upset_plot(upset_data, fig=fig, element_size=None)
    
    return fig

def export_plot_to_bytes(fig, format='pdf') -> io.BytesIO:
    """
    Saves a matplotlib figure to a BytesIO object for Streamlit download.
    """
    buf = io.BytesIO()
    fig.savefig(buf, format=format, bbox_inches='tight', dpi=300)
    buf.seek(0)
    return buf
