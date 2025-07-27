import numpy as np

# Create a large .fac file for performance testing
def create_large_fac_file(filename, num_rows=5000):
    """Create a large .fac file for testing"""
    with open(filename, 'w') as f:
        # Write header
        f.write("header_col1 header_col2 header_col3 header_col4 header_col5 header_col6\n")
        
        # Write data rows
        for i in range(num_rows):
            row = [i] + [round(np.random.random() * 100, 2) for _ in range(5)]
            f.write(" ".join(map(str, row)) + "\n")
        
        # Write last 10 rows (to be skipped)
        for i in range(10):
            f.write(f"last{i} last{i} last{i} last{i} last{i} last{i}\n")

if __name__ == "__main__":
    create_large_fac_file("large_sample.fac", 5000)
    print("Created large_sample.fac with 5000 data rows + header + 10 footer rows")
