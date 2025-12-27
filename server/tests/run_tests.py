#!/usr/bin/env python3
"""
Test runner for all Local MCP Server tests.
Runs all test suites and provides a comprehensive report.
"""

import sys
import subprocess
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# Test categories with their descriptions
UNITTEST_TESTS = [
    ("test_argument_building.py", "Argument Building Logic"),
    ("test_tool_execution.py", "Tool Execution System"),
    ("test_fire_argparse_integration.py", "Fire/Argparse Compatibility"),
]

STANDALONE_TESTS = [
    ("test_audit_logging.py", "Audit Logging System"),
    ("test_error_sanitization.py", "Error Sanitization"),
    ("test_mcp_upgrade.py", "MCP 1.25.0 Protocol Features"),
    ("test_param_validation.py", "Parameter Validation"),
    ("test_path_traversal.py", "Path Traversal Protection"),
    ("test_redaction.py", "Sensitive Data Redaction"),
    ("test_resource_limits.py", "Resource Limits & Rate Limiting"),
    ("test_temp_cleanup.py", "Temporary File Cleanup"),
]


def run_unittest_suite():
    """Run unittest-based tests."""
    import unittest
    
    print("\n" + "=" * 80)
    print("🧪 UNITTEST SUITE")
    print("=" * 80)
    
    from test_argument_building import TestArgumentBuilding
    from test_tool_execution import TestToolExecution
    from test_fire_argparse_integration import TestFireVsArgparseIntegration
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestArgumentBuilding))
    suite.addTests(loader.loadTestsFromTestCase(TestToolExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestFireVsArgparseIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.testsRun, len(result.failures), len(result.errors)


def run_standalone_tests():
    """Run standalone test scripts."""
    print("\n" + "=" * 80)
    print("🔬 STANDALONE TESTS")
    print("=" * 80)
    
    results = []
    tests_dir = Path(__file__).parent
    
    for test_file, description in STANDALONE_TESTS:
        test_path = tests_dir / test_file
        print(f"\n▶️  Running: {description} ({test_file})")
        print("-" * 80)
        
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=False,
            cwd=tests_dir.parent
        )
        
        results.append((test_file, description, result.returncode == 0))
        
    return results


def print_summary(unittest_results, standalone_results):
    """Print comprehensive test summary."""
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print("=" * 80)
    
    # Unittest summary
    total_tests, failures, errors = unittest_results
    success_count = total_tests - failures - errors
    
    print("\n🧪 Unittest Suite:")
    print(f"  Total: {total_tests} | ✅ Passed: {success_count} | ❌ Failed: {failures} | 💥 Errors: {errors}")
    
    # Standalone tests summary
    print("\n🔬 Standalone Tests:")
    passed = sum(1 for _, _, success in standalone_results if success)
    failed = len(standalone_results) - passed
    
    for test_file, description, success in standalone_results:
        status = "✅" if success else "❌"
        print(f"  {status} {description}")
    
    print(f"\n  Total: {len(standalone_results)} | ✅ Passed: {passed} | ❌ Failed: {failed}")
    
    # Overall summary
    total_all = total_tests + len(standalone_results)
    passed_all = success_count + passed
    failed_all = (failures + errors) + failed
    
    print("\n" + "=" * 80)
    print(f"🎯 OVERALL: {passed_all}/{total_all} tests passed")
    
    if failed_all == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("✨ Local MCP Server is working perfectly!")
    else:
        print(f"\n⚠️  {failed_all} test(s) failed - see details above")
    
    print("=" * 80)
    
    return failed_all == 0


def run_all_tests():
    """Run all test suites and report results."""
    print("🚀 Local MCP Server Comprehensive Test Suite")
    print("=" * 80)
    print("Testing all system components:")
    print("  • Universal argument system (Fire & argparse)")
    print("  • Security features (validation, sanitization, limits)")
    print("  • MCP protocol compliance (1.25.0)")
    print("  • Tool execution and monitoring")
    print("=" * 80)
    
    # Run all tests
    unittest_results = run_unittest_suite()
    standalone_results = run_standalone_tests()
    
    # Print summary
    success = print_summary(unittest_results, standalone_results)
    
    return success


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)