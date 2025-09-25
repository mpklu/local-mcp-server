#!/usr/bin/env python3
"""
Test suite for argument building logic.
Tests the _build_script_arguments method with various argument patterns.
"""

import sys
import unittest
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_mcp.config import Config
from local_mcp.executor import ScriptExecutor


class TestArgumentBuilding(unittest.TestCase):
    """Test the argument building logic for different parameter patterns."""

    def setUp(self):
        """Set up test environment."""
        self.tools_dir = Path(__file__).parent.parent.parent / "tools"
        self.config_dir = Path(__file__).parent.parent / "config"
        self.config = Config(self.config_dir)
        self.executor = ScriptExecutor(self.tools_dir, self.config)

    def test_function_parameter_extraction(self):
        """Test that function parameter is correctly extracted and used."""
        arguments = {
            'confirm': True,
            'function': 'test_function',
            'param1': 'value1',
            'param2': 'value2'
        }
        
        result_args = self.executor._build_script_arguments(arguments)
        
        # Function name should be first argument
        self.assertEqual(result_args[0], 'test_function')
        
        # Parameters should be in --param=value format
        self.assertIn('--param1=value1', result_args)
        self.assertIn('--param2=value2', result_args)
        
        # confirm should be filtered out
        confirm_args = [arg for arg in result_args if 'confirm' in arg]
        self.assertEqual(len(confirm_args), 0)
        
        print(f"✅ Function parameter extraction: {result_args}")

    def test_command_parameter_extraction(self):
        """Test that 'command' parameter works as alias for 'function'."""
        arguments = {
            'confirm': True,
            'command': 'test_command',
            'param1': 'value1'
        }
        
        result_args = self.executor._build_script_arguments(arguments)
        
        # Command name should be first argument
        self.assertEqual(result_args[0], 'test_command')
        self.assertIn('--param1=value1', result_args)
        
        print(f"✅ Command parameter extraction: {result_args}")

    def test_function_over_command_priority(self):
        """Test that 'function' takes priority over 'command' when both present."""
        arguments = {
            'confirm': True,
            'function': 'priority_function',
            'command': 'ignored_command',
            'param1': 'value1'
        }
        
        result_args = self.executor._build_script_arguments(arguments)
        
        # Function should take priority
        self.assertEqual(result_args[0], 'priority_function')
        self.assertNotIn('ignored_command', result_args)
        
        print(f"✅ Function priority test: {result_args}")

    def test_no_function_parameter(self):
        """Test behavior when no function/command parameter is provided."""
        arguments = {
            'confirm': True,
            'param1': 'value1',
            'param2': 'value2'
        }
        
        result_args = self.executor._build_script_arguments(arguments)
        
        # No function name should be added
        # First argument should be a parameter
        self.assertTrue(result_args[0].startswith('--'))
        self.assertIn('--param1=value1', result_args)
        self.assertIn('--param2=value2', result_args)
        
        print(f"✅ No function parameter test: {result_args}")

    def test_special_parameter_formats(self):
        """Test handling of parameters that already have -- prefix."""
        arguments = {
            'confirm': True,
            'function': 'test_function',
            '--existing-prefix': 'value1',
            'normal_param': 'value2',
            'a': 'single_char'  # Single character parameter
        }
        
        result_args = self.executor._build_script_arguments(arguments)
        
        # Check different parameter formats
        self.assertIn('--existing-prefix=value1', result_args)
        self.assertIn('--normal_param=value2', result_args)
        self.assertIn('-a', result_args)
        self.assertIn('single_char', result_args)
        
        print(f"✅ Special parameter formats: {result_args}")

    def test_complex_values(self):
        """Test handling of complex parameter values."""
        arguments = {
            'confirm': True,
            'function': 'test_function',
            'text': 'Hello world! This is a test with spaces and punctuation.',
            'path': '/Users/test/path with spaces',
            'number': 42,
            'boolean': True
        }
        
        result_args = self.executor._build_script_arguments(arguments)
        
        # All values should be converted to strings and properly formatted
        text_arg = '--text=Hello world! This is a test with spaces and punctuation.'
        path_arg = '--path=/Users/test/path with spaces'
        number_arg = '--number=42'
        boolean_arg = '--boolean=True'
        
        self.assertIn(text_arg, result_args)
        self.assertIn(path_arg, result_args)
        self.assertIn(number_arg, result_args)
        self.assertIn(boolean_arg, result_args)
        
        print(f"✅ Complex values test: {result_args}")

    def test_filtered_arguments(self):
        """Test that MCP-specific arguments are properly filtered out."""
        arguments = {
            'confirm': True,
            'function': 'test_function',
            'command': 'test_command',  # Should be filtered since function takes priority
            'normal_param': 'value1',
            'another_param': 'value2'
        }
        
        result_args = self.executor._build_script_arguments(arguments)
        
        # MCP-specific arguments should not appear in result
        filtered_items = ['confirm', 'command']
        for item in filtered_items:
            confirm_args = [arg for arg in result_args if item in arg]
            # command might appear as part of function name, but not as separate parameter
            if item == 'command':
                separate_command_args = [arg for arg in result_args if arg == 'test_command' or arg.startswith('--command=')]
                self.assertEqual(len(separate_command_args), 0)
            else:
                self.assertEqual(len(confirm_args), 0, f"{item} should be filtered out")
        
        print(f"✅ Filtered arguments test: {result_args}")


if __name__ == '__main__':
    print("Running Argument Building Tests...")
    print("=" * 50)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 50)
    print("🎉 All argument building tests completed!")