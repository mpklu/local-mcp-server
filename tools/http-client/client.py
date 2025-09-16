#!/usr/bin/env python3
"""
HTTP Client Utilities

Provides HTTP request capabilities for testing APIs and web services.
This tool showcases HTTP operations, error handling, and structured responses.
"""

import json
import time
import fire
import requests
from urllib.parse import urlparse
from datetime import datetime
from typing import Optional, Dict, Any


def get_url(url, headers=None, timeout=30, follow_redirects=True):
    """Make GET request to URL with optional headers.
    
    Args:
        url (str): The URL to request
        headers (str, optional): JSON string of headers to include
        timeout (int): Request timeout in seconds (default: 30)
        follow_redirects (bool): Whether to follow redirects (default: True)
        
    Returns:
        str: JSON formatted response details
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return "Error: Invalid URL. Must include protocol (http:// or https://)"
        
        # Parse headers if provided
        request_headers = {}
        if headers:
            try:
                request_headers = json.loads(headers)
            except json.JSONDecodeError:
                return "Error: Headers must be valid JSON string"
        
        # Add user agent if not provided
        if 'User-Agent' not in request_headers:
            request_headers['User-Agent'] = 'Local-MCP-Server-HTTP-Client/1.0'
        
        # Make request
        start_time = time.time()
        response = requests.get(
            url, 
            headers=request_headers,
            timeout=timeout,
            allow_redirects=follow_redirects
        )
        end_time = time.time()
        
        # Build result
        result = {
            "request": {
                "url": url,
                "method": "GET",
                "headers": request_headers,
                "timestamp": datetime.now().isoformat()
            },
            "response": {
                "status_code": response.status_code,
                "status_text": response.reason,
                "headers": dict(response.headers),
                "content_type": response.headers.get('Content-Type', 'unknown'),
                "content_length": len(response.content),
                "encoding": response.encoding,
                "elapsed_seconds": round(end_time - start_time, 3)
            },
            "content": {
                "preview": response.text[:500] if response.text else "",
                "truncated": len(response.text) > 500 if response.text else False,
                "is_json": _is_json_response(response),
                "size_bytes": len(response.content)
            }
        }
        
        # Add redirect information if redirects occurred
        if response.history:
            result["redirects"] = [
                {"url": r.url, "status_code": r.status_code} 
                for r in response.history
            ]
        
        return json.dumps(result, indent=2)
        
    except requests.exceptions.Timeout:
        return f"Error: Request timed out after {timeout} seconds"
    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to {url}"
    except requests.exceptions.RequestException as e:
        return f"Error making request: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def post_data(url, data, content_type="application/json", headers=None, timeout=30):
    """POST data to URL with specified content type.
    
    Args:
        url (str): The URL to POST to
        data (str): Data to send in the request body
        content_type (str): Content-Type header (default: application/json)
        headers (str, optional): JSON string of additional headers
        timeout (int): Request timeout in seconds (default: 30)
        
    Returns:
        str: JSON formatted response details
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return "Error: Invalid URL. Must include protocol (http:// or https://)"
        
        # Parse additional headers if provided
        request_headers = {'Content-Type': content_type}
        if headers:
            try:
                additional_headers = json.loads(headers)
                request_headers.update(additional_headers)
            except json.JSONDecodeError:
                return "Error: Headers must be valid JSON string"
        
        # Add user agent if not provided
        if 'User-Agent' not in request_headers:
            request_headers['User-Agent'] = 'Local-MCP-Server-HTTP-Client/1.0'
        
        # Prepare data based on content type
        if content_type == 'application/json':
            try:
                # Validate JSON if content type is JSON
                json.loads(data)
            except json.JSONDecodeError:
                return "Error: Data must be valid JSON when content-type is application/json"
        
        # Make request
        start_time = time.time()
        response = requests.post(
            url,
            data=data.encode('utf-8'),
            headers=request_headers,
            timeout=timeout
        )
        end_time = time.time()
        
        result = {
            "request": {
                "url": url,
                "method": "POST",
                "headers": request_headers,
                "data_size": len(data.encode('utf-8')),
                "content_type": content_type,
                "timestamp": datetime.now().isoformat()
            },
            "response": {
                "status_code": response.status_code,
                "status_text": response.reason,
                "headers": dict(response.headers),
                "content_type": response.headers.get('Content-Type', 'unknown'),
                "content_length": len(response.content),
                "elapsed_seconds": round(end_time - start_time, 3)
            },
            "content": {
                "preview": response.text[:500] if response.text else "",
                "truncated": len(response.text) > 500 if response.text else False,
                "is_json": _is_json_response(response),
                "size_bytes": len(response.content)
            }
        }
        
        return json.dumps(result, indent=2)
        
    except requests.exceptions.Timeout:
        return f"Error: Request timed out after {timeout} seconds"
    except requests.exceptions.ConnectionError:
        return f"Error: Could not connect to {url}"
    except requests.exceptions.RequestException as e:
        return f"Error making request: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def check_status(url, expected_status=200, timeout=10):
    """Check HTTP status of URL quickly.
    
    Args:
        url (str): URL to check
        expected_status (int): Expected HTTP status code (default: 200)
        timeout (int): Request timeout in seconds (default: 10)
        
    Returns:
        str: JSON formatted status check result
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return "Error: Invalid URL. Must include protocol (http:// or https://)"
        
        # Make HEAD request (faster than GET)
        start_time = time.time()
        response = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={'User-Agent': 'Local-MCP-Server-HTTP-Client/1.0'}
        )
        end_time = time.time()
        
        # Determine status
        is_healthy = response.status_code == expected_status
        status_category = _get_status_category(response.status_code)
        
        result = {
            "url": url,
            "status_code": response.status_code,
            "status_text": response.reason,
            "expected_status": expected_status,
            "is_healthy": is_healthy,
            "status_category": status_category,
            "response_time_ms": round((end_time - start_time) * 1000, 1),
            "server": response.headers.get('Server', 'unknown'),
            "content_type": response.headers.get('Content-Type', 'unknown'),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add redirect information if applicable
        if response.history:
            result["redirected"] = True
            result["final_url"] = response.url
            result["redirect_count"] = len(response.history)
        else:
            result["redirected"] = False
        
        return json.dumps(result, indent=2)
        
    except requests.exceptions.Timeout:
        return json.dumps({
            "url": url,
            "error": f"Timeout after {timeout} seconds",
            "is_healthy": False,
            "timestamp": datetime.now().isoformat()
        }, indent=2)
    except requests.exceptions.ConnectionError:
        return json.dumps({
            "url": url,
            "error": "Connection failed",
            "is_healthy": False,
            "timestamp": datetime.now().isoformat()
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "url": url,
            "error": str(e),
            "is_healthy": False,
            "timestamp": datetime.now().isoformat()
        }, indent=2)


def batch_check(urls, timeout=10, max_workers=5):
    """Check status of multiple URLs concurrently.
    
    Args:
        urls (str): Comma-separated list of URLs to check
        timeout (int): Request timeout per URL (default: 10)
        max_workers (int): Maximum concurrent requests (default: 5)
        
    Returns:
        str: JSON formatted results for all URLs
    """
    import concurrent.futures
    
    try:
        # Parse URLs
        url_list = [url.strip() for url in urls.split(',')]
        if len(url_list) > 20:
            return "Error: Maximum 20 URLs allowed for batch checking"
        
        def check_single_url(url):
            """Helper function for single URL check."""
            try:
                start_time = time.time()
                response = requests.head(url, timeout=timeout, allow_redirects=True)
                end_time = time.time()
                
                return {
                    "url": url,
                    "status_code": response.status_code,
                    "status_text": response.reason,
                    "response_time_ms": round((end_time - start_time) * 1000, 1),
                    "is_healthy": response.status_code == 200,
                    "error": None
                }
            except Exception as e:
                return {
                    "url": url,
                    "status_code": None,
                    "status_text": None,
                    "response_time_ms": None,
                    "is_healthy": False,
                    "error": str(e)
                }
        
        # Execute concurrent requests
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(check_single_url, url): url for url in url_list}
            for future in concurrent.futures.as_completed(future_to_url):
                results.append(future.result())
        
        # Sort results by original URL order
        url_to_result = {r["url"]: r for r in results}
        ordered_results = [url_to_result[url] for url in url_list]
        
        # Summary statistics
        healthy_count = sum(1 for r in results if r["is_healthy"])
        avg_response_time = sum(r["response_time_ms"] for r in results if r["response_time_ms"]) / len([r for r in results if r["response_time_ms"]])
        
        final_result = {
            "summary": {
                "total_urls": len(url_list),
                "healthy_urls": healthy_count,
                "unhealthy_urls": len(url_list) - healthy_count,
                "success_rate_percent": round((healthy_count / len(url_list)) * 100, 1),
                "average_response_time_ms": round(avg_response_time, 1) if avg_response_time else 0,
                "timestamp": datetime.now().isoformat()
            },
            "results": ordered_results
        }
        
        return json.dumps(final_result, indent=2)
        
    except Exception as e:
        return f"Error in batch check: {str(e)}"


def _is_json_response(response):
    """Check if response is JSON."""
    content_type = response.headers.get('Content-Type', '').lower()
    return 'application/json' in content_type


def _get_status_category(status_code):
    """Get HTTP status code category."""
    if 200 <= status_code < 300:
        return "success"
    elif 300 <= status_code < 400:
        return "redirect"
    elif 400 <= status_code < 500:
        return "client_error"
    elif 500 <= status_code < 600:
        return "server_error"
    else:
        return "unknown"


if __name__ == "__main__":
    fire.Fire()