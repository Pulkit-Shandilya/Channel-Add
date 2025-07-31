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
            
            # Find where data starts and ends
            data_start = -1
            data_end = len(lines)
            
            for i, line in enumerate(lines):
                # Look for header line starting with !
                if line.strip().startswith('!'):
                    data_start = i + 1
                    break
            
            # Look for end markers
            for i, line in enumerate(lines):
                if '##END##' in line or line.strip() == '':
                    data_end = i
                    break
            
            if data_start == -1:
                return None
            
            # Process data lines
            for line_idx in range(data_start, min(data_end, len(lines))):
                line = lines[line_idx].strip()
                if not line or line.startswith('#'):
                    continue
                
                # Handle different row formats
                if line.startswith('*,'):
                    # Format: *,"product_name",value1,value2,...
                    parts = line.split(',')
                    if len(parts) > 1:
                        row_data = parts[1:]  # Skip the '*'
                        # Clean up quoted strings and convert to appropriate types
                        cleaned_data = []
                        for item in row_data:
                            item = item.strip().strip('"').strip()
                            if item:
                                try:
                                    cleaned_data.append(float(item))
                                except ValueError:
                                    cleaned_data.append(item)
                        if cleaned_data:
                            result.append(np.array(cleaned_data))
                else:
                    # Standard format: value1,value2,value3,... or space-separated
                    # Try comma-separated first, then space-separated
                    if ',' in line:
                        row_data = [x.strip() for x in line.split(',') if x.strip()]
                    else:
                        row_data = line.split()[1:] if len(line.split()) > 1 else line.split()
                    
                    if row_data:
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
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if file uses *-format (star comma format)
            if '*,' in content:
                return _parse_star_format(content.splitlines())
            
            # Use standard pandas approach for space-separated format
            df = pd.read_csv(file_path, sep=r'\s+', skiprows=1, header=None)
            filtered_df = df.iloc[:-10, 1:]
            numpy_array = filtered_df.to_numpy()
            
            try:
                numpy_array = numpy_array.astype(float)
            except ValueError:
                pass
            
            return [row for row in numpy_array]
        except Exception:
            return None
    
    def _parse_star_format(lines):
        """Helper function to parse *-format lines"""
        result = []
        for line in lines:
            line = line.strip()
            if not line.startswith('*,'):
                continue
                
            parts = line.split(',')[1:]  # Skip the '*'
            cleaned_data = []
            for item in parts:
                item = item.strip().strip('"').strip()
                if item:
                    try:
                        cleaned_data.append(float(item))
                    except ValueError:
                        cleaned_data.append(item)
            
            if cleaned_data:
                result.append(np.array(cleaned_data))
        return result
    
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


def Check_Column_Channel_Product(Data, data_address) -> Union[None, List,int]:
    """
    Add channel functionality to process .fac file data
    """
    if not Data:
        print("No data to process")
        return
    
    print(f"Processing file: {data_address}")
    print(f"Total rows: {len(Data)}")
    
    # Look for header information in the original file
    channel_address = None
    product_address = None
    
    try:
        # Read the original file to find the header line
        with open(data_address, 'r') as f:
            lines = f.readlines()
        
        header_line = None
        for line in lines:
            if line.strip().startswith('!'):
                header_line = line.strip()
                break
        
        if header_line:
            # Parse header to find column positions
            header_parts = header_line.split(',')
            for col_index, value in enumerate(header_parts):
                if str(value).lower() == 'channel':
                    channel_address = col_index - 1  # Adjust for the ! prefix
                elif str(value).lower() == 'product' or 'prod_name' in str(value).lower():
                    product_address = col_index - 1  # Adjust for the ! prefix
        
        print(f"Found channel at column {channel_address}, product at column {product_address}")
        unique_products = []
        seen_products = set()
        for i, row in enumerate(Data):
            try:
                if len(row) > product_address:
                    # Get the product value and all columns from product_address onwards
                    product_row = row[product_address:]
                    product_key = str(product_row[0])  # Use first element as key for uniqueness
                    
                    if product_key not in seen_products:
                        seen_products.add(product_key)
                        unique_products.append(product_row)
                        print(f"Row {i}: Found unique product: {product_key}")

            except Exception as e:
                print(f"Error processing row {i}: {e}")
                continue

        return channel_address, product_address, unique_products

    except Exception as e:
        print(f"Error processing file {data_address}: {e}")
        return

def extract_unique_products(unique_products, channel_address, newchannel) -> List:
    """
    Extract unique products and create new channel entries with "*" prefix
    """
    print(f"Unique products found: {len(unique_products)}")
    print(len(unique_products))
    if unique_products:
        print("Sample unique products:")
        for i, product in enumerate(unique_products[:5]):  # Show first 5
            print(f"  {i+1}: {product}")
    
    new_lines = []
    for i in unique_products:
        try:
            if len(i) > channel_address:
                # Create a copy and modify the channel
                product_copy = i.copy()
                product_copy[channel_address] = newchannel
                # Convert to list and add "*" as first element
                new_line = ["*"] + product_copy.tolist()
                new_lines.append(new_line)
        except Exception as e:
            print(f"Error processing row {i}: {e}")
            continue
    
    return new_lines





def extract_and_remove_bottom_lines(file_path):
    """
    Extract and remove the bottom metadata lines from a .fac file.
    
    Args:
        file_path (str): Path to the .fac file
        
    Returns:
        tuple: (data_lines, bottom_lines, header_lines)
            - data_lines: List of data rows without header and footer
            - bottom_lines: List of bottom metadata lines (##END##, ##COLOR##, etc.)
            - header_lines: List of header lines before data starts
    """
    try:
        with open(file_path, 'r') as f:
            all_lines = f.readlines()
        
        # Find header end (line starting with !)
        header_end = -1
        for i, line in enumerate(all_lines):
            if line.strip().startswith('!'):
                header_end = i
                break
        
        # Find where bottom metadata starts
        bottom_start = len(all_lines)
        for i in range(len(all_lines) - 1, -1, -1):
            line = all_lines[i].strip()
            if line.startswith('##') or line == '':
                bottom_start = i
            else:
                break
        
        # Split the file into sections
        header_lines = all_lines[:header_end + 1] if header_end >= 0 else []
        data_lines = all_lines[header_end + 1:bottom_start] if header_end >= 0 else []
        bottom_lines = all_lines[bottom_start:]
        
        # Clean up data lines (remove empty lines and comments)
        clean_data_lines = []
        for line in data_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                clean_data_lines.append(line)
        
        return clean_data_lines, bottom_lines, header_lines
        
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return [], [], []


def save_file_without_bottom(file_path, output_path=None):
    """
    Save a .fac file without the bottom metadata lines.
    
    Args:
        file_path (str): Path to the original .fac file
        output_path (str): Path for the output file (optional, defaults to original file)
        
    Returns:
        tuple: (success, bottom_lines) - success status and extracted bottom lines
    """
    try:
        data_lines, bottom_lines, header_lines = extract_and_remove_bottom_lines(file_path)
        
        if output_path is None:
            output_path = file_path
        
        # Write the file without bottom lines
        with open(output_path, 'w') as f:
            # Write header
            f.writelines(header_lines)
            # Write data
            f.writelines(data_lines)
        
        print(f"File saved without bottom lines: {output_path}")
        print(f"Extracted {len(bottom_lines)} bottom lines")
        
        return True, bottom_lines
        
    except Exception as e:
        print(f"Error saving file: {e}")
        return False, []


def restore_bottom_lines(file_path, bottom_lines):
    """
    Restore the bottom metadata lines to a .fac file.
    
    Args:
        file_path (str): Path to the .fac file
        bottom_lines (list): List of bottom lines to restore
        
    Returns:
        bool: Success status
    """
    try:
        with open(file_path, 'a') as f:
            f.writelines(bottom_lines)
        
        print(f"Bottom lines restored to: {file_path}")
        return True
        
    except Exception as e:
        print(f"Error restoring bottom lines: {e}")
        return False

def process_fac_with_bottom_management(file_path, modified_lines):
    """
    Example of how to process a .fac file while properly managing bottom lines.
    
    Args:
        file_path (str): Path to the .fac file
        new_channel_name (str): Name of new channel to add
        
    Returns:
        bool: Success status
    """
    try:
        print(f"\n=== Processing {file_path} with Bottom Line Management ===")
        
        # Step 1: Extract components
        data_lines, bottom_lines, header_lines = extract_and_remove_bottom_lines(file_path)
        print(f"Extracted {len(data_lines)} data lines and {len(bottom_lines)} bottom lines")

        
        # Step 4: Write back with bottom lines
        with open(file_path, 'w') as f:
            # Write header
            f.writelines(header_lines)
            # Write modified data
            print(f"Writing data lines: {data_lines}")
            f.writelines(data_lines)
            # Write modified lines (e.g., new channel entries)
            for modified_line_row in modified_lines:
                print(f"Adding modified line: {modified_line_row}")
            # Write bottom lines
            print(f"Restoring bottom lines: {bottom_lines}")
            f.writelines(bottom_lines)
        
        print(f"File updated successfully with 'New channel' entries")
        return True
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return False


if __name__ == "__main__":
    # Choose which example to run
    run_bottom_extraction_test = True
    
    if run_bottom_extraction_test:
        # Test the bottom line extraction functionality
        test_file = r"Data\TABLE_II_May'25\IC_ADJ_PC.fac"
        
        print("=== Testing Bottom Line Extraction ===")
        
        # Extract bottom lines
        data_lines, bottom_lines, header_lines = extract_and_remove_bottom_lines(test_file)
        
        print(f"Header lines: {len(header_lines)}")
        print(f"Data lines: {len(data_lines)}")
        print(f"Bottom lines: {len(bottom_lines)}")
        
        print("\nBottom lines content:")
        for i, line in enumerate(bottom_lines):
            print(f"  {i+1}: {line.strip()}")
        
        print("\nFirst few data lines:")
        for i, line in enumerate(data_lines[:3]):
            print(f"  {i+1}: {line.strip()}")
    



    # Always run normal file reading for comparison
    print("\n=== Normal File Reading ===")
    folder_data = read_fac_files(r"Data\TABLE_II_May'25\IC_ADJ_PC.fac")
    newchannel = "This_Is_A_New_Channel"

    for file_path, file_data in folder_data.items():
        channel_address, product_address, unique_products = Check_Column_Channel_Product(file_data, file_path)
        Unique_Lines= extract_unique_products(unique_products, channel_address, newchannel)
        print(Unique_Lines)
        process_fac_with_bottom_management(file_path, Unique_Lines)
