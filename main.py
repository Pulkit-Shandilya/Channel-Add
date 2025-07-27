import numpy as np
import pandas as pd

def read_fac_file(file_path):
    """
    Read .fac file with filtering:
    - Skip first row (header)
    - Skip last 10 rows  
    - Skip first column
    - Return each row as numpy array in a list
    
    Automatically chooses optimal method based on file size.
    """
    
    def count_rows(file_path):
        """Count data rows in file"""
        try:
            with open(file_path, 'r') as f:
                total_lines = sum(1 for _ in f)
            return max(0, total_lines - 11)  # minus header and footer
        except:
            return 0
    
    def read_manual(file_path):
        """Manual method - fast for small files"""
        result = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        for line in lines[1:-10]:  # Skip first and last 10 rows
            row_data = line.strip().split()[1:]  # Skip first column
            try:
                row_array = np.array([float(x) for x in row_data])
            except ValueError:
                row_array = np.array(row_data)
            result.append(row_array)
        
        return result
    
    def read_pandas(file_path):
        """Pandas method - fast for large files"""
        df = pd.read_csv(file_path, sep=r'\s+', skiprows=1, header=None)
        filtered_df = df.iloc[:-10, 1:]  # Remove last 10 rows and first column
        numpy_array = filtered_df.to_numpy()
        
        try:
            numpy_array = numpy_array.astype(float)
        except ValueError:
            pass
        
        return [row for row in numpy_array]
    
    # Choose method based on file size
    data_rows = count_rows(file_path)
    
    try:
        if data_rows < 150:
            return read_manual(file_path)
        else:
            return read_pandas(file_path)
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# Usage
if __name__ == "__main__":
    data = read_fac_file("your_file.fac")
    
    if data:
        print(f"Loaded {len(data)} rows with {len(data[0])} columns each")
        print(f"First row: {data[0]}")
    else:
        print("Failed to load file")
