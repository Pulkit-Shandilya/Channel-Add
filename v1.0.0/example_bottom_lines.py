"""
Example: How to remove and restore bottom lines from .fac files

This example demonstrates:
1. How to extract bottom metadata lines
2. How to work with the file without bottom lines
3. How to restore the bottom lines later
"""

from read_file import extract_and_remove_bottom_lines, save_file_without_bottom, restore_bottom_lines
import shutil

def example_workflow():
    """
    Example workflow showing how to handle bottom lines in .fac files
    """
    
    # Original file path
    original_file = r"../Data/TABLE_II_May'25/IC_ADJ_PC.fac"
    backup_file = "IC_ADJ_PC_backup.fac"
    temp_file = "IC_ADJ_PC_temp.fac"
    
    print("=== .fac File Bottom Lines Management Example ===\n")
    
    # Step 1: Create a backup
    print("1. Creating backup...")
    shutil.copy2(original_file, backup_file)
    print(f"   Backup created: {backup_file}")
    
    # Step 2: Extract bottom lines
    print("\n2. Extracting bottom lines...")
    data_lines, bottom_lines, header_lines = extract_and_remove_bottom_lines(backup_file)
    
    print(f"   Found {len(header_lines)} header lines")
    print(f"   Found {len(data_lines)} data lines") 
    print(f"   Found {len(bottom_lines)} bottom lines")
    
    print("\n   Bottom lines extracted:")
    for i, line in enumerate(bottom_lines, 1):
        print(f"     {i}. {line.strip()}")
    
    # Step 3: Save file without bottom lines
    print("\n3. Saving file without bottom lines...")
    success, extracted_bottom = save_file_without_bottom(backup_file, temp_file)
    
    if success:
        print(f"   File saved without bottom lines: {temp_file}")
        print(f"   Bottom lines stored in memory for later use")
    
    # Step 4: Work with the clean file (your processing here)
    print("\n4. Working with clean file...")
    print("   (This is where you would add your channel processing logic)")
    
    # Example: Add a new line to the data
    with open(temp_file, 'a') as f:
        f.write('*,C_T99_NEW,"NEW_CHANNEL",10,8,0,\n')
    print("   Added example new data line")
    
    # Step 5: Restore bottom lines
    print("\n5. Restoring bottom lines...")
    success = restore_bottom_lines(temp_file, bottom_lines)
    
    if success:
        print("   Bottom lines restored successfully")
    
    # Step 6: Verify the result
    print("\n6. Verification...")
    with open(temp_file, 'r') as f:
        lines = f.readlines()
    
    print(f"   Final file has {len(lines)} total lines")
    print("   Last few lines:")
    for line in lines[-6:]:
        print(f"     {line.strip()}")
    
    print(f"\n=== Workflow Complete ===")
    print(f"Original file: {original_file} (unchanged)")
    print(f"Backup file: {backup_file}")
    print(f"Modified file: {temp_file}")
    print(f"Bottom lines stored in variable: {len(bottom_lines)} lines")


if __name__ == "__main__":
    example_workflow()
