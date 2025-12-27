#!/usr/bin/env python3
"""Test @param parsing and validation."""

import json
import asyncio
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from local_mcp.config import Config
from local_mcp.discovery import ScriptDiscovery
from local_mcp.utils import validate_script_arguments


async def test_param_parsing():
    """Test that @param annotations are parsed correctly."""
    print("=" * 60)
    print("TEST 1: @param Parsing")
    print("=" * 60)
    
    config = Config(Path(__file__).parent / "config")
    discovery = ScriptDiscovery(
        tools_dir=Path(__file__).parent.parent / "tools",
        config=config
    )
    
    # Discover tools - need to discover first
    await discovery.discover_scripts(force_full=True)
    tools = await discovery.get_available_tools()
    
    print(f"\n✅ Discovered {len(tools)} tools\n")
    
    # Check file-ops tool
    file_ops = next((t for t in tools if t.name == "file-ops"), None)
    if file_ops:
        print(f"📋 file-ops inputSchema:")
        print(json.dumps(file_ops.inputSchema, indent=2))
        
        # Check if required params are present
        if "function" in file_ops.inputSchema.get("properties", {}):
            print("\n✅ 'function' parameter found")
            if "function" in file_ops.inputSchema.get("required", []):
                print("✅ 'function' is marked as required")
        else:
            print("\n❌ 'function' parameter NOT found")
    else:
        print("❌ file-ops tool not found")
    
    return file_ops


async def test_validation():
    """Test that validation works correctly."""
    print("\n" + "=" * 60)
    print("TEST 2: Parameter Validation")
    print("=" * 60)
    
    file_ops = await test_param_parsing()
    
    if not file_ops:
        print("❌ Cannot test validation without file-ops tool")
        return
    
    # Test 1: Missing required parameter
    print("\n📝 Test: Missing required 'function' parameter")
    args = {"filepath": "/tmp/test.txt"}
    errors = validate_script_arguments(args, file_ops.inputSchema)
    
    if errors:
        print(f"✅ Validation correctly caught errors:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("❌ Validation should have caught missing 'function'")
    
    # Test 2: Valid arguments
    print("\n📝 Test: Valid arguments")
    args = {"function": "read_file", "filepath": "/tmp/test.txt"}
    errors = validate_script_arguments(args, file_ops.inputSchema)
    
    if not errors:
        print("✅ Validation passed for valid arguments")
    else:
        print(f"❌ Validation incorrectly reported errors:")
        for error in errors:
            print(f"   - {error}")
    
    # Test 3: Wrong type
    print("\n📝 Test: Wrong type (integer instead of string)")
    args = {"function": 123}  # Should be string
    errors = validate_script_arguments(args, file_ops.inputSchema)
    
    if errors:
        print(f"✅ Validation correctly caught type error:")
        for error in errors:
            print(f"   - {error}")
    else:
        print("❌ Validation should have caught type mismatch")


async def main():
    """Run all tests."""
    print("\n🧪 Testing @param Parsing and Validation\n")
    
    try:
        await test_validation()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
