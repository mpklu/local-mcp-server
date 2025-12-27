# Local MCP Server Tests

This directory contains comprehensive tests for the Local MCP Server, covering all major system components including argument handling, security features, MCP protocol compliance, and tool execution.

## Test Files

### Core Functionality Tests

#### `test_argument_building.py`
Tests the core argument building logic in `ScriptExecutor._build_script_arguments()`:
- Function parameter extraction and priority handling
- Parameter format conversion (`--param=value`)
- Filtering of MCP-specific arguments (`confirm`, `function`, `command`)
- Handling of complex parameter values and special formats

#### `test_tool_execution.py`
Tests actual tool execution with both Fire and argparse tools:
- **Fire Tools**: `file-ops`, `text-utils`, `http-client`
- **Argparse Tools**: `system-info`
- Verifies JSON response structures and functionality
- Tests end-to-end execution with virtual environments

#### `test_fire_argparse_integration.py`
Integration tests demonstrating compatibility between Fire and argparse:
- Equivalent functionality testing
- Parameter handling consistency
- Error handling compatibility
- Command structure verification
- Complete workflow comparisons

### Security Tests

#### `test_path_traversal.py`
Tests path traversal protection mechanisms:
- Parent directory reference blocking (`../`)
- Absolute path restrictions
- Symbolic link validation
- Workspace boundary enforcement
- Multi-layer validation testing

#### `test_redaction.py`
Tests sensitive data redaction system:
- Keyword-based redaction (passwords, tokens, secrets)
- Pattern-based detection (credit cards, SSNs, API keys)
- AWS credentials, GitHub/GitLab tokens, JWT tokens
- Configurable redaction scope (arguments, outputs, both)
- Full vs hint-style redaction modes

#### `test_error_sanitization.py`
Tests the SafeErrorFormatter for secure error messages:
- Filesystem path removal from errors
- Stack trace sanitization
- Module path redaction
- Safe error types for different exception classes
- Configuration file path protection

#### `test_resource_limits.py`
Tests resource limit enforcement:
- CPU time limits (Unix/Linux/macOS only)
- Memory limits (virtual memory caps)
- Process count limits
- Concurrent execution limits (max simultaneous tools)
- Rate limiting (sliding window per-tool limits)

#### `test_param_validation.py`
Tests parameter validation system:
- Required parameter enforcement
- Type validation (string, int, bool)
- Format validation (email, URL patterns)
- Range validation (min/max values)
- Custom validation rules

#### `test_audit_logging.py`
Tests comprehensive audit logging:
- Tool execution lifecycle events (start, end, error)
- Request correlation with UUID tracking
- Structured JSON log format
- Log rotation and retention
- Sensitive data redaction in logs

### Protocol & Features Tests

#### `test_mcp_upgrade.py`
Tests MCP 1.25.0 protocol features:
- Tool title fields for human-readable names
- Tool annotations (readOnly, destructive flags)
- Protocol version compliance
- Backward compatibility verification

#### `test_temp_cleanup.py`
Tests temporary file cleanup system:
- Time-based retention policy (default 24 hours)
- Automatic cleanup on server startup
- Statistics tracking (files removed, space freed)
- Configuration flag respect (`auto_cleanup_temp`)
- Age-based directory removal

### Test Runner

#### `run_tests.py`
Comprehensive test runner that executes all test suites:
- Runs unittest-based tests (argument building, tool execution, integration)
- Runs standalone test scripts (security, protocol, features)
- Provides detailed summary with pass/fail counts
- Returns proper exit codes for CI/CD integration

## Running Tests

### Run All Tests (Recommended)
```bash
cd server
uv run python tests/run_tests.py
```

This will run all unittest suites and standalone tests, providing a comprehensive report.

### Run Individual Test Categories

**Unittest Suite (Core Functionality):**
```bash
cd server/tests
python test_argument_building.py
python test_tool_execution.py
python test_fire_argparse_integration.py
```

**Security Tests:**
```bash
cd server/tests
python test_path_traversal.py
python test_redaction.py
python test_error_sanitization.py
python test_resource_limits.py
python test_param_validation.py
python test_audit_logging.py
```

**Protocol & Features:**
```bash
cd server/tests
python test_mcp_upgrade.py
python test_temp_cleanup.py
```

### Run with UV (Recommended for Isolation)
```bash
cd server
uv run python tests/test_argument_building.py
uv run python tests/test_path_traversal.py
# ... etc
```

## Test Coverage

The test suite provides comprehensive coverage of:

### ✅ Core Functionality
- **Argument Building**: Universal format for Fire and argparse tools
- **Tool Execution**: End-to-end execution with virtual environments
- **Cross-Library Compatibility**: Same argument structure works for both libraries

### ✅ Security Features
- **Input Validation**: Path traversal, parameter types, required fields
- **Data Protection**: Sensitive data redaction (30+ patterns)
- **Resource Limits**: CPU, memory, process, and concurrent execution limits
- **Rate Limiting**: Per-tool sliding window algorithm
- **Error Sanitization**: Safe error messages without sensitive paths

### ✅ Protocol Compliance
- **MCP 1.25.0**: Title fields and tool annotations
- **Tool Classification**: readOnly and destructive flags
- **Backward Compatibility**: Works with older MCP clients

### ✅ System Features
- **Audit Logging**: Structured JSON logs with request correlation
- **Temp File Management**: Automatic cleanup with configurable retention
- **Statistics Tracking**: Execution metrics and cleanup statistics

## Key Validations

The tests verify that:

### 1. Universal Argument Format
Both Fire and argparse tools accept the same argument structure:
```python
{
    "confirm": True,
    "function": "command_name",
    "param1": "value1",
    "param2": "value2"
}
```

### 2. Command Generation
Both libraries receive properly formatted commands:
```bash
# Fire tool
python run.py list_files --directory=. --pattern=*.py

# Argparse tool  
python run.py get_system_info
python run.py get_disk_usage --path=/Users
```

### 3. Security Enforcement
All security layers are active and properly enforced:
- Path traversal attempts are blocked
- Sensitive data is automatically redacted
- Resource limits prevent runaway processes
- Rate limiting prevents abuse
- Errors don't leak filesystem information

### 4. Protocol Compliance
MCP 1.25.0 features work correctly:
- Tool titles appear in AI interfaces
- Annotations (readOnly/destructive) are set correctly
- Protocol responses match specification

### 5. System Reliability
Core system features function properly:
- Temp files are cleaned up automatically
- Audit logs capture all security events
- Statistics tracking provides observability
- Configuration changes take effect

## Test Results

Expected behavior when all tests pass:
- **Unittest Suite**: All assertion-based tests pass
- **Security Tests**: All protection mechanisms work correctly
- **Protocol Tests**: MCP 1.25.0 compliance verified
- **Feature Tests**: Cleanup, logging, monitoring operational

Run `uv run python tests/run_tests.py` to verify your installation.

## Expected Output

When all tests pass, you should see:
```
🎉 ALL TESTS PASSED!
✨ Universal argument system working perfectly!
🔥 Both Python Fire and argparse tools are fully compatible!
```

This confirms that the MCP server's argument building fix works universally for both Python Fire and argparse-based tools.