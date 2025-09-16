# HTTP Client Utilities

This tool provides comprehensive HTTP request capabilities for testing APIs and web services including:

- GET requests with custom headers
- POST requests with various content types
- Quick status checks and health monitoring
- Batch URL testing with concurrent requests

## Usage Examples

### Make GET request
```bash
python run.py get_url "https://api.github.com/users/octocat"
```

### GET with custom headers
```bash
python run.py get_url "https://api.example.com/data" --headers='{"Authorization": "Bearer token123", "Accept": "application/json"}'
```

### POST JSON data
```bash
python run.py post_data "https://httpbin.org/post" '{"name": "test", "value": 123}' --content_type="application/json"
```

### POST form data
```bash
python run.py post_data "https://httpbin.org/post" "name=test&value=123" --content_type="application/x-www-form-urlencoded"
```

### Quick status check
```bash
python run.py check_status "https://example.com"
python run.py check_status "https://api.service.com/health" --expected_status=200
```

### Batch status checking
```bash
python run.py batch_check "https://google.com,https://github.com,https://stackoverflow.com"
```

## Available Functions

### get_url(url, headers=None, timeout=30, follow_redirects=True)
- **url**: Target URL (required)
- **headers**: JSON string of HTTP headers
- **timeout**: Request timeout in seconds
- **follow_redirects**: Whether to follow HTTP redirects

### post_data(url, data, content_type="application/json", headers=None, timeout=30)  
- **url**: Target URL (required)
- **data**: Request body data (required)
- **content_type**: Content-Type header
- **headers**: JSON string of additional headers
- **timeout**: Request timeout in seconds

### check_status(url, expected_status=200, timeout=10)
- **url**: URL to check (required)
- **expected_status**: Expected HTTP status code
- **timeout**: Request timeout in seconds

### batch_check(urls, timeout=10, max_workers=5)
- **urls**: Comma-separated list of URLs (required)
- **timeout**: Timeout per URL
- **max_workers**: Maximum concurrent requests (max 20 URLs)

## Features Demonstrated

- **HTTP Operations**: GET, POST, HEAD requests
- **Error Handling**: Timeout, connection, and HTTP errors
- **Structured Output**: JSON formatted responses with metadata
- **Parameter Validation**: URL validation and input checking
- **Concurrent Processing**: Batch operations with threading
- **Rich Metadata**: Response times, headers, content analysis

## Response Information

Each request returns detailed information including:
- Request details (URL, method, headers, timestamp)
- Response status and headers  
- Content preview and metadata
- Performance metrics (response time, size)
- Redirect information when applicable
- Error details for failed requests

## Dependencies

Install dependencies with:
```bash
pip install -r requirements.txt
```