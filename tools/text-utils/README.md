# Text Processing Utilities

This tool provides comprehensive text analysis and manipulation capabilities including:

- Word count and text statistics
- Text formatting and transformations
- URL extraction and analysis  
- Pattern matching with regex
- Text cleaning and normalization

## Usage Examples

### Analyze text statistics
```bash
python run.py word_count "Your text here to analyze for word count and statistics."
```

### Format text in different ways
```bash
python run.py format_text "hello world" --action=uppercase
python run.py format_text "MAKE THIS TITLE CASE" --action=title
python run.py format_text "add line numbers to this text" --action=add_line_numbers
```

### Extract URLs from text
```bash
python run.py extract_urls "Check out https://github.com and https://stackoverflow.com for coding help!"
```

### Find patterns with regex
```bash
python run.py find_patterns "Email: test@example.com, contact@site.org" "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
```

### Clean and normalize text  
```bash
python run.py clean_text "<p>HTML text with   extra spaces!</p>" --remove_html=True --remove_extra_whitespace=True
```

## Available Actions for format_text

- `uppercase` - Convert to UPPERCASE
- `lowercase` - convert to lowercase  
- `title` - Convert To Title Case
- `capitalize` - Capitalize first letter only
- `reverse` - esreveR text
- `remove_spaces` - Removespaces
- `remove_extra_spaces` - Normalize   multiple   spaces
- `add_line_numbers` - Add line numbers
- `snake_case` - convert_to_snake_case
- `camel_case` - ConvertToCamelCase

## Features Demonstrated

- **Text Analysis**: Comprehensive word/character counting
- **Multiple Parameters**: Different formatting actions
- **Regex Processing**: Pattern matching with flags
- **Structured Output**: JSON formatted results
- **Error Handling**: Input validation and error messages
- **Boolean Parameters**: Enable/disable cleaning options

## Dependencies

Install dependencies with:
```bash
pip install -r requirements.txt
```