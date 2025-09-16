#!/usr/bin/env python3
"""
Text Processing Utilities

Provides various text processing and analysis functions.
This tool showcases text manipulation, regex processing, and structured output.
"""

import json
import re
import fire
from collections import Counter
from typing import List, Dict, Any
from urllib.parse import urlparse


def word_count(text):
    """Count words, characters, and lines in text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        str: JSON formatted text statistics
    """
    try:
        if not isinstance(text, str):
            return "Error: Input must be a string"
        
        # Basic counts
        lines = text.split('\n')
        words = text.split()
        characters = len(text)
        characters_no_spaces = len(text.replace(' ', ''))
        
        # Word frequency analysis
        word_freq = Counter(word.lower().strip('.,!?";()[]{}') for word in words)
        most_common = word_freq.most_common(5)
        
        # Average word length
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        result = {
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "statistics": {
                "lines": len(lines),
                "words": len(words),
                "characters": characters,
                "characters_no_spaces": characters_no_spaces,
                "paragraphs": len([line for line in lines if line.strip()]),
                "average_word_length": round(avg_word_length, 2)
            },
            "word_frequency": {
                "most_common_words": [{"word": word, "count": count} for word, count in most_common],
                "unique_words": len(word_freq)
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error analyzing text: {str(e)}"


def format_text(text, action="uppercase"):
    """Format text using various transformations.
    
    Args:
        text (str): The text to format
        action (str): Format action - 'uppercase', 'lowercase', 'title', 'capitalize', 
                     'reverse', 'remove_spaces', 'add_line_numbers'
                     
    Returns:
        str: JSON formatted result with original and formatted text
    """
    try:
        if not isinstance(text, str):
            return "Error: Input must be a string"
        
        actions = {
            'uppercase': lambda t: t.upper(),
            'lowercase': lambda t: t.lower(),
            'title': lambda t: t.title(),
            'capitalize': lambda t: t.capitalize(),
            'reverse': lambda t: t[::-1],
            'remove_spaces': lambda t: t.replace(' ', ''),
            'remove_extra_spaces': lambda t: re.sub(r'\s+', ' ', t.strip()),
            'add_line_numbers': lambda t: '\n'.join(f"{i+1:3d}: {line}" for i, line in enumerate(t.split('\n'))),
            'snake_case': lambda t: re.sub(r'[^a-zA-Z0-9]', '_', t.lower()),
            'camel_case': lambda t: ''.join(word.capitalize() for word in re.findall(r'[a-zA-Z0-9]+', t))
        }
        
        if action not in actions:
            available = ', '.join(actions.keys())
            return f"Error: Unknown action '{action}'. Available actions: {available}"
        
        formatted = actions[action](text)
        
        result = {
            "original": text,
            "action": action,
            "formatted": formatted,
            "length_change": len(formatted) - len(text)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error formatting text: {str(e)}"


def extract_urls(text):
    """Extract all URLs from text using regex patterns.
    
    Args:
        text (str): The text to search for URLs
        
    Returns:
        str: JSON formatted list of found URLs with analysis
    """
    try:
        if not isinstance(text, str):
            return "Error: Input must be a string"
        
        # URL regex pattern
        url_pattern = r'https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?'
        
        # Find all URLs
        urls = re.findall(url_pattern, text)
        
        # Analyze URLs
        url_analysis = []
        for url in urls:
            try:
                parsed = urlparse(url)
                analysis = {
                    "url": url,
                    "domain": parsed.netloc,
                    "scheme": parsed.scheme,
                    "path": parsed.path,
                    "has_query": bool(parsed.query),
                    "has_fragment": bool(parsed.fragment)
                }
                url_analysis.append(analysis)
            except Exception:
                url_analysis.append({"url": url, "error": "Failed to parse"})
        
        # Domain frequency
        domains = [analysis.get("domain", "unknown") for analysis in url_analysis if "domain" in analysis]
        domain_freq = Counter(domains)
        
        result = {
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "total_urls": len(urls),
            "urls": url_analysis,
            "domain_frequency": [{"domain": domain, "count": count} for domain, count in domain_freq.most_common()],
            "unique_domains": len(domain_freq)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error extracting URLs: {str(e)}"


def find_patterns(text, pattern, flags=""):
    """Find all matches of a regex pattern in text.
    
    Args:
        text (str): The text to search
        pattern (str): Regular expression pattern
        flags (str): Regex flags ('i' for ignorecase, 'm' for multiline, 's' for dotall)
        
    Returns:
        str: JSON formatted matches with positions
    """
    try:
        if not isinstance(text, str):
            return "Error: Text input must be a string"
        
        if not isinstance(pattern, str):
            return "Error: Pattern must be a string"
        
        # Convert flags string to regex flags
        regex_flags = 0
        if 'i' in flags.lower():
            regex_flags |= re.IGNORECASE
        if 'm' in flags.lower():
            regex_flags |= re.MULTILINE
        if 's' in flags.lower():
            regex_flags |= re.DOTALL
        
        # Find all matches with positions
        matches = []
        for match in re.finditer(pattern, text, regex_flags):
            match_info = {
                "match": match.group(),
                "start": match.start(),
                "end": match.end(),
                "groups": match.groups() if match.groups() else []
            }
            matches.append(match_info)
        
        result = {
            "pattern": pattern,
            "flags": flags,
            "text_length": len(text),
            "total_matches": len(matches),
            "matches": matches[:20],  # Limit to first 20 matches
            "truncated": len(matches) > 20
        }
        
        return json.dumps(result, indent=2)
        
    except re.error as e:
        return f"Error: Invalid regex pattern: {str(e)}"
    except Exception as e:
        return f"Error finding patterns: {str(e)}"


def clean_text(text, remove_html=False, remove_extra_whitespace=True, remove_punctuation=False):
    """Clean and normalize text by removing various elements.
    
    Args:
        text (str): The text to clean
        remove_html (bool): Remove HTML tags
        remove_extra_whitespace (bool): Normalize whitespace
        remove_punctuation (bool): Remove punctuation characters
        
    Returns:
        str: JSON formatted result with cleaned text
    """
    try:
        if not isinstance(text, str):
            return "Error: Input must be a string"
        
        original_text = text
        cleaning_steps = []
        
        # Remove HTML tags
        if remove_html:
            html_pattern = r'<[^>]+>'
            text = re.sub(html_pattern, '', text)
            cleaning_steps.append("Removed HTML tags")
        
        # Remove extra whitespace
        if remove_extra_whitespace:
            text = re.sub(r'\s+', ' ', text.strip())
            cleaning_steps.append("Normalized whitespace")
        
        # Remove punctuation
        if remove_punctuation:
            text = re.sub(r'[^\w\s]', '', text)
            cleaning_steps.append("Removed punctuation")
        
        result = {
            "original": original_text,
            "cleaned": text,
            "cleaning_steps": cleaning_steps,
            "original_length": len(original_text),
            "cleaned_length": len(text),
            "reduction_percent": round(((len(original_text) - len(text)) / len(original_text)) * 100, 1) if original_text else 0
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error cleaning text: {str(e)}"


if __name__ == "__main__":
    fire.Fire()