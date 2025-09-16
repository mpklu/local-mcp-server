# File Operations Tool

This tool provides basic file and directory operations with safety checks including:

- Directory listing with pattern matching
- File reading with encoding support
- Safe file creation with overwrite protection
- Detailed file metadata and information

## Usage Examples

### List files in current directory
```bash
python run.py list_files
```

### List files with pattern
```bash
python run.py list_files /path/to/dir "*.py" --include_hidden=True
```

### Read file contents
```bash
python run.py read_file "example.txt"
python run.py read_file "large_file.log" --lines=100
```

### Create new file
```bash
python run.py create_file "new_file.txt" "Hello World!" --overwrite=False
```

### Get file information
```bash
python run.py get_file_info "/path/to/file"
```

## Available Functions

### list_files(directory=".", pattern="*", include_hidden=False)
- **directory**: Directory to list files from (default: current directory)
- **pattern**: Glob pattern to match files (default: "*" for all files)
- **include_hidden**: Include hidden files/directories (default: False)

### read_file(file_path, lines=None, encoding="utf-8")
- **file_path**: Path to the file to read (required)
- **lines**: Maximum number of lines to read (None for all)
- **encoding**: File encoding (default: utf-8)

### create_file(file_path, content="", overwrite=False)
- **file_path**: Path where the file should be created (required)
- **content**: Content to write to the file (default: empty)
- **overwrite**: Whether to overwrite existing files (default: False)

### get_file_info(file_path)
- **file_path**: Path to examine (required)

## Features Demonstrated

- **Multiple Parameters**: Various parameter types and combinations
- **File Safety**: Existence checks and overwrite protection
- **Input Validation**: Path validation and error handling
- **Structured Output**: JSON formatted results with metadata
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Error Recovery**: Graceful handling of file system errors

## Dependencies

Install dependencies with:
```bash
pip install -r requirements.txt
```