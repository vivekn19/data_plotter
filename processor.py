import pandas as pd
import os
import streamlit as st
from typing import List, Tuple, Optional

@st.cache_data
def load_and_process_files(directory_path: Optional[str] = None, target_col: str = "Target ID", file_paths: Optional[List[str]] = None) -> Tuple[pd.DataFrame, List[str]]:
    """
    Processes files from a directory OR a specific list of file paths.
    Extracts Target IDs, cleans them, and returns a Binary Occurrence Matrix.
    """
    all_data = []
    processed_files = []
    valid_extensions = ('.xlsx', '.xls', '.csv')

    # Determine which files to process
    if file_paths:
        target_files = [p for p in file_paths if p.lower().endswith(valid_extensions)]
    elif directory_path and os.path.exists(directory_path):
        target_files = [os.path.join(directory_path, f) for f in os.listdir(directory_path) if f.lower().endswith(valid_extensions)]
    else:
        return pd.DataFrame(), []
    
    for filepath in target_files:
        filename = os.path.basename(filepath)
        try:
            if filepath.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                df = pd.read_csv(filepath)
            
            if target_col in df.columns:
                ids = df[target_col].dropna().astype(str).str.strip().str.upper()
                ids = ids[ids != ""].unique()
                
                temp_df = pd.DataFrame({
                    'Target ID': ids,
                    'Filename': filename,
                    'Present': 1
                })
                all_data.append(temp_df)
                processed_files.append(filename)
        except Exception as e:
            st.warning(f"Error processing {filename}: {e}")

    if not all_data:
        return pd.DataFrame(), []

    combined_df = pd.concat(all_data, ignore_index=True)
    matrix = combined_df.pivot_table(index='Target ID', columns='Filename', values='Present', aggfunc='max').fillna(0).astype(int)
    
    return matrix, processed_files

def filter_matrix(matrix: pd.DataFrame, min_occurrence: int) -> pd.DataFrame:
    """
    Filters the matrix to only include Target IDs that appear in at least min_occurrence files.
    """
    if matrix.empty:
        return matrix
    
    occurrence_counts = matrix.sum(axis=1)
    filtered_ids = occurrence_counts[occurrence_counts >= min_occurrence].index
    return matrix.loc[filtered_ids]
