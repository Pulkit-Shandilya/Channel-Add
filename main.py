#!/usr/bin/env python3
"""
Channel Add - In-Place File Processing
Processes .fac files to add CHANNEL_TI rows for files with CHANNEL and PRODUCT columns.
"""

import pandas as pd
import os
from fac_reader import read_fac_file_complete, write_fac_file

def has_required_columns(filename):
    """Check if file has both CHANNEL and PRODUCT columns"""
    try:
        fac_data = read_fac_file_complete(filename)
        if not fac_data:
            return False
        
        df = fac_to_dataframe(fac_data)
        if df is None:
            return False
        
        has_channel = False
        has_product = False
        
        for col in df.columns:
            col_upper = str(col).upper()
            if 'CHANNEL' in col_upper:
                has_channel = True
            if ('PROD' in col_upper and 'NAME' in col_upper) or col_upper in ['PRODUCT', 'PROD_NAME', 'LOB_CODE']:
                has_product = True
        
        return has_channel and has_product
        
    except Exception:
        return False

def fac_to_dataframe(fac_data):
    """Convert .fac data to pandas DataFrame"""
    if not fac_data:
        return None
    
    headers, data_rows, footers = fac_data
    
    column_names = None
    for header in headers:
        if header.startswith('!') and ',' in header:
            column_names = [col.strip() for col in header[1:].split(',')]
            break
    
    if column_names is None:
        max_cols = max(len(row) for row in data_rows) if data_rows else 0
        column_names = [f'Column_{i}' for i in range(max_cols)]
    
    clean_data = []
    for row in data_rows:
        clean_row = row[1:] if len(row) > 0 and row[0] == '*' else row
        while len(clean_row) < len(column_names):
            clean_row.append('')
        clean_data.append(clean_row[:len(column_names)])
    
    df = pd.DataFrame(clean_data, columns=column_names)
    return df

def dataframe_to_fac(df, original_headers, original_footers):
    """Convert DataFrame back to .fac format"""
    headers = original_headers.copy()
    
    data_rows = []
    for _, row in df.iterrows():
        fac_row = ['*'] + row.tolist()
        data_rows.append(fac_row)
    
    footers = original_footers.copy()
    return headers, data_rows, footers

def add_channel_rows(filename, new_agent):
    """Add new channel rows to the file data"""
    try:
        if not has_required_columns(filename):
            return None
        
        fac_data = read_fac_file_complete(filename)
        if not fac_data:
            return None
        
        df = fac_to_dataframe(fac_data)
        if df is None:
            return None
        
        channel_col = None
        prod_name_col = None
        
        for i, col in enumerate(df.columns):
            col_upper = str(col).upper()
            if 'CHANNEL' in col_upper:
                channel_col = i
            if ('PROD' in col_upper and 'NAME' in col_upper) or col_upper in ['PRODUCT', 'PROD_NAME', 'LOB_CODE']:
                prod_name_col = i
        
        if channel_col is None or prod_name_col is None:
            return None
        
        processed_combinations = []
        
        for _, row in df.iterrows():
            prod_name = row.iloc[prod_name_col]
            row_values = [row.iloc[i] for i in range(len(row)) if i != channel_col]
            combination_key = (prod_name, tuple(row_values))
            
            if combination_key not in processed_combinations:
                processed_combinations.append(combination_key)
                new_row = row.copy()
                new_row.iloc[channel_col] = new_agent
                df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
        
        return df
        
    except Exception:
        return None

def process_single_file(input_file, new_agent):
    """Process a single .fac file in place"""
    try:
        if not has_required_columns(input_file):
            return None
        
        original_fac_data = read_fac_file_complete(input_file)
        if not original_fac_data:
            return False
        
        headers, _, footers = original_fac_data
        modified_df = add_channel_rows(input_file, new_agent)
        if modified_df is None:
            return False
        
        # Create backup
        backup_file = input_file + '.backup'
        if os.path.exists(input_file):
            os.rename(input_file, backup_file)
        
        try:
            new_headers, new_data_rows, new_footers = dataframe_to_fac(modified_df, headers, footers)
            write_fac_file(input_file, new_headers, new_data_rows, new_footers)
            
            if os.path.exists(input_file):
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                return True
            else:
                if os.path.exists(backup_file):
                    os.rename(backup_file, input_file)
                return False
                
        except Exception:
            if os.path.exists(backup_file):
                os.rename(backup_file, input_file)
            return False
            
    except Exception:
        return False

def process_files(input_path, new_agent):
    """Process files or folder in place"""
    try:
        results = {'successful': 0, 'failed': 0, 'skipped': 0}
        
        if input_path.endswith('.fac'):
            if os.path.exists(input_path):
                result = process_single_file(input_path, new_agent)
                if result is True:
                    results['successful'] += 1
                elif result is False:
                    results['failed'] += 1
                else:
                    results['skipped'] += 1
            else:
                results['failed'] += 1
        else:
            if not os.path.exists(input_path):
                return results
            
            fac_files = []
            for root, dirs, files in os.walk(input_path):
                for file in files:
                    if file.endswith('.fac'):
                        file_path = os.path.join(root, file)
                        fac_files.append(file_path)
            
            for file_path in fac_files:
                result = process_single_file(file_path, new_agent)
                if result is True:
                    results['successful'] += 1
                elif result is False:
                    results['failed'] += 1
                else:
                    results['skipped'] += 1
        
        return results
        
    except Exception:
        return {'successful': 0, 'failed': 1, 'skipped': 0}

def restore_backups(directory):
    """Restore all backup files in directory"""
    backup_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.backup'):
                backup_path = os.path.join(root, file)
                original_path = backup_path[:-7]
                backup_files.append((backup_path, original_path))
    
    if not backup_files:
        return False
    
    for backup_path, original_path in backup_files:
        try:
            if os.path.exists(original_path):
                os.remove(original_path)
            os.rename(backup_path, original_path)
        except Exception:
            continue
    
    return True

def cleanup_backups(directory):
    """Remove all backup files in directory"""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.backup'):
                try:
                    os.remove(os.path.join(root, file))
                except Exception:
                    continue

def main():
    """Main processing function"""
    print("=== Channel Add - .fac File Processor ===")
    
    # Ask for input path
    while True:
        input_path = input("\nEnter the path to folder or .fac file: ").strip()
        if input_path:
            # Remove quotes if user included them
            input_path = input_path.strip('"').strip("'")
            if os.path.exists(input_path):
                break
            else:
                print(f"Error: Path not found: {input_path}")
                print("Please enter a valid path to a folder or .fac file.")
        else:
            print("Please enter a path.")
    
    # Ask for agent name
    new_agent = input("\nEnter new agent name (default: CHANNEL_TI): ").strip()
    if not new_agent:
        new_agent = "CHANNEL_TI"
    
    # Count files that will be processed
    valid_files = 0
    total_files = 0
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if file.endswith('.fac'):
                total_files += 1
                file_path = os.path.join(root, file)
                if has_required_columns(file_path):
                    valid_files += 1
    
    print(f"Found {total_files} .fac files total")
    print(f"{valid_files} files will be processed")
    print(f"{total_files - valid_files} files will be skipped")
    
    if valid_files == 0:
        print("No files to process!")
        return
    
    # Confirm operation
    response = input(f"\nProceed to modify {valid_files} files? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("Operation cancelled.")
        return
    
    # Process files
    results = process_files(input_path, new_agent)
    
    print(f"\nResults:")
    print(f"  Successfully processed: {results['successful']} files")
    print(f"  Failed: {results['failed']} files")
    print(f"  Skipped: {results['skipped']} files")
    
    if results['successful'] > 0:
        print(f"\nSuccess! {results['successful']} files modified with {new_agent} rows.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Add CHANNEL_TI rows to .fac files')
    parser.add_argument('--path', help='Input path (optional - will prompt if not provided)')
    parser.add_argument('--agent', help='New agent value (optional - will prompt if not provided)')
    parser.add_argument('--restore', action='store_true', help='Restore from backups')
    parser.add_argument('--cleanup', action='store_true', help='Clean up backup files')
    
    args = parser.parse_args()
    
    if args.restore:
        # For restore, we need a path
        path = args.path
        if not path:
            path = input("Enter path to restore backups from: ").strip().strip('"').strip("'")
        
        if restore_backups(path):
            print("Backups restored successfully.")
        else:
            print("No backup files found.")
    elif args.cleanup:
        # For cleanup, we need a path
        path = args.path
        if not path:
            path = input("Enter path to clean backups from: ").strip().strip('"').strip("'")
        
        cleanup_backups(path)
        print("Backup files cleaned up.")
    else:
        # If path and agent are provided via command line, use them directly
        if args.path and args.agent:
            input_path = args.path.strip('"').strip("'")
            new_agent = args.agent
            
            if not os.path.exists(input_path):
                print(f"Error: Input path not found: {input_path}")
                exit(1)
            
            print("=== Channel Add - .fac File Processor ===")
            print(f"Input path: {input_path}")
            print(f"Agent: {new_agent}")
            
            # Count files and process
            valid_files = 0
            total_files = 0
            
            if input_path.endswith('.fac'):
                total_files = 1
                if has_required_columns(input_path):
                    valid_files = 1
            else:
                for root, dirs, files in os.walk(input_path):
                    for file in files:
                        if file.endswith('.fac'):
                            total_files += 1
                            file_path = os.path.join(root, file)
                            if has_required_columns(file_path):
                                valid_files += 1
            
            print(f"\nFound {total_files} .fac files total")
            print(f"{valid_files} files will be processed")
            print(f"{total_files - valid_files} files will be skipped")
            
            if valid_files == 0:
                print("No files to process!")
                exit(0)
            
            response = input(f"\nProceed to modify {valid_files} files? (yes/no): ").lower().strip()
            if response not in ['yes', 'y']:
                print("Operation cancelled.")
                exit(0)
            
            results = process_files(input_path, new_agent)
            
            print(f"\nResults:")
            print(f"  Successfully processed: {results['successful']} files")
            print(f"  Failed: {results['failed']} files")
            print(f"  Skipped: {results['skipped']} files")
            
            if results['successful'] > 0:
                print(f"\nSuccess! {results['successful']} files modified with {new_agent} rows.")
        else:
            # Interactive mode
            main()
