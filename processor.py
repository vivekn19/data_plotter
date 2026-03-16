import pandas as pd
import os
import streamlit as st
from typing import List, Tuple

@st.cache_data
def load_and_process_files(directory_path: str, target_col: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    Iterates through Excel and CSV files in a directory, extracts Target IDs,
    cleans them, and returns a Binary Occurrence Matrix.
    """
    if not os.path.exists(directory_path):
        return pd.DataFrame(), []

    all_data = []
    processed_files = []

    # Supported extensions
    valid_extensions = ('.xlsx', '.xls', '.csv')

    files = [f for f in os.listdir(directory_path) if f.lower().endswith(valid_extensions)]
    
    for filename in files:
        filepath = os.path.join(directory_path, filename)
        try:
            if filename.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                df = pd.read_csv(filepath)
            
            if target_col in df.columns:
                # Extract and clean Target IDs
                ids = df[target_col].dropna().astype(str).str.strip().str.upper()
                ids = ids[ids != ""].unique()
                
                # Store as temporary dataframe for merging
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

    # Vectorized transformation to Binary Occurrence Matrix
    # We concatenate all and then pivot
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
