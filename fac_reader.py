import numpy as np
import pandas as pd

def read_fac_file(file_path, force_method=None):
    """
    Read .fac file with filtering:
    - Skip first row (header)
    - Skip last 10 rows
    - Skip first column
    - Return each row as numpy array in a list
    
    Automatically chooses optimal method based on file size.
    Files < 150 rows: Uses manual method (faster)
    Files >= 150 rows: Uses pandas method (better scalability)
    """
    
    def count_data_rows(file_path):
        """Quick count of data rows without loading full file"""
        try:
            count = 0
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip().startswith('*,'):
                        count += 1
            return count
        except:
            return 0
    
    def read_fac_manual(file_path):
        """Manual method - optimal for small files (< 150 rows)"""
        try:
            result = []
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Find data lines (start with '*')
            data_lines = []
            for line in lines:
                line = line.strip()
                if line.startswith('*,'):
                    data_lines.append(line)
            
            for line in data_lines:
                # Split by comma and skip first column (which is '*')
                row_data = line.split(',')[1:]  # Skip first column ('*')
                try:
                    # Try to convert numeric columns to float
                    row_array = []
                    for item in row_data:
                        try:
                            row_array.append(float(item))
                        except ValueError:
                            row_array.append(item)  # Keep as string if not numeric
                    row_array = np.array(row_array)
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
            # Read all lines first to filter for data rows
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Filter lines that start with '*,'
            data_lines = []
            for line in lines:
                line = line.strip()
                if line.startswith('*,'):
                    data_lines.append(line)
            
            # Create a temporary string with just the data lines
            data_content = '\n'.join(data_lines)
            
            # Read with pandas, treating comma as separator
            from io import StringIO
            df = pd.read_csv(StringIO(data_content), sep=',', header=None)
            
            # Skip first column (which contains '*')
            filtered_df = df.iloc[:, 1:]
            numpy_array = filtered_df.to_numpy()
            
            # Try to convert numeric columns to float where possible
            result = []
            for row in numpy_array:
                converted_row = []
                for item in row:
                    try:
                        converted_row.append(float(item))
                    except (ValueError, TypeError):
                        converted_row.append(item)
                result.append(np.array(converted_row))
            
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


def Channel_add(data):
    """Legacy function - basic data processing"""
    if not data or len(data) == 0:
        print("No data to process")
        return []
    
    # Get unique values while preserving order
    seen = set()
    unique_rows = []
    for row in data:
        if len(row) > 2:
            value = row[2]
            if value not in seen:
                seen.add(value)
                unique_rows.append(row)
    
    return unique_rows


def add_unique_channel_combinations(file_path, output_path, new_channel_name):
    """
    Add a new channel to create unique channel-product combinations.
    Each parameter will have one entry per channel-product combination.
    
    Parameters:
    file_path (str): Path to the input .fac file
    output_path (str): Path to save the output .fac file
    new_channel_name (str): Name of the new channel to add
    """
    try:
        # Read the .fac file data
        fac_data = read_fac_file_complete(file_path)
        
        if fac_data is None:
            print(f"Error: Could not read the file {file_path}")
            return
        
        # Extract the data arrays from the tuple
        headers, data_rows, footers = fac_data
        
        print(f"Original file has {len(data_rows)} data rows")
        
        # Group data by parameter (column 0)
        param_groups = {}
        for row in data_rows:
            if len(row) > 1:
                param = row[0]
                if param not in param_groups:
                    param_groups[param] = []
                param_groups[param].append(row)
        
        print(f"Found {len(param_groups)} unique parameters: {list(param_groups.keys())}")
        
        # Get unique products from all rows
        all_products = set()
        for row in data_rows:
            if len(row) > 1:
                all_products.add(row[1])
        
        print(f"Found {len(all_products)} unique products: {all_products}")
        
        # Create new data structure with unique channel-product combinations
        new_data_rows = []
        
        for param, param_rows in param_groups.items():
            # Keep original rows (existing channel-product combinations)
            for row in param_rows:
                new_data_rows.append(row)
            
            # Add one row for the new channel (using data from first product of this parameter)
            if param_rows:
                template_row = param_rows[0].copy()  # Use first row as template
                template_row[1] = new_channel_name  # Replace product with new channel name
                new_data_rows.append(template_row)
        
        print(f"Total rows after adding unique channel combinations: {len(new_data_rows)}")
        
        # Write to output file
        write_fac_file(output_path, headers, new_data_rows, footers)
        print(f"Successfully wrote output to {output_path}")
        
        # Show summary
        print("\nSummary of channel-product combinations:")
        param_channel_count = {}
        for row in new_data_rows:
            if len(row) > 1:
                param = row[0]
                channel = row[1]
                if param not in param_channel_count:
                    param_channel_count[param] = set()
                param_channel_count[param].add(channel)
        
        for param, channels in param_channel_count.items():
            print(f"  {param}: {len(channels)} channels ({', '.join(sorted(channels))})")
        
    except Exception as e:
        print(f"Error in add_unique_channel_combinations: {e}")


def write_fac_file(output_path, headers, data_rows, footers):
    """
    Write data to a .fac file with proper formatting.
    
    Parameters:
    output_path (str): Path to save the output file
    headers (list): Header lines starting with !
    data_rows (list): Data rows starting with *
    footers (list): Footer lines starting with ##
    """
    try:
        with open(output_path, 'w') as file:
            # Write headers
            for header in headers:
                file.write(header + '\n')
            
            # Write data rows
            for row in data_rows:
                # Convert all elements to strings and join with commas
                row_str = ','.join(str(item) for item in row)
                file.write(row_str + '\n')
            
            # Write footers
            for footer in footers:
                file.write(footer + '\n')
                
        print(f"File written successfully to {output_path}")
        
    except Exception as e:
        print(f"Error writing file: {e}")

def read_fac_file_complete(file_path):
    """
    Read a .fac file and return headers, data rows, and footers
    
    Parameters:
    file_path (str): Path to the .fac file
    
    Returns:
    tuple: (headers, data_rows, footers) where:
    - headers: list of header lines (starting with !)
    - data_rows: list of data rows (starting with *)
    - footers: list of footer lines (starting with ##)
    """
    try:
        headers = []
        data_rows = []
        footers = []
        
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith('!'):
                headers.append(line)
            elif line.startswith('*,'):
                # Parse data row
                row_data = line.split(',')
                data_rows.append(row_data)
            elif line.startswith('##'):
                footers.append(line)
            elif line and not line.startswith('*') and not line.startswith('!') and not line.startswith('##'):
                # Handle first line (count) or other format lines
                if len(headers) == 0 and len(data_rows) == 0:
                    headers.append(line)  # Include count line as first header
        
        print(f"Read {len(headers)} headers, {len(data_rows)} data rows, {len(footers)} footers")
        return headers, data_rows, footers
        
    except Exception as e:
        print(f"Error reading .fac file {file_path}: {e}")
        return None


# Usage examples
if __name__ == "__main__":
    # Automatic method selection (recommended)
    data = read_fac_file(r"Data\TABLE_II_May'25\INFLATION_RATE_TABLE.fac")
    print(data)
    # print(Channel_add(data))

    # Force specific method if needed
    # data = read_fac_file('file.fac', force_method='manual')
    # data = read_fac_file('file.fac', force_method='pandas')
    
    # if data:
    #     print(f"Loaded {len(data)} rows with {len(data[0])} columns each")
    #     print(f"First row: {data[0]}")
    # else:
    #     print("Failed to load file")
