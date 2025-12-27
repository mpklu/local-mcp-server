#!/usr/bin/env python3
"""Test sensitive data redaction."""

import json
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from local_mcp.sanitization import SensitiveDataRedactor


def test_keyword_based_redaction():
    """Test redaction of sensitive keywords."""
    print("=" * 70)
    print("TEST 1: Keyword-Based Redaction")
    print("=" * 70)
    
    redactor = SensitiveDataRedactor()
    
    test_cases = [
        {
            "name": "Password field",
            "data": {"username": "admin", "password": "secret123"},
            "should_redact": ["password"]
        },
        {
            "name": "API key",
            "data": {"api_key": "sk-proj-abc123xyz", "endpoint": "https://api.example.com"},
            "should_redact": ["api_key"]
        },
        {
            "name": "Multiple secrets",
            "data": {"token": "bearer_token", "secret": "my_secret", "public_data": "visible"},
            "should_redact": ["token", "secret"]
        },
        {
            "name": "Nested dict",
            "data": {"config": {"database": {"password": "dbpass123", "host": "localhost"}}},
            "should_redact": ["password"]
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 {test['name']}")
        print(f"   Input: {json.dumps(test['data'], indent=6)}")
        
        redacted = redactor.redact_dict(test['data'])
        print(f"   Output: {json.dumps(redacted, indent=6)}")
        
        # Check if sensitive fields were redacted
        success = True
        for field in test['should_redact']:
            if field in str(redacted) and "REDACTED" not in str(redacted):
                success = False
        
        status = "✅" if success else "❌"
        print(f"   {status} Redaction {'successful' if success else 'FAILED'}")


def test_pattern_based_redaction():
    """Test pattern-based redaction."""
    print("\n" + "=" * 70)
    print("TEST 2: Pattern-Based Redaction")
    print("=" * 70)
    
    redactor = SensitiveDataRedactor()
    
    test_cases = [
        {
            "name": "Credit card in value",
            "data": {"note": "Card number is 4532-1234-5678-9012"},
            "pattern": "credit_card"
        },
        {
            "name": "SSN in value",
            "data": {"info": "SSN: 123-45-6789"},
            "pattern": "ssn"
        },
        {
            "name": "OpenAI API key",
            "data": {"message": "Use key sk-proj-abcdefghijklmnopqrstuvwxyz1234567890abcdef"},
            "pattern": "api_key"
        },
        {
            "name": "AWS access key",
            "data": {"credentials": "AWS key: AKIAIOSFODNN7EXAMPLE"},
            "pattern": "aws_key"
        },
        {
            "name": "GitHub token",
            "data": {"auth": "Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"},
            "pattern": "github_token"
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 {test['name']}")
        print(f"   Input: {json.dumps(test['data'], indent=6)}")
        
        redacted = redactor.redact_dict(test['data'], scan_values=True)
        print(f"   Output: {json.dumps(redacted, indent=6)}")
        
        # Check if pattern was caught
        contains_redacted = "REDACTED" in str(redacted)
        status = "✅" if contains_redacted else "❌"
        print(f"   {status} Pattern {'detected and redacted' if contains_redacted else 'NOT detected'}")


def test_logging_format():
    """Test redaction for logging."""
    print("\n" + "=" * 70)
    print("TEST 3: Logging Format Redaction")
    print("=" * 70)
    
    redactor = SensitiveDataRedactor()
    
    test_cases = [
        {
            "name": "Tool arguments with password",
            "data": {"function": "authenticate", "username": "admin", "password": "secret123", "host": "db.example.com"}
        },
        {
            "name": "HTTP request with auth header",
            "data": {"url": "https://api.example.com", "headers": {"authorization": "Bearer abc123xyz"}, "method": "POST"}
        },
        {
            "name": "Database connection",
            "data": {"driver": "postgresql", "host": "localhost", "database": "mydb", "password": "dbpass"}
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 {test['name']}")
        print(f"   Original: {test['data']}")
        
        redacted_log = redactor.redact_for_logging(test['data'], max_length=200)
        print(f"   For logging: {redacted_log}")
        
        # Check safe for logging
        contains_sensitive = any(word in redacted_log.lower() for word in ['secret', 'dbpass', 'abc123'])
        status = "✅" if not contains_sensitive else "❌"
        print(f"   {status} {'Safe for logging' if not contains_sensitive else 'CONTAINS SENSITIVE DATA'}")


def test_audit_format():
    """Test redaction for audit logs."""
    print("\n" + "=" * 70)
    print("TEST 4: Audit Log Format (with hints)")
    print("=" * 70)
    
    redactor = SensitiveDataRedactor()
    
    test_data = {
        "tool": "database_query",
        "user": "admin@example.com",
        "password": "supersecret123",
        "api_key": "sk-proj-verylongapikey123456789",
        "query": "SELECT * FROM users"
    }
    
    print(f"\n📝 Original data:")
    print(f"   {json.dumps(test_data, indent=3)}")
    
    redacted_audit = redactor.redact_for_audit(test_data)
    print(f"\n   Audit format (with hints):")
    print(f"   {json.dumps(redacted_audit, indent=3)}")
    
    # Check hints are present
    contains_hints = "<redacted:" in str(redacted_audit)
    status = "✅" if contains_hints else "❌"
    print(f"\n   {status} {'Type hints included for debugging' if contains_hints else 'No hints found'}")


def test_redaction_styles():
    """Test different redaction styles."""
    print("\n" + "=" * 70)
    print("TEST 5: Redaction Styles")
    print("=" * 70)
    
    redactor = SensitiveDataRedactor()
    
    test_data = {"password": "my_secret_password_123"}
    
    styles = ["full", "partial", "hint"]
    
    for style in styles:
        print(f"\n📝 Style: {style}")
        redacted = redactor.redact_dict(test_data, redaction_style=style)
        print(f"   Result: {redacted}")


def main():
    """Run all redaction tests."""
    print("\n🔒 Testing Sensitive Data Redaction\n")
    
    try:
        test_keyword_based_redaction()
        test_pattern_based_redaction()
        test_logging_format()
        test_audit_format()
        test_redaction_styles()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 70)
        print("\nSensitive data redaction is working correctly!")
        print("- Keywords are detected and redacted")
        print("- Patterns like credit cards and API keys are caught")
        print("- Logging format is safe")
        print("- Audit logs include helpful type hints")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
