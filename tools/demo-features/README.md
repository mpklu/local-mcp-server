# Web Interface Demo Features

This tool demonstrates advanced features of the Local MCP Server web interface including timeout handling, dependency management, confirmation workflows, and error recovery patterns.

## Usage Examples

### Long-running task simulation
```bash
# Test timeout handling with a 15-second task
python run.py long_running_task --duration=15 --report_interval=3
```

### Dependency management demo
```bash
# Check which packages are available vs missing
python run.py dependency_demo
```

### Interactive confirmation workflow
```bash
# Low-risk action (no confirmation)
python run.py interactive_demo --name="Alice" --danger_level="low"

# High-risk action (requires confirmation)
python run.py interactive_demo --name="Bob" --danger_level="high" --confirm=True
```

### Error handling demonstration
```bash
# Successful execution
python run.py error_handling_demo --error_type="none"

# Simulate different error types
python run.py error_handling_demo --error_type="value"
python run.py error_handling_demo --error_type="timeout"
```

### Configuration showcase
```bash
# Show all configuration patterns and capabilities
python run.py configuration_showcase
```

## Available Functions

### long_running_task(duration=10, report_interval=2)
- **Purpose**: Test timeout handling and progress monitoring
- **duration**: Task duration in seconds (max 60)
- **report_interval**: Progress report frequency in seconds
- **Demo Features**: Progress tracking, real-time monitoring, timeout handling

### dependency_demo()
- **Purpose**: Show dependency management capabilities
- **Demo Features**: Package detection, installation guidance, environment info
- **Tests**: Common packages like requests, pandas, numpy, matplotlib

### interactive_demo(name="Anonymous", confirm=True, danger_level="low")
- **Purpose**: Demonstrate confirmation workflows and user interaction
- **name**: User name for personalized messages
- **confirm**: Whether confirmation is required
- **danger_level**: Risk level - "low", "medium", "high"
- **Demo Features**: Confirmation dialogs, risk assessment, user validation

### error_handling_demo(error_type="none")
- **Purpose**: Show error handling and recovery patterns
- **error_type**: Error to simulate - "none", "value", "type", "runtime", "timeout"
- **Demo Features**: Exception catching, graceful degradation, structured error responses

### configuration_showcase()
- **Purpose**: Display configuration patterns and web interface capabilities
- **Demo Features**: Parameter types, validation patterns, execution monitoring

## Web Interface Features Demonstrated

### **Parameter Handling**
- **String Parameters**: Text input with validation
- **Numeric Parameters**: Range validation and type checking
- **Boolean Parameters**: Checkbox/toggle interfaces
- **Choice Parameters**: Dropdown selections
- **JSON Parameters**: Structured input with syntax validation

### **Execution Monitoring**
- **Progress Tracking**: Real-time progress bars for long operations
- **Timeout Management**: Configurable timeouts with user notifications
- **Status Updates**: Live feedback during tool execution
- **Result Formatting**: Structured output with syntax highlighting

### **Confirmation Workflows**
- **Risk Assessment**: Automatic risk level detection
- **Confirmation Dialogs**: User approval for medium/high-risk operations
- **Safety Warnings**: Clear risk descriptions and consequences
- **Multi-step Confirmations**: Enhanced protection for destructive operations

### **Dependency Management**
- **Automatic Detection**: Scan for missing tool dependencies
- **Installation Guidance**: Step-by-step installation instructions
- **Environment Validation**: Python environment compatibility checks
- **Real-time Validation**: Pre-execution dependency verification

### **Error Recovery**
- **Graceful Degradation**: System remains stable after errors
- **Structured Error Responses**: Clear error messages with context
- **Recovery Suggestions**: Actionable guidance for error resolution
- **Debug Information**: Detailed error context for troubleshooting

## Configuration Examples for Web Interface

Each function demonstrates different configuration patterns:

1. **Simple Configuration** (`configuration_showcase`)
   - No parameters required
   - Demonstrates basic tool setup

2. **Parameter Validation** (`interactive_demo`)
   - Multiple parameter types
   - Choice validation with predefined options
   - Boolean parameter handling

3. **Advanced Options** (`long_running_task`)
   - Numeric parameters with limits
   - Default value handling
   - Real-time parameter effects

4. **Error Simulation** (`error_handling_demo`)
   - Choice parameters for error types
   - Error handling demonstration
   - Recovery pattern showcase

## Dependencies

Install dependencies with:
```bash
pip install -r requirements.txt
```

## Integration with Web Interface

This tool is specifically designed to showcase the Local MCP Server web interface capabilities. Use it to:

1. **Test Configuration**: Verify parameter input and validation
2. **Monitor Execution**: Watch real-time progress and status updates
3. **Handle Errors**: Experience graceful error handling and recovery
4. **Manage Dependencies**: Practice dependency installation workflows
5. **User Interaction**: Test confirmation dialogs and safety features