# .fac File Bottom Lines Management

## Overview
This module provides functions to extract, remove, and restore the bottom metadata lines from .fac files. This is useful when you need to modify the data content while preserving the file's metadata structure.

## .fac File Structure
```
Header lines (file info)
!COLUMN_HEADERS...           <- Header line with column definitions
Data lines                   <- Actual data rows
##END##                      <- Start of bottom metadata
##COLOR####ENDCOLOR##
##FORMULA####ENDFORMULA##
##NOTES####ENDNOTES##
##USEROWDEFAULTVALUE####ENDUSEROWDEFAULTVALUE##
##ROWDEFAULTVALUE####ENDROWDEFAULTVALUE##
##GENERIC##VAR_NAME##ENDGENERIC##
```

## Main Functions

### 1. `extract_and_remove_bottom_lines(file_path)`
Extracts the file into three components:

**Returns:**
- `data_lines`: List of data rows (between header and metadata)
- `bottom_lines`: List of bottom metadata lines (##END##, etc.)
- `header_lines`: List of header lines (before data starts)

**Example:**
```python
data_lines, bottom_lines, header_lines = extract_and_remove_bottom_lines("file.fac")
print(f"Found {len(bottom_lines)} bottom lines")
```

### 2. `save_file_without_bottom(file_path, output_path=None)`
Saves a clean version of the file without bottom metadata.

**Parameters:**
- `file_path`: Original file path
- `output_path`: Output file path (optional, defaults to original file)

**Returns:**
- `(success, bottom_lines)`: Success status and extracted bottom lines

**Example:**
```python
success, bottom_lines = save_file_without_bottom("file.fac", "clean_file.fac")
if success:
    print("Clean file saved!")
```

### 3. `restore_bottom_lines(file_path, bottom_lines)`
Restores the bottom metadata lines to a file.

**Parameters:**
- `file_path`: File to restore bottom lines to
- `bottom_lines`: List of bottom lines to append

**Example:**
```python
success = restore_bottom_lines("modified_file.fac", bottom_lines)
```

## Typical Workflow

### Step 1: Extract Components
```python
# Extract the file components
data_lines, bottom_lines, header_lines = extract_and_remove_bottom_lines("file.fac")

# Store bottom lines for later
saved_bottom_lines = bottom_lines.copy()
```

### Step 2: Process Data
```python
# Work with clean data lines
modified_data = []
for line in data_lines:
    # Your processing logic here
    if line.startswith('*,'):
        # Modify the line as needed
        modified_line = process_line(line)
        modified_data.append(modified_line)
    else:
        modified_data.append(line)

# Add new data if needed
modified_data.append('*,NEW_PRODUCT,"NEW_CHANNEL",10,7,0,\\n')
```

### Step 3: Save Complete File
```python
# Write back with all components
with open("file.fac", 'w') as f:
    f.writelines(header_lines)      # Header
    f.writelines(modified_data)     # Modified data
    f.writelines(saved_bottom_lines) # Bottom metadata
```

## Example: Adding a New Channel

```python
def add_channel_to_file(file_path, new_channel_name):
    # Extract components
    data_lines, bottom_lines, header_lines = extract_and_remove_bottom_lines(file_path)
    
    # Find unique products
    unique_products = set()
    for line in data_lines:
        if line.startswith('*,'):
            parts = line.split(',')
            if len(parts) >= 2:
                product = parts[1].strip('"')
                unique_products.add(product)
    
    # Add new channel entries
    new_entries = []
    for product in unique_products:
        new_entry = f'*,{product},"{new_channel_name}",10,7,0,\\n'
        new_entries.append(new_entry)
    
    # Combine all data
    all_data = data_lines + new_entries
    
    # Write back complete file
    with open(file_path, 'w') as f:
        f.writelines(header_lines)
        f.writelines(all_data)
        f.writelines(bottom_lines)
    
    print(f"Added {len(new_entries)} entries for channel '{new_channel_name}'")
```

## Benefits

1. **Preserve Metadata**: Keeps all original file metadata intact
2. **Clean Processing**: Work with just the data without metadata interference
3. **Flexible Workflow**: Extract, modify, and restore in separate steps
4. **Error Recovery**: Can restore original structure if processing fails
5. **Backup Friendly**: Easy to create backups before modification

## Error Handling

All functions include try-catch blocks and return appropriate status indicators. Always check return values:

```python
data_lines, bottom_lines, header_lines = extract_and_remove_bottom_lines(file_path)
if not bottom_lines:
    print("Warning: No bottom lines found or error occurred")

success, extracted = save_file_without_bottom(file_path)
if not success:
    print("Error: Could not save file")
```
