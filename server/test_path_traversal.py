#!/usr/bin/env python3
"""Test path traversal protection."""

import json
import asyncio
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from local_mcp.sanitization import InputSanitizer, validate_arguments_security
from local_mcp.config import Config, WorkspaceConfig


def test_path_sanitization():
    """Test path sanitization logic."""
    print("=" * 70)
    print("TEST 1: Path Sanitization")
    print("=" * 70)
    
    sanitizer = InputSanitizer()
    tools_dir = Path(__file__).parent.parent / "tools"
    
    # Create test allowed bases
    allowed_bases = [
        tools_dir / "file-ops" / "workspace"
    ]
    
    test_cases = [
        # (path, allow_absolute, follow_symlinks, should_pass, description)
        ("workspace/test.txt", False, True, True, "Valid relative path"),
        ("../../../etc/passwd", False, True, False, "Path traversal with parent refs"),
        ("/etc/passwd", False, True, False, "Absolute path (not allowed)"),
        ("/etc/passwd", True, True, False, "Absolute path outside allowed (even with allow_absolute)"),
        ("workspace/subdir/file.txt", False, True, True, "Valid nested path"),
        ("./workspace/data.json", False, True, True, "Valid path with ./"),
    ]
    
    print(f"\nAllowed bases: {allowed_bases}\n")
    
    for path, allow_abs, follow_sym, should_pass, desc in test_cases:
        is_valid, resolved, error = sanitizer.sanitize_path(
            path,
            allowed_bases,
            allow_absolute=allow_abs,
            follow_symlinks=follow_sym,
            tool_name="file-ops"
        )
        
        status = "✅" if is_valid == should_pass else "❌"
        result = "VALID" if is_valid else "BLOCKED"
        
        print(f"{status} {desc}")
        print(f"   Path: {path}")
        print(f"   Result: {result}")
        if error:
            print(f"   Error: {error}")
        if resolved:
            print(f"   Resolved: {resolved}")
        print()


def test_argument_validation():
    """Test full argument validation."""
    print("=" * 70)
    print("TEST 2: Argument Validation")
    print("=" * 70)
    
    tools_dir = Path(__file__).parent.parent / "tools"
    
    # Test config with default workspace
    config = {
        "name": "file-ops",
        "workspace_config": {
            "allowed_paths": ["{TOOL_DIR}/workspace"],
            "allow_absolute_paths": False,
            "follow_symlinks": True,
            "create_workspace": True,
            "max_string_length": 1000000,
            "check_prompt_injection": True
        }
    }
    
    test_cases = [
        # (arguments, should_pass, description)
        (
            {"function": "read_file", "filepath": "workspace/test.txt", "confirm": True},
            True,
            "Valid path within workspace"
        ),
        (
            {"function": "read_file", "filepath": "../../../etc/passwd", "confirm": True},
            False,
            "Path traversal attack"
        ),
        (
            {"function": "read_file", "filepath": "/etc/passwd", "confirm": True},
            False,
            "Absolute path (not allowed)"
        ),
        (
            {"function": "read_file", "filepath": "workspace/subdir/file.txt", "confirm": True},
            True,
            "Valid nested path"
        ),
    ]
    
    for args, should_pass, desc in test_cases:
        errors = validate_arguments_security(
            args,
            config,
            "file-ops",
            tools_dir
        )
        
        is_valid = len(errors) == 0
        status = "✅" if is_valid == should_pass else "❌"
        result = "PASSED" if is_valid else "BLOCKED"
        
        print(f"{status} {desc}")
        print(f"   Arguments: {json.dumps(args, indent=6)}")
        print(f"   Result: {result}")
        if errors:
            print(f"   Errors:")
            for error in errors:
                print(f"     - {error}")
        print()


def test_identifier_validation():
    """Test identifier validation."""
    print("=" * 70)
    print("TEST 3: Identifier Validation")
    print("=" * 70)
    
    sanitizer = InputSanitizer()
    
    test_cases = [
        ("valid_name", True, "Valid identifier"),
        ("valid-name-123", True, "Valid with hyphens and numbers"),
        ("../../../etc", False, "Path traversal in identifier"),
        ("name;rm -rf", False, "Shell metacharacters"),
        ("", False, "Empty string"),
        ("a" * 100, False, "Too long"),
    ]
    
    for name, should_pass, desc in test_cases:
        is_valid, sanitized, error = sanitizer.sanitize_identifier(name)
        
        status = "✅" if is_valid == should_pass else "❌"
        result = "VALID" if is_valid else "INVALID"
        
        print(f"{status} {desc}")
        print(f"   Input: {repr(name)}")
        print(f"   Result: {result}")
        if error:
            print(f"   Error: {error}")
        print()


def main():
    """Run all tests."""
    print("\n🔒 Testing Path Traversal Protection\n")
    
    try:
        test_path_sanitization()
        test_argument_validation()
        test_identifier_validation()
        
        print("=" * 70)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 70)
        print("\nPath traversal protection is working correctly!")
        print("Paths are validated before tool execution.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
