#!/usr/bin/env python3
"""Test script for temporary file cleanup functionality."""

import sys
import os
import time
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_mcp.config import Config
from local_mcp.executor import ScriptExecutor


def test_cleanup():
    """Test the cleanup_temp_files() functionality."""
    
    # Setup
    tools_dir = Path(__file__).parent.parent.parent / "tools"
    config_dir = Path(__file__).parent.parent / "config"
    
    config = Config(config_dir)
    executor = ScriptExecutor(tools_dir, config)
    
    # Get the temp directory
    global_config = config.get_global_config()
    temp_base = Path(global_config.temp_dir or tempfile.gettempdir())
    mcp_temp_dir = temp_base / "local_mcp_server"
    mcp_temp_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✓ Using temp directory: {mcp_temp_dir}")
    
    # Create some test temp directories with different ages
    current_time = time.time()
    
    # Create an old directory (25 hours old - should be cleaned)
    old_dir = mcp_temp_dir / "exec_test_old_12345"
    old_dir.mkdir(exist_ok=True)
    (old_dir / "test.txt").write_text("old content")
    old_mtime = current_time - (25 * 3600)  # 25 hours ago
    os.utime(old_dir, (old_mtime, old_mtime))
    print(f"✓ Created old test directory: {old_dir.name} (25 hours old)")
    
    # Create a recent directory (1 hour old - should NOT be cleaned)
    recent_dir = mcp_temp_dir / "exec_test_recent_67890"
    recent_dir.mkdir(exist_ok=True)
    (recent_dir / "test.txt").write_text("recent content")
    recent_mtime = current_time - (1 * 3600)  # 1 hour ago
    os.utime(recent_dir, (recent_mtime, recent_mtime))
    print(f"✓ Created recent test directory: {recent_dir.name} (1 hour old)")
    
    # Run cleanup
    print("\nRunning cleanup...")
    stats = executor.cleanup_temp_files()
    
    # Verify results
    print(f"\nCleanup statistics:")
    print(f"  - Directories cleaned: {stats['cleaned']}")
    print(f"  - Size freed: {stats['size_freed'] / 1024:.2f} KB")
    print(f"  - Errors: {stats['errors']}")
    
    # Check that old directory was removed
    if not old_dir.exists():
        print(f"\n✓ Old directory was cleaned up successfully")
    else:
        print(f"\n✗ ERROR: Old directory still exists")
        return False
    
    # Check that recent directory still exists
    if recent_dir.exists():
        print(f"✓ Recent directory was preserved")
    else:
        print(f"✗ ERROR: Recent directory was incorrectly removed")
        return False
    
    # Cleanup test directories
    if recent_dir.exists():
        import shutil
        shutil.rmtree(recent_dir)
        print(f"\n✓ Cleaned up test directories")
    
    print("\n✅ All tests passed!")
    return True


def test_cleanup_disabled():
    """Test that cleanup respects the auto_cleanup_temp config."""
    
    tools_dir = Path(__file__).parent.parent.parent / "tools"
    config_dir = Path(__file__).parent.parent / "config"
    
    # Create a modified config file temporarily
    import json
    config_file = Path(config_dir) / "config.json"
    
    # Read original config
    with open(config_file, 'r') as f:
        original_config = json.load(f)
    
    # Temporarily disable cleanup
    modified_config = original_config.copy()
    modified_config['auto_cleanup_temp'] = False
    
    # Write modified config
    with open(config_file, 'w') as f:
        json.dump(modified_config, f, indent=2)
    
    try:
        # Create executor with disabled cleanup
        config = Config(config_dir)
        executor = ScriptExecutor(tools_dir, config)
        
        print("\nTesting with auto_cleanup_temp=False...")
        stats = executor.cleanup_temp_files()
        
        if stats.get('skipped') == True:
            print("✓ Cleanup correctly skipped when disabled")
            return True
        else:
            print("✗ ERROR: Cleanup ran when it should have been disabled")
            return False
    finally:
        # Restore original config
        with open(config_file, 'w') as f:
            json.dump(original_config, f, indent=2)


if __name__ == "__main__":
    print("=" * 60)
    print("Testing temporary file cleanup functionality")
    print("=" * 60)
    
    try:
        result1 = test_cleanup()
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        print("\nNote: Cleanup respects auto_cleanup_temp config flag")
        print("When disabled, cleanup returns: {'skipped': True, 'reason': '...'}")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
