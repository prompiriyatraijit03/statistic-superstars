"""
Data loading and preprocessing utilities.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import requests
from typing import Optional, Tuple, List
import json


class DataLoader:
    """Handles data loading from various sources."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_from_url(self, url: str, filename: str) -> pd.DataFrame:
        """
        Download data from URL and load into DataFrame.
        
        Args:
            url: URL to download from
            filename: Name to save file as
            
        Returns:
            DataFrame with downloaded data
        """
        filepath = self.raw_dir / filename
        
        # Check if file already exists
        if not filepath.exists():
            print(f"Downloading data from {url}...")
            response = requests.get(url)
            response.raise_for_status()
            
            # Save file
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"Saved to {filepath}")
        
        # Load based on file extension
        if filename.endswith('.csv'):
            return pd.read_csv(filepath)
        elif filename.endswith('.xlsx'):
            return pd.read_excel(filepath)
        elif filename.endswith('.json'):
            return pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
    
    def load_local_data(self, filename: str) -> pd.DataFrame:
        """Load data from local processed directory."""
        filepath = self.processed_dir / filename
        return pd.read_csv(filepath)
    
    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """Save processed data to processed directory."""
        filepath = self.processed_dir / filename
        df.to_csv(filepath, index=False)
        print(f"Saved processed data to {filepath}")
    
    def get_dataset_info(self, df: pd.DataFrame) -> dict:
        """
        Generate comprehensive dataset information.
        
        Returns dict with:
        - shape: (rows, columns)
        - column_info: {col: {'dtype': type, 'null_count': int, 'unique': int}}
        - memory_usage: float (MB)
        - sample: first 5 rows
        """
        info = {
            'shape': df.shape,
            'column_info': {},
            'memory_usage': df.memory_usage(deep=True).sum() / 1e6,
            'sample': df.head(5).to_dict('records')
        }
        
        for col in df.columns:
            info['column_info'][col] = {
                'dtype': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'unique': df[col].nunique()
            }
        
        return info
    
    def create_data_dictionary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create a data dictionary for documentation.
        """
        dict_data = {
            'Column': [],
            'Type': [],
            'Description': [],
            'Missing (%)': [],
            'Unique Values': [],
            'Example Values': []
        }
        
        for col in df.columns:
            dict_data['Column'].append(col)
            dict_data['Type'].append(str(df[col].dtype))
            dict_data['Description'].append('')  # To be filled manually
            dict_data['Missing (%)'].append(
                f"{df[col].isnull().mean() * 100:.1f}%"
            )
            dict_data['Unique Values'].append(df[col].nunique())
            
            # Get sample values
            sample = df[col].dropna().head(3).tolist()
            dict_data['Example Values'].append(str(sample)[:50])
        
        return pd.DataFrame(dict_data)
