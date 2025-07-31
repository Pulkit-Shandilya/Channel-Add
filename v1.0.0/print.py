# Extract components
data_lines, bottom_lines, header_lines = extract_and_remove_bottom_lines("file.fac")

# Process your data
# ... your channel addition logic here ...

# Write back complete file
with open("file.fac", 'w') as f:
    f.writelines(header_lines)      # Original header
    f.writelines(modified_data)     # Your modified data
    f.writelines(bottom_lines)      # Original bottom metadata