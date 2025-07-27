import numpy as np
import pandas as pd

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
            return max(0, total_lines - 11)  # minus header and 10 footer rows
        except:
            return 0
    
    def read_fac_manual(file_path):
        """Manual method - optimal for small files (< 150 rows)"""
        try:
            result = []
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            filtered_lines = lines[1:-10]  # Skip first row and last 10 rows
            
            for line in filtered_lines:
                row_data = line.strip().split()[1:]  # Skip first column
                try:
                    row_array = np.array([float(x) for x in row_data])
                except ValueError:
                    row_array = np.array(row_data)
                result.append(row_array)
            
            return result
        except Exception as e:
            print(f"Error with manual method: {e}")
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
        except Exception as e:
            print(f"Error with pandas method: {e}")
            return None
    
    # Choose method based on file size or force specific method
    if force_method == 'pandas':
        return read_fac_pandas(file_path)
    elif force_method == 'manual':
        return read_fac_manual(file_path)
    else:
        # Auto-detect best method
        data_rows = count_data_rows(file_path)
        
        if data_rows < 150:
            return read_fac_manual(file_path)
        else:
            return read_fac_pandas(file_path)

# Usage examples
if __name__ == "__main__":
    # Automatic method selection (recommended)
    data = read_fac_file_smart('your_file.fac')
    
    # Force specific method if needed
    # data = read_fac_file_smart('file.fac', force_method='manual')
    # data = read_fac_file_smart('file.fac', force_method='pandas')
    
    if data:
        print(f"Loaded {len(data)} rows with {len(data[0])} columns each")
        print(f"First row: {data[0]}")
    else:
        print("Failed to load file")
