#!/usr/bin/env python3
"""
Test runner for all Local MCP Server tests.
Runs all test suites and provides a comprehensive report.
"""

import sys
import unittest
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from test_argument_building import TestArgumentBuilding
from test_tool_execution import TestToolExecution
from test_fire_argparse_integration import TestFireVsArgparseIntegration


def run_all_tests():
    """Run all test suites and report results."""
    print("🚀 Local MCP Server Test Suite")
    print("=" * 80)
    print("Testing universal argument system compatibility with Fire and argparse tools")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestArgumentBuilding))
    suite.addTests(loader.loadTestsFromTestCase(TestToolExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestFireVsArgparseIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_count = total_tests - failures - errors
    
    print(f"Total Tests Run: {total_tests}")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failures: {failures}")
    print(f"💥 Errors: {errors}")
    
    if failures == 0 and errors == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✨ Universal argument system working perfectly!")
        print("🔥 Both Python Fire and argparse tools are fully compatible!")
    else:
        print(f"\n⚠️  {failures + errors} test(s) failed")
        if failures > 0:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}")
        if errors > 0:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('\n')[-2]}")
    
    print("=" * 80)
    
    # Return success status
    return failures == 0 and errors == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)