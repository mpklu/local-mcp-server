# Local MCP Server Tests

This directory contains comprehensive tests for the Local MCP Server, focusing on the universal argument system that supports both Python Fire and argparse-based tools.

## Test Files

### `test_argument_building.py`
Tests the core argument building logic in `ScriptExecutor._build_script_arguments()`:
- Function parameter extraction and priority handling
- Parameter format conversion (`--param=value`)
- Filtering of MCP-specific arguments (`confirm`, `function`, `command`)
- Handling of complex parameter values and special formats

### `test_tool_execution.py`
Tests actual tool execution with both Fire and argparse tools:
- **Fire Tools**: `file-ops`, `text-utils`, `http-client`
- **Argparse Tools**: `system-info`
- Verifies JSON response structures and functionality
- Tests end-to-end execution with virtual environments

### `test_fire_argparse_integration.py`
Integration tests demonstrating compatibility between Fire and argparse:
- Equivalent functionality testing
- Parameter handling consistency
- Error handling compatibility
- Command structure verification
- Complete workflow comparisons

### `run_tests.py`
Test runner that executes all test suites and provides comprehensive reporting.

## Running Tests

### Run All Tests
```bash
cd server/tests
python run_tests.py
```

### Run Individual Test Suites
```bash
cd server/tests
python test_argument_building.py
python test_tool_execution.py
python test_fire_argparse_integration.py
```

### Run with UV (Recommended)
```bash
cd server
uv run python tests/run_tests.py
```

## Test Coverage

The test suite covers:

✅ **Argument Building Logic**
- Function parameter extraction (`function` vs `command`)
- Parameter format conversion to `--param=value`
- MCP argument filtering
- Complex value handling

✅ **Tool Execution**
- Python Fire tools: `list_files`, `read_file`, `word_count`, `get_url`
- Argparse tools: `get_system_info`, `get_disk_usage`, `get_network_info`
- Virtual environment isolation
- JSON response validation

✅ **Cross-Library Compatibility**
- Same argument format works for both Fire and argparse
- Consistent error handling
- Equivalent command structure generation

## Key Validations

The tests verify that:

1. **Universal Argument Format**: Both Fire and argparse tools accept the same argument structure:
   ```python
   {
       "confirm": True,
       "function": "command_name",
       "param1": "value1",
       "param2": "value2"
   }
   ```

2. **Command Generation**: Both libraries receive properly formatted commands:
   ```bash
   # Fire tool
   python run.py list_files --directory=. --pattern=*.py
   
   # Argparse tool  
   python run.py get_system_info
   python run.py get_disk_usage --path=/Users
   ```

3. **Response Consistency**: All tools return structured JSON responses with error handling.

## Expected Output

When all tests pass, you should see:
```
🎉 ALL TESTS PASSED!
✨ Universal argument system working perfectly!
🔥 Both Python Fire and argparse tools are fully compatible!
```

This confirms that the MCP server's argument building fix works universally for both Python Fire and argparse-based tools.