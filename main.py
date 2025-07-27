import numpy as np

def read_fac_file(file_path):
    """
    Read a .fac file and return data with specified filtering:
    - Skip first row
    - Skip last 10 rows
    - Skip first column
    - Store each row as an individual array inside a main array
    
    Args:
        file_path (str): Path to the .fac file
        
    Returns:
        list: List of numpy arrays, where each array represents a row
    """
    try:
        # First, try to read as numeric data (skip header row)
        try:
            data = np.loadtxt(file_path, delimiter=None, skiprows=1)
            # Apply filtering: skip last 10 rows and first column
            filtered_data = data[:-10, 1:]  # [start_row:end_row, start_col:end_col]
            # Convert to list of arrays (each row as an individual array)
            result = [row for row in filtered_data]
            return result
        except ValueError:
            # If numeric loading fails, use the alternative method
            return read_fac_file_mixed_data(file_path)
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def read_fac_file_mixed_data(file_path):
    """
    Alternative method for files with mixed data types or headers
    """
    try:
        result = []
        
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Remove first row and last 10 rows
        filtered_lines = lines[1:-10]
        
        for line in filtered_lines:
            # Split the line and remove first column
            row_data = line.strip().split()[1:]  # Skip first column
            
            # Convert to numpy array, trying numeric first
            try:
                row_array = np.array([float(x) for x in row_data])
            except ValueError:
                # If conversion fails, keep as string array
                row_array = np.array(row_data)
            
            result.append(row_array)
        
        return result
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def print_data_info(data, method_name):
    """Helper function to print information about the loaded data"""
    if data is not None:
        print(f"✅ {method_name} successful!")
        print(f"   Number of rows: {len(data)}")
        if len(data) > 0:
            print(f"   Columns per row: {len(data[0])}")
            print(f"   Data type: {data[0].dtype}")
            print(f"   Sample data (first 3 rows):")
            for i, row in enumerate(data[:3]):
                print(f"   Row {i}: {row}")
        print()
    else:
        print(f"❌ {method_name} failed!")
        print()

# Example usage
if __name__ == "__main__":
    # Replace 'your_file.fac' with the actual path to your .fac file
    file_path = "sample.fac"
    
    print("="*60)
    print("FAC FILE READER - Processing:", file_path)
    print("="*60)
    print("Filters applied:")
    print("- Skip first row