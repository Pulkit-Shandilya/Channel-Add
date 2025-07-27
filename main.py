import numpy as np
import pandas as pd
import time

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

def read_fac_file_pandas(file_path):
    """
    Read a .fac file using pandas - FASTEST for large files
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
        # Read the file with pandas, skipping the first row (header)
        df = pd.read_csv(file_path, sep=r'\s+', skiprows=1, header=None)
        
        # Remove last 10 rows and first column
        filtered_df = df.iloc[:-10, 1:]  # [rows, columns]
        
        # Convert each row to numpy array and store in list
        result = [row.to_numpy() for _, row in filtered_df.iterrows()]
        
        return result
        
    except Exception as e:
        print(f"Error reading file with pandas: {e}")
        return None

def read_fac_file_pandas_optimized(file_path):
    """
    Ultra-optimized pandas version - converts entire dataframe at once
    """
    try:
        # Read the file with pandas
        df = pd.read_csv(file_path, sep=r'\s+', skiprows=1, header=None)
        
        # Remove last 10 rows and first column
        filtered_df = df.iloc[:-10, 1:]
        
        # Convert to numpy array and then to list of rows (most efficient)
        numpy_array = filtered_df.to_numpy()
        result = [row for row in numpy_array]
        
        return result
        
    except Exception as e:
        print(f"Error reading file with optimized pandas: {e}")
        return None

def benchmark_methods(file_path, num_runs=3):
    """Compare performance of different reading methods"""
    print(f"\n{'='*80}")
    print(f"PERFORMANCE BENCHMARK - {file_path}")
    print(f"{'='*80}")
    
    methods = [
        ("Current Method (line-by-line)", read_fac_file),
        ("Pandas Method (row iteration)", read_fac_file_pandas),
        ("Pandas Optimized (vectorized)", read_fac_file_pandas_optimized)
    ]
    
    results = {}
    
    for method_name, method_func in methods:
        print(f"\nTesting: {method_name}")
        times = []
        data = None
        
        for run in range(num_runs):
            start_time = time.time()
            data = method_func(file_path)
            end_time = time.time()
            
            if data is not None:
                times.append(end_time - start_time)
                print(f"  Run {run+1}: {times[-1]:.4f} seconds")
            else:
                print(f"  Run {run+1}: FAILED")
                break
        
        if times:
            avg_time = sum(times) / len(times)
            results[method_name] = {
                'avg_time': avg_time,
                'data_rows': len(data) if data else 0,
                'data_cols': len(data[0]) if data and len(data) > 0 else 0
            }
            print(f"  Average: {avg_time:.4f} seconds")
            print(f"  Rows processed: {len(data)}")
        
    # Summary
    print(f"\n{'='*80}")
    print("PERFORMANCE SUMMARY")
    print(f"{'='*80}")
    
    if results:
        fastest = min(results.items(), key=lambda x: x[1]['avg_time'])
        print(f"🏆 FASTEST: {fastest[0]} - {fastest[1]['avg_time']:.4f} seconds")
        
        print("\nSpeed comparison:")
        baseline_time = fastest[1]['avg_time']
        for method, stats in results.items():
            speedup = stats['avg_time'] / baseline_time
            print(f"  {method}: {stats['avg_time']:.4f}s ({speedup:.1f}x slower than fastest)")
    
    return results

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
    # Test with small file first
    print("="*60)
    print("TESTING WITH SMALL FILE (sample.fac)")
    print("="*60)
    
    small_file = "sample.fac"
    data = read_fac_file_pandas_optimized(small_file)
    print_data_info(data, "Pandas optimized method")
    
    # Performance benchmark with large file
    large_file = "large_sample.fac"
    try:
        # Check if large file exists
        with open(large_file, 'r') as f:
            pass
        
        # Run performance benchmark
        benchmark_results = benchmark_methods(large_file, num_runs=3)
        
        # Show recommendations
        print(f"\n{'='*80}")
        print("RECOMMENDATIONS FOR LARGE .FAC FILES")
        print(f"{'='*80}")
        print("✅ Use the pandas optimized method for best performance")
        print("✅ Pandas is typically 5-10x faster for files with 1000+ rows")
        print("✅ Memory usage is also more efficient with pandas")
        print("✅ Built-in data type inference and error handling")
        
    except FileNotFoundError:
        print(f"\nLarge test file '{large_file}' not found.")
        print("Run 'python create_large_fac.py' first to create a test file.")
        
    # Show how to use the recommended method
    print(f"\n{'='*60}")
    print("RECOMMENDED USAGE FOR YOUR .FAC FILES:")
    print(f"{'='*60}")
    print("# For best performance with large .fac files:")
    print("data = read_fac_file_pandas_optimized('your_file.fac')")
    print("# Each row is a numpy array: data[0], data[1], etc.")
    print("# Access elements: data[row_index][column_index]")