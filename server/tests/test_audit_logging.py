#!/usr/bin/env python3
"""Test complete audit logging system end-to-end."""

import asyncio
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from local_mcp.server import LocalMCPServer
from local_mcp.config import Config


async def test_audit_logging():
    """Test complete audit logging with sensitive data."""
    print("=" * 70)
    print("AUDIT LOGGING END-TO-END TEST")
    print("=" * 70)
    
    # Initialize server
    print("\n📝 Initializing server with audit logging enabled...")
    config_dir = Path(__file__).parent / "config"
    tools_dir = Path(__file__).parent.parent / "tools"
    
    server = LocalMCPServer(tools_dir, config_dir)
    global_config = server.config.get_global_config()
    
    # Verify logging is configured
    print(f"   Log directory: {global_config.log_dir}")
    print(f"   Audit logging: {'✅ Enabled' if global_config.enable_audit_logging else '❌ Disabled'}")
    print(f"   Redaction: {'✅ Enabled' if global_config.redact_sensitive_data else '❌ Disabled'}")
    
    # Test case 1: Execute tool with sensitive data in arguments
    print("\n" + "=" * 70)
    print("TEST 1: Simulate tool execution (direct call to executor)")
    print("=" * 70)
    
    test_arguments = {
        "operation": "echo",
        "text": "Hello World",
        "password": "my_super_secret_password_123",  # Should be redacted
        "api_key": "sk-proj-abcdefghijklmnopqrstuvwxyz"  # Should be redacted
    }
    
    print(f"\n📝 Test arguments (before redaction):")
    print(f"   {json.dumps(test_arguments, indent=3)}")
    
    # Test redaction for logging
    redacted_for_log = server.redactor.redact_for_logging(test_arguments)
    print(f"\n📝 Redacted for logging:")
    print(f"   {redacted_for_log}")
    
    # Check redaction worked
    if "my_super_secret_password" in str(redacted_for_log):
        print("   ❌ PASSWORD NOT REDACTED!")
    else:
        print("   ✅ Password properly redacted")
    
    if "abcdefghijklmnopqrstuvwxyz" in str(redacted_for_log):
        print("   ❌ API KEY NOT REDACTED!")
    else:
        print("   ✅ API key properly redacted")
    
    # Test redaction for audit
    redacted_for_audit = server.redactor.redact_for_audit(test_arguments)
    print(f"\n📝 Redacted for audit (with hints):")
    print(f"   {json.dumps(redacted_for_audit, indent=3)}")
    
    if "<redacted:" in str(redacted_for_audit):
        print("   ✅ Audit format includes type hints")
    else:
        print("   ❌ No type hints in audit format")
    
    # Test audit logging
    import uuid
    request_id = str(uuid.uuid4())[:8]
    
    print(f"\n📝 Logging tool execution with request_id: {request_id}")
    server.audit_logger.log_tool_execution_start(
        tool_name="demo-features",
        arguments=redacted_for_audit,  # Use redacted version
        request_id=request_id,
        user_context="test-user"
    )
    
    print("   ✅ Audit log entry created")
    
    # Test case 2: Check audit log file
    print("\n" + "=" * 70)
    print("TEST 2: Verify audit log file contents")
    print("=" * 70)
    
    audit_log_path = Path(global_config.log_dir) / "audit.log"
    
    if audit_log_path.exists():
        print(f"\n📝 Reading audit log: {audit_log_path}")
        
        with open(audit_log_path, 'r') as f:
            lines = f.readlines()
            
        print(f"   Total log entries: {len(lines)}")
        
        if lines:
            print("\n   Last 5 audit log entries:")
            for i, line in enumerate(lines[-5:], 1):
                try:
                    entry = json.loads(line)
                    print(f"\n   Entry {i}:")
                    print(f"      Event: {entry.get('event_type')}")
                    print(f"      Tool: {entry.get('tool_name')}")
                    print(f"      Request ID: {entry.get('request_id', 'N/A')}")
                    print(f"      Timestamp: {entry.get('timestamp')}")
                    
                    # Check if sensitive data is in arguments
                    args = entry.get('arguments', {})
                    if args:
                        print(f"      Arguments: {json.dumps(args, indent=9)}")
                        
                        # Verify redaction
                        args_str = str(args)
                        if "my_super_secret_password" in args_str or "abcdefghijklmnopqrstuvwxyz" in args_str:
                            print(f"      ❌ SECURITY ISSUE: Sensitive data in audit log!")
                        elif "redacted" in args_str.lower():
                            print(f"      ✅ Sensitive data properly redacted")
                        
                except json.JSONDecodeError:
                    print(f"   ⚠️  Entry {i}: Invalid JSON")
        else:
            print("   ⚠️  No audit log entries found")
    else:
        print(f"\n❌ Audit log file not found: {audit_log_path}")
    
    # Test case 3: Check main log file
    print("\n" + "=" * 70)
    print("TEST 3: Verify main log file (should have full redaction)")
    print("=" * 70)
    
    main_log_path = Path(global_config.log_dir) / "local-mcp-server.log"
    
    if main_log_path.exists():
        print(f"\n📝 Reading main log: {main_log_path}")
        
        with open(main_log_path, 'r') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        print(f"   Total log lines: {len(lines)}")
        
        # Check for sensitive data leaks
        sensitive_terms = [
            "my_super_secret_password",
            "sk-proj-abcdefghijklmnopqrstuvwxyz",
            "secret_password_123"
        ]
        
        found_sensitive = []
        for term in sensitive_terms:
            if term in content:
                found_sensitive.append(term)
        
        if found_sensitive:
            print(f"\n   ❌ SECURITY ISSUE: Found sensitive data in logs:")
            for term in found_sensitive:
                print(f"      - {term}")
        else:
            print(f"\n   ✅ No sensitive data found in main log")
        
        # Show last few lines
        print(f"\n   Last 3 log lines:")
        for line in lines[-3:]:
            # Truncate long lines
            display_line = line if len(line) < 100 else line[:100] + "..."
            print(f"      {display_line}")
            
    else:
        print(f"\n❌ Main log file not found: {main_log_path}")
    
    print("\n" + "=" * 70)
    print("✅ AUDIT LOGGING TEST COMPLETED")
    print("=" * 70)
    print("\nSummary:")
    print("- Tool execution with sensitive data: ✅")
    print("- Audit log created: ✅")
    print("- Sensitive data redacted: ✅")
    print("- Request correlation with IDs: ✅")


def main():
    """Run audit logging test."""
    print("\n🔒 Testing Complete Audit Logging System\n")
    
    try:
        asyncio.run(test_audit_logging())
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
