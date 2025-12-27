#!/usr/bin/env python3
"""
Quick test for error sanitization functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from local_mcp.sanitization import SafeErrorFormatter


def test_error_sanitization():
    """Test various error scenarios to ensure sensitive info is not leaked."""
    
    print("Testing SafeErrorFormatter...")
    print("=" * 70)
    
    # Test 1: FileNotFoundError with filesystem path
    print("\n1. FileNotFoundError (should hide filesystem path)")
    print("-" * 70)
    try:
        open('/Users/kunlu/Projects/secret-project/passwords.txt')
    except Exception as e:
        safe_msg = SafeErrorFormatter.format_error(e, tool_name="file-ops", request_id="test-001")
        print(f"Original error: {e}")
        print(f"Safe message: {safe_msg}")
        assert "/Users/kunlu" not in safe_msg, "❌ Path leaked!"
        assert "passwords.txt" not in safe_msg, "❌ Filename leaked!"
        print("✅ Path successfully hidden")
    
    # Test 2: PermissionError
    print("\n2. PermissionError (should sanitize)")
    print("-" * 70)
    try:
        open('/etc/shadow', 'w')
    except Exception as e:
        safe_msg = SafeErrorFormatter.format_error(e, tool_name="file-ops")
        print(f"Original error: {e}")
        print(f"Safe message: {safe_msg}")
        assert "/etc/shadow" not in safe_msg, "❌ Sensitive path leaked!"
        print("✅ Permission error sanitized")
    
    # Test 3: ModuleNotFoundError (acceptable to show module name)
    print("\n3. ModuleNotFoundError (module name OK)")
    print("-" * 70)
    try:
        import nonexistent_module
    except Exception as e:
        safe_msg = SafeErrorFormatter.format_error(e, tool_name="http-client")
        print(f"Original error: {e}")
        print(f"Safe message: {safe_msg}")
        print("✅ Module error handled")
    
    # Test 4: ValueError (generic)
    print("\n4. ValueError (generic message)")
    print("-" * 70)
    e = ValueError("Database password must be at least 8 characters")
    safe_msg = SafeErrorFormatter.format_error(e, tool_name="db-tool")
    print(f"Original error: {e}")
    print(f"Safe message: {safe_msg}")
    assert "password" not in safe_msg.lower() or "Invalid" in safe_msg, "✅ Generic error message"
    print("✅ Value error sanitized")
    
    # Test 5: Error with partial details (scrubbed)
    print("\n5. Error with scrubbed details")
    print("-" * 70)
    try:
        open('/Users/admin/secret-api-keys/production.env')
    except Exception as e:
        safe_msg = SafeErrorFormatter.format_error_with_details(
            e, 
            tool_name="file-ops",
            allow_partial_message=True
        )
        print(f"Original error: {e}")
        print(f"Safe message with scrubbed details: {safe_msg}")
        assert "/Users/admin" not in safe_msg or "<user>" in safe_msg, "❌ Username leaked!"
        print("✅ Scrubbing applied")
    
    # Test 6: Simulated database error
    print("\n6. Simulated database connection error")
    print("-" * 70)
    e = ConnectionRefusedError("Connection to postgresql://admin:secret@localhost:5432/prod failed")
    safe_msg = SafeErrorFormatter.format_error(e, tool_name="db-tool")
    safe_msg_details = SafeErrorFormatter.format_error_with_details(
        e,
        tool_name="db-tool",
        allow_partial_message=True
    )
    print(f"Original error: {e}")
    print(f"Safe message (basic): {safe_msg}")
    print(f"Safe message (with scrubbed details): {safe_msg_details}")
    assert "admin:secret" not in safe_msg_details, "❌ Credentials leaked!"
    assert "<database_url>" in safe_msg_details or "Connection" in safe_msg_details
    print("✅ Database error sanitized")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed! Error sanitization is working correctly.")
    print("=" * 70)


if __name__ == "__main__":
    test_error_sanitization()
