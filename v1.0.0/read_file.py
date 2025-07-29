import os
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Union

def read_fac_file_smart(file_path, force_method=None):
    """
    Smart .fac file reader that automatically chooses the optimal method
    based on file size for best performance
    
    - Files < 150 rows: Uses manual method (10-18x faster)
    - Files >= 150 rows: Uses pandas method (optimal for large files)
    
    Args:
        file_path (str): Path to the .fac file
        force_method (str): Force specific method ('pandas' or 'manual')
        
    Returns:
        list: List of numpy arrays, where each array represents a row
    """

    def count_data_rows(file_path):
        """Quick count of data rows without loading full file"""
        try:
            with open(file_path, 'r') as f:
                total_lines = sum(1 for _ in f)
            return max(0, total_lines - 11)
        except:
            return 0
    
    def read_fac_manual(file_path):
        """Manual method - optimal for small files (< 150 rows)"""
        try:
            result = []
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            filtered_lines = lines[1:-10]
            
            for line in filtered_lines:
                row_data = line.strip().split()[1:]
                try:
                    row_array = np.array([float(x) for x in row_data])
                except ValueError:
                    row_array = np.array(row_data)
                result.append(row_array)
            
            return result
        except Exception:
            return None
    
    def read_fac_pandas(file_path):
        """Pandas method - optimal for large files (>= 150 rows)"""
        try:
            df = pd.read_csv(file_path, sep=r'\s+', skiprows=1, header=None)
            filtered_df = df.iloc[:-10, 1:]
            numpy_array = filtered_df.to_numpy()
            
            try:
                numpy_array = numpy_array.astype(float)
            except ValueError:
                pass
            
            result = [row for row in numpy_array]
            return result
        except Exception:
            return None
    
    if force_method == 'pandas':
        return read_fac_pandas(file_path)
    elif force_method == 'manual':
        return read_fac_manual(file_path)
    else:
        data_rows = count_data_rows(file_path)
        
        if data_rows < 150:
            return read_fac_manual(file_path)
        else:
            return read_fac_pandas(file_path)


def read_fac_files(path: Union[str, Path]) -> Dict[str, List]:
    """
    Read .fac files from a file or folder (including subfolders recursively).
    
    Args:
        path (str or Path): Path to a .fac file or folder containing .fac files
        
    Returns:
        dict: Dictionary where keys are file paths and values are the data from each .fac file
    """
    path = Path(path)
    results = {}
    
    if not path.exists():
        return results
    
    if path.is_file():
        if path.suffix.lower() == '.fac':
            data = read_fac_file_smart(str(path))
            if data is not None:
                results[str(path)] = data
    
    elif path.is_dir():
        fac_files = list(path.rglob('*.fac'))
        
        for fac_file in fac_files:
            try:
                data = read_fac_file_smart(str(fac_file))
                if data is not None:
                    results[str(fac_file)] = data
            except Exception:
                pass
    
    return results


def print_fac_summary(data_dict: Dict[str, List]) -> None:
    """
    Print a summary of the loaded .fac files data.
    
    Args:
        data_dict: Dictionary returned by read_fac_files()
    """
    if not data_dict:
        print("No data loaded")
        return
    
    print(f"\n=== FAC Files Summary ===")
    print(f"Total files loaded: {len(data_dict)}")
    print(data_dict)
    
    for file_path, file_data in data_dict.items():
        Add_Channel(file_data, file_path)
        # print(f"\nFile: {Path(file_path).name}")
        # print(f"  Path: {file_path}")
        # print(f"  Rows: {len(file_data)}")
        # if file_data:
        #     print(f"  Columns: {len(file_data[0])}")
        #     print(f"  First row sample: {file_data[0][:5]}...")
        # else:
        #     print("  No data")




def Add_Channel(Data,data_address):
    print(f"Data from {data_address}:     {Data}")
    if not Data:
        print("No data to process")
        return
    
    # Get the first row (header) to find column positions
    header_row = Data[0]
    channel_address = None
    product_address = None

    for col_index, value in enumerate(header_row):
        if str(value).lower() == 'channel':
            channel_address = col_index
        elif str(value).lower() == 'product':
            product_address = col_index

    if channel_address is not None and product_address is not None:
        print(f"Found channel at column {channel_address}, product at column {product_address}")
    else:
        return
        print("Could not find both 'channel' and 'product' columns")

    # Create array with unique elements from product_address column onwards
    unique_products = []
    seen_products = set()
    
    for row in Data[1:]:  # Skip header row
        # Get the product value and all columns from product_address onwards
        product_row = row[product_address:]
        product_key = str(product_row[0])  # Use first element as key for uniqueness
        
        if product_key not in seen_products:
            seen_products.add(product_key)
            unique_products.append(product_row)

    

if __name__ == "__main__":
    folder_data = read_fac_files('subfolder')
    print_fac_summary(folder_data)