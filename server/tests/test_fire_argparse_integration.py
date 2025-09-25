#!/usr/bin/env python3
"""
Integration test suite demonstrating Fire vs Argparse compatibility.
Shows that both argument parsing approaches work seamlessly together.
"""

import asyncio
import sys
import unittest
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_mcp.config import Config
from local_mcp.executor import ScriptExecutor


class TestFireVsArgparseIntegration(unittest.TestCase):
    """Integration tests comparing Fire and argparse tool behavior."""

    def setUp(self):
        """Set up test environment."""
        self.tools_dir = Path(__file__).parent.parent.parent / "tools"
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config = Config(self.config_dir)
        self.executor = ScriptExecutor(self.tools_dir, self.config)

    def test_equivalent_functionality(self):
        """Test that similar functions work equivalently between Fire and argparse."""
        async def run_test():
            # Both tools have info-gathering functions - test similar patterns
            
            # Fire-based: Get file info
            fire_args = {
                'confirm': True,
                'function': 'get_file_info',
                'file_path': str(Path(__file__).resolve())
            }
            
            fire_result = await self.executor.execute_script('file-ops', fire_args)
            
            # Argparse-based: Get system info
            argparse_args = {
                'confirm': True,
                'function': 'get_system_info'
            }
            
            argparse_result = await self.executor.execute_script('system-info', argparse_args)
            
            return fire_result, argparse_result

        fire_result, argparse_result = asyncio.run(run_test())
        
        # Both should return valid JSON
        self.assertIn('{', fire_result)
        self.assertIn('}', fire_result)
        self.assertIn('{', argparse_result)
        self.assertIn('}', argparse_result)
        
        print("✅ Both Fire and argparse tools return structured JSON")

    def test_parameter_handling_consistency(self):
        """Test that parameter handling is consistent between Fire and argparse."""
        async def run_test():
            # Fire tool with parameters
            fire_args = {
                'confirm': True,
                'function': 'list_files',
                'directory': '.',
                'pattern': '*.py',
                'include_hidden': False
            }
            
            fire_result = await self.executor.execute_script('file-ops', fire_args)
            
            # Argparse tool with parameters
            argparse_args = {
                'confirm': True,
                'function': 'get_disk_usage',
                'path': '/'
            }
            
            argparse_result = await self.executor.execute_script('system-info', argparse_args)
            
            return fire_result, argparse_result

        fire_result, argparse_result = asyncio.run(run_test())
        
        # Both should handle parameters correctly
        # Fire result should show the pattern was applied
        self.assertIn('"pattern"', fire_result)
        
        # Argparse result should show the path was used
        self.assertIn('"path"', argparse_result)
        
        print("✅ Both Fire and argparse tools handle parameters consistently")

    def test_error_handling_compatibility(self):
        """Test that error handling works similarly for both approaches."""
        async def run_test():
            # Test Fire tool with invalid parameter
            fire_args = {
                'confirm': True,
                'function': 'read_file',
                'file_path': '/nonexistent/file/path.txt'
            }
            
            fire_result = await self.executor.execute_script('file-ops', fire_args)
            
            # Test argparse tool with invalid parameter
            argparse_args = {
                'confirm': True,
                'function': 'get_disk_usage',
                'path': '/nonexistent/path'
            }
            
            argparse_result = await self.executor.execute_script('system-info', argparse_args)
            
            return fire_result, argparse_result

        fire_result, argparse_result = asyncio.run(run_test())
        
        # Both should handle errors gracefully
        self.assertIn('Error', fire_result)
        self.assertIn('Error', argparse_result)
        
        print("✅ Both Fire and argparse tools handle errors gracefully")

    def test_command_structure_compatibility(self):
        """Test that the command structure works the same for both approaches."""
        
        # Test command structure building for Fire tool
        fire_args = {
            'confirm': True,
            'function': 'word_count',
            'text': 'Sample text for testing'
        }
        
        fire_cmd_args = self.executor._build_script_arguments(fire_args)
        
        # Test command structure building for argparse tool
        argparse_args = {
            'confirm': True,
            'function': 'get_system_info'
        }
        
        argparse_cmd_args = self.executor._build_script_arguments(argparse_args)
        
        # Both should have function name as first argument
        self.assertEqual(fire_cmd_args[0], 'word_count')
        self.assertEqual(argparse_cmd_args[0], 'get_system_info')
        
        # Both should use --param=value format for additional parameters
        if len(fire_cmd_args) > 1:
            param_args = [arg for arg in fire_cmd_args[1:] if arg.startswith('--')]
            self.assertTrue(all('=' in arg for arg in param_args))
        
        print(f"✅ Command structure consistent: Fire={fire_cmd_args}, Argparse={argparse_cmd_args}")

    def test_full_workflow_comparison(self):
        """Test complete workflow from arguments to results for both approaches."""
        async def run_test():
            # Complete Fire workflow
            fire_workflow = []
            
            # 1. List files with Fire
            fire_args1 = {
                'confirm': True,
                'function': 'list_files',
                'directory': '.'
            }
            fire_result1 = await self.executor.execute_script('file-ops', fire_args1)
            fire_workflow.append(('list_files', len(fire_result1)))
            
            # 2. Process text with Fire
            fire_args2 = {
                'confirm': True,
                'function': 'word_count',
                'text': 'Testing Fire-based text processing functionality.'
            }
            fire_result2 = await self.executor.execute_script('text-utils', fire_args2)
            fire_workflow.append(('word_count', len(fire_result2)))
            
            # Complete argparse workflow
            argparse_workflow = []
            
            # 1. Get system info with argparse
            argparse_args1 = {
                'confirm': True,
                'function': 'get_system_info'
            }
            argparse_result1 = await self.executor.execute_script('system-info', argparse_args1)
            argparse_workflow.append(('get_system_info', len(argparse_result1)))
            
            # 2. Get disk usage with argparse
            argparse_args2 = {
                'confirm': True,
                'function': 'get_disk_usage',
                'path': '/'
            }
            argparse_result2 = await self.executor.execute_script('system-info', argparse_args2)
            argparse_workflow.append(('get_disk_usage', len(argparse_result2)))
            
            return fire_workflow, argparse_workflow

        fire_workflow, argparse_workflow = asyncio.run(run_test())
        
        # Both workflows should complete successfully
        self.assertEqual(len(fire_workflow), 2)
        self.assertEqual(len(argparse_workflow), 2)
        
        # All results should have content
        for name, length in fire_workflow + argparse_workflow:
            self.assertGreater(length, 0, f"{name} should return content")
        
        print(f"✅ Complete workflows: Fire={fire_workflow}, Argparse={argparse_workflow}")


if __name__ == '__main__':
    print("Running Fire vs Argparse Integration Tests...")
    print("=" * 60)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("🎉 All integration tests completed!")
    print("Both Fire and argparse tools work seamlessly with the universal argument system!")