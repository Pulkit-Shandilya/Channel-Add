# Channel Add - .fac File Processor

Simple tool to add CHANNEL_TI rows to .fac files that contain both CHANNEL and PRODUCT columns.

## Files

- `main.py` - Main processing script
- `fac_reader.py` - File reading/writing utilities
- `ChannelAdd.bat` - **Simple launcher for Windows**
- `Data/` - Input data folder

## Quick Start

### Windows Users
**Double-click `ChannelAdd.bat`** - Launches the interactive processor

### Command Line
```bash
python main.py    # Interactive mode
```

## Usage

### Interactive Mode (Recommended)
The script will ask you to:
1. Enter the path to a folder or .fac file
2. Enter the agent name (or press Enter for default "CHANNEL_TI")
3. Confirm the operation

### Command Line Options
```bash
# Process with specific path and agent
python main.py --path "path\to\your\data" --agent "YOUR_AGENT_NAME"

# Restore backups (undo changes)
python main.py --restore

# Clean up backup files
python main.py --cleanup
```

## How It Works

1. **Scans** all .fac files in the specified folder or processes single file
2. **Filters** files that have both CHANNEL and PRODUCT columns
3. **Creates backups** before processing
4. **Adds new rows** with specified agent for each unique product combination
5. **Saves** modified files in place

## Safety Features

- Automatic backup creation
- Error recovery from backups
- User confirmation required
- Only processes files with required columns
- Interactive path validation

## Example Usage

### Interactive Mode
```
=== Channel Add - .fac File Processor ===

Enter the path to folder or .fac file: Data/TABLE_II_May'25

Enter new agent name (default: CHANNEL_TI): CUSTOM_AGENT

Found 135 .fac files total
16 files will be processed
119 files will be skipped

Proceed to modify 16 files? (yes/no): yes

Results:
  Successfully processed: 16 files
  Failed: 0 files
  Skipped: 119 files

Success! 16 files modified with CUSTOM_AGENT rows.
```

### Command Line Mode
```bash
python main.py --path "Data/TABLE_II_May'25" --agent "CHANNEL_TI"
```
