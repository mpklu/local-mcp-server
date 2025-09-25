#!/usr/bin/env python3
"""
Test suite for argument building and tool execution functionality.
Tests both Python Fire and argparse-based tools.
"""

import asyncio
import sys
import unittest
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_mcp.config import Config
from local_mcp.executor import ScriptExecutor


class TestToolExecution(unittest.TestCase):
    """Test tool execution with both Fire and argparse."""

    def setUp(self):
        """Set up test environment."""
        self.tools_dir = Path(__file__).parent.parent.parent / "tools"
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config = Config(self.config_dir)
        self.executor = ScriptExecutor(self.tools_dir, self.config)

    def test_fire_tool_list_files(self):
        """Test Python Fire tool - file-ops list_files function."""
        async def run_test():
            arguments = {
                'confirm': True,
                'function': 'list_files',
                'directory': '.'
            }
            
            result = await self.executor.execute_script('file-ops', arguments)
            
            # Verify JSON response structure
            self.assertIn('"directory"', result)
            self.assertIn('"files"', result)
            self.assertIn('"total_items"', result)
            return result

        result = asyncio.run(run_test())
        print(f"✅ Fire list_files test passed: {len(result)} chars returned")

    def test_fire_tool_read_file(self):
        """Test Python Fire tool - file-ops read_file function."""
        async def run_test():
            # Use absolute path to README.md
            readme_path = str((self.tools_dir.parent / "README.md").resolve())
            
            arguments = {
                'confirm': True,
                'function': 'read_file',
                'file_path': readme_path,
                'lines': 3
            }
            
            result = await self.executor.execute_script('file-ops', arguments)
            
            # Verify JSON response structure
            self.assertIn('"file_path"', result)
            self.assertIn('"content"', result)
            self.assertIn('"lines_requested"', result)
            return result

        result = asyncio.run(run_test())
        print(f"✅ Fire read_file test passed: {len(result)} chars returned")

    def test_fire_tool_text_utils(self):
        """Test Python Fire tool - text-utils word_count function."""
        async def run_test():
            arguments = {
                'confirm': True,
                'function': 'word_count',
                'text': 'Hello world! This is a test text for counting words and characters.'
            }
            
            result = await self.executor.execute_script('text-utils', arguments)
            
            # Verify JSON response structure
            self.assertIn('"statistics"', result)
            self.assertIn('"word_frequency"', result)
            self.assertIn('"words"', result)
            return result

        result = asyncio.run(run_test())
        print(f"✅ Fire word_count test passed: {len(result)} chars returned")

    def test_fire_tool_http_client(self):
        """Test Python Fire tool - http-client get_url function."""
        async def run_test():
            arguments = {
                'confirm': True,
                'function': 'get_url',
                'url': 'https://httpbin.org/get',
                'timeout': 10
            }
            
            result = await self.executor.execute_script('http-client', arguments)
            
            # Verify JSON response structure (should work even if request fails)
            self.assertIn('"request"', result)
            self.assertIn('"response"', result)
            return result

        result = asyncio.run(run_test())
        print(f"✅ Fire http_client test passed: {len(result)} chars returned")

    def test_argparse_tool_system_info(self):
        """Test argparse tool - system-info get_system_info function."""
        async def run_test():
            arguments = {
                'confirm': True,
                'function': 'get_system_info'
            }
            
            result = await self.executor.execute_script('system-info', arguments)
            
            # Verify JSON response structure
            self.assertIn('"timestamp"', result)
            self.assertIn('"system"', result)
            self.assertIn('"cpu"', result)
            self.assertIn('"memory"', result)
            return result

        result = asyncio.run(run_test())
        print(f"✅ Argparse get_system_info test passed: {len(result)} chars returned")

    def test_argparse_tool_disk_usage(self):
        """Test argparse tool - system-info get_disk_usage function with parameter."""
        async def run_test():
            arguments = {
                'confirm': True,
                'function': 'get_disk_usage',
                'path': '/Users'
            }
            
            result = await self.executor.execute_script('system-info', arguments)
            
            # Verify JSON response structure
            self.assertIn('"path"', result)
            self.assertIn('"total_gb"', result)
            self.assertIn('"used_gb"', result)
            self.assertIn('"free_gb"', result)
            return result

        result = asyncio.run(run_test())
        print(f"✅ Argparse get_disk_usage test passed: {len(result)} chars returned")

    def test_argparse_tool_network_info(self):
        """Test argparse tool - system-info get_network_info function."""
        async def run_test():
            arguments = {
                'confirm': True,
                'function': 'get_network_info'
            }
            
            result = await self.executor.execute_script('system-info', arguments)
            
            # Verify JSON response structure
            self.assertIn('"interfaces"', result)
            self.assertIn('"statistics"', result)
            return result

        result = asyncio.run(run_test())
        print(f"✅ Argparse get_network_info test passed: {len(result)} chars returned")

    def test_argument_format_compatibility(self):
        """Test that both Fire and argparse tools work with the same argument format."""
        async def run_test():
            # Test Fire tool
            fire_args = {
                'confirm': True,
                'function': 'list_files',
                'directory': '.'
            }
            
            fire_result = await self.executor.execute_script('file-ops', fire_args)
            fire_success = '"directory"' in fire_result and '"files"' in fire_result
            
            # Test argparse tool
            argparse_args = {
                'confirm': True,
                'function': 'get_system_info'
            }
            
            argparse_result = await self.executor.execute_script('system-info', argparse_args)
            argparse_success = '"timestamp"' in argparse_result and '"system"' in argparse_result
            
            return fire_success, argparse_success

        fire_success, argparse_success = asyncio.run(run_test())
        
        self.assertTrue(fire_success, "Fire tool should work with function parameter")
        self.assertTrue(argparse_success, "Argparse tool should work with function parameter")
        print("✅ Both Fire and argparse tools work with the same argument format!")


if __name__ == '__main__':
    print("Running Tool Execution Tests...")
    print("=" * 50)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 50)
    print("🎉 All tool execution tests completed!")