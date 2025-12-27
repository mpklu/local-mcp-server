#!/usr/bin/env python3
"""
Web Interface Demo Features

Demonstrates advanced features of the Local MCP Server web interface including:
- Long-running tasks for timeout testing
- Dependency management workflows  
- Confirmation dialogs and user interaction
- Error handling and recovery patterns
"""

import json
import time
import fire
import os
import sys
from datetime import datetime
from typing import Optional


def long_running_task(duration=10, report_interval=2):
    """Simulate a long-running task to test timeout handling and progress monitoring.
    
    Args:
        duration (int): How long the task should run in seconds (default: 10, max: 60)
        report_interval (int): How often to report progress in seconds (default: 2)
        
    Returns:
        str: JSON formatted task completion report
    """
    try:
        # Limit maximum duration for safety
        duration = min(duration, 60)
        report_interval = max(report_interval, 1)
        
        start_time = time.time()
        reports = []
        
        print(f"Starting long-running task for {duration} seconds...")
        
        # Simulate work with progress reporting
        elapsed = 0
        while elapsed < duration:
            time.sleep(min(report_interval, duration - elapsed))
            elapsed = time.time() - start_time
            
            progress_percent = min((elapsed / duration) * 100, 100)
            report = {
                "elapsed_seconds": round(elapsed, 1),
                "progress_percent": round(progress_percent, 1),
                "timestamp": datetime.now().isoformat(),
                "status": "in_progress" if elapsed < duration else "completed"
            }
            reports.append(report)
            
            # Print progress for real-time monitoring
            print(f"Progress: {progress_percent:.1f}% ({elapsed:.1f}s/{duration}s)")
        
        end_time = time.time()
        total_elapsed = end_time - start_time
        
        result = {
            "task": "long_running_simulation",
            "requested_duration": duration,
            "actual_duration": round(total_elapsed, 2),
            "report_interval": report_interval,
            "total_progress_reports": len(reports),
            "completed_successfully": True,
            "progress_history": reports,
            "completion_time": datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2)
        
    except KeyboardInterrupt:
        return json.dumps({
            "task": "long_running_simulation",
            "error": "Task interrupted by user",
            "completed_successfully": False,
            "elapsed_seconds": round(time.time() - start_time, 2),
            "timestamp": datetime.now().isoformat()
        }, indent=2)
    except Exception as e:
        return f"Error in long-running task: {str(e)}"


def dependency_demo():
    """Demonstrate dependency management by trying to import various packages.
    
    This function attempts to import common packages to show how the web interface
    handles dependency installation and validation.
    
    Returns:
        str: JSON formatted dependency check results
    """
    try:
        # List of packages to test
        test_packages = [
            {"name": "requests", "module": "requests", "description": "HTTP library"},
            {"name": "pandas", "module": "pandas", "description": "Data analysis library"},
            {"name": "numpy", "module": "numpy", "description": "Scientific computing"},
            {"name": "pillow", "module": "PIL", "description": "Image processing"},
            {"name": "matplotlib", "module": "matplotlib", "description": "Plotting library"},
            {"name": "fire", "module": "fire", "description": "CLI interface (should be available)"}
        ]
        
        results = []
        available_count = 0
        
        for package in test_packages:
            try:
                __import__(package["module"])
                result = {
                    "package": package["name"],
                    "module": package["module"],
                    "description": package["description"],
                    "available": True,
                    "error": None
                }
                available_count += 1
            except ImportError as e:
                result = {
                    "package": package["name"],
                    "module": package["module"], 
                    "description": package["description"],
                    "available": False,
                    "error": str(e)
                }
            
            results.append(result)
        
        # Get Python environment info
        python_info = {
            "version": sys.version,
            "executable": sys.executable,
            "path": sys.path[:3]  # Show first few path entries
        }
        
        summary = {
            "dependency_check": {
                "total_packages_tested": len(test_packages),
                "available_packages": available_count,
                "missing_packages": len(test_packages) - available_count,
                "success_rate_percent": round((available_count / len(test_packages)) * 100, 1)
            },
            "python_environment": python_info,
            "package_results": results,
            "timestamp": datetime.now().isoformat(),
            "instructions": {
                "web_interface": "Use the web interface to install missing packages",
                "manual_install": "pip install package_name or uv add package_name"
            }
        }
        
        return json.dumps(summary, indent=2)
        
    except Exception as e:
        return f"Error checking dependencies: {str(e)}"


def interactive_demo(name="Anonymous", confirm=True, danger_level="low"):
    """Demonstrate interactive features requiring confirmation dialogs.
    
    Args:
        name (str): User name for personalized interaction (default: "Anonymous")
        confirm (bool): Whether this action requires confirmation (default: True) 
        danger_level (str): Risk level - "low", "medium", "high" (default: "low")
        
    Returns:
        str: JSON formatted interaction result
    """
    try:
        # Validate danger level
        valid_levels = ["low", "medium", "high"]
        if danger_level not in valid_levels:
            return f"Error: danger_level must be one of {valid_levels}"
        
        # Determine action based on danger level
        actions = {
            "low": {
                "action": "Display welcome message",
                "risk": "None",
                "confirmation_required": False
            },
            "medium": {
                "action": "Modify user preferences", 
                "risk": "May change system behavior",
                "confirmation_required": True
            },
            "high": {
                "action": "Delete temporary files",
                "risk": "Permanent data loss possible",
                "confirmation_required": True
            }
        }
        
        action_info = actions[danger_level]
        requires_confirmation = confirm and action_info["confirmation_required"]
        
        # Simulate confirmation check
        if requires_confirmation:
            print("⚠️  CONFIRMATION REQUIRED ⚠️")
            print(f"Action: {action_info['action']}")
            print(f"Risk Level: {danger_level.upper()}")
            print(f"Risk Description: {action_info['risk']}")
            print(f"User: {name}")
            print("")
            print("This action would normally require user confirmation in the web interface.")
            time.sleep(1)  # Simulate confirmation dialog delay
        
        # Execute the simulated action
        execution_result = {
            "user": name,
            "action_executed": action_info["action"],
            "danger_level": danger_level,
            "confirmation_required": requires_confirmation,
            "confirmation_bypassed": not confirm,
            "execution_time": datetime.now().isoformat(),
            "success": True,
            "message": f"Hello {name}! Successfully executed {danger_level} risk action."
        }
        
        # Add warnings for high-risk actions
        if danger_level == "high":
            execution_result["warnings"] = [
                "This was a high-risk operation",
                "Always verify destructive actions",
                "Consider backup procedures"
            ]
        
        result = {
            "interactive_demo": execution_result,
            "web_interface_features": {
                "confirmation_dialogs": "Shown for medium/high risk actions",
                "user_input_validation": "All parameters validated before execution",
                "progress_indicators": "Real-time feedback during execution",
                "error_recovery": "Graceful handling of failures"
            },
            "demonstration_complete": True
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error in interactive demo: {str(e)}"


def error_handling_demo(error_type="none"):
    """Demonstrate various error handling patterns and recovery mechanisms.
    
    Args:
        error_type (str): Type of error to simulate - "none", "value", "type", "runtime", "timeout"
        
    Returns:
        str: JSON formatted error handling demonstration
    """
    try:
        start_time = datetime.now()
        
        if error_type == "none":
            result = {
                "message": "No error requested - successful execution",
                "error_type": "none",
                "success": True
            }
        
        elif error_type == "value":
            # Simulate ValueError
            raise ValueError("Simulated ValueError: Invalid input parameter")
            
        elif error_type == "type":
            # Simulate TypeError  
            raise TypeError("Simulated TypeError: Incompatible data types")
            
        elif error_type == "runtime":
            # Simulate RuntimeError
            raise RuntimeError("Simulated RuntimeError: System operation failed")
            
        elif error_type == "timeout":
            # Simulate timeout scenario
            print("Simulating timeout scenario...")
            time.sleep(2)
            raise TimeoutError("Simulated TimeoutError: Operation exceeded time limit")
            
        else:
            return f"Error: Unknown error_type '{error_type}'. Valid types: none, value, type, runtime, timeout"
        
        # This will only execute for error_type="none"
        end_time = datetime.now()
        
        result.update({
            "execution_time": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_ms": int((end_time - start_time).total_seconds() * 1000)
            },
            "error_handling_info": {
                "graceful_degradation": "Errors are caught and formatted as JSON",
                "user_feedback": "Clear error messages with context",
                "logging": "All errors logged for debugging",
                "recovery": "System remains stable after errors"
            }
        })
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        # Demonstrate error handling
        end_time = datetime.now()
        
        error_result = {
            "error_demonstration": {
                "requested_error_type": error_type,
                "actual_error": str(e),
                "error_class": type(e).__name__,
                "caught_successfully": True,
                "execution_time": {
                    "start": start_time.isoformat(),
                    "error_occurred": end_time.isoformat(),
                    "duration_ms": int((end_time - start_time).total_seconds() * 1000)
                }
            },
            "error_handling_features": {
                "exception_catching": "All errors caught and processed",
                "structured_response": "Errors returned as valid JSON", 
                "context_preservation": "Error context maintained for debugging",
                "user_experience": "Graceful error presentation in web interface"
            },
            "recovery_status": "System operational after error"
        }
        
        return json.dumps(error_result, indent=2)


def configuration_showcase():
    """Showcase various configuration patterns for the web interface.
    
    Returns:
        str: JSON formatted configuration examples and patterns
    """
    try:
        # Demonstrate different parameter types and patterns
        config_examples = {
            "parameter_types": {
                "string": {
                    "example": "name='John Doe'",
                    "description": "Text input with validation"
                },
                "integer": {
                    "example": "duration=30",
                    "description": "Numeric input with range validation"
                },
                "boolean": {
                    "example": "confirm=True",
                    "description": "Checkbox or toggle input"
                },
                "choice": {
                    "example": "danger_level='medium'",
                    "description": "Dropdown selection from predefined options"
                },
                "json": {
                    "example": "headers='{\"Authorization\": \"Bearer token\"}'",
                    "description": "JSON input with syntax validation"
                }
            },
            "validation_patterns": {
                "required_parameters": "Parameters marked as required must be provided",
                "type_checking": "Input types validated before execution",
                "range_validation": "Numeric parameters can have min/max limits", 
                "format_validation": "String patterns validated (URLs, emails, etc.)",
                "dependency_checking": "Tool dependencies verified before execution"
            },
            "confirmation_workflows": {
                "low_risk": "No confirmation required",
                "medium_risk": "User confirmation dialog",
                "high_risk": "Multiple confirmations with warnings",
                "destructive": "Type confirmation text to proceed"
            },
            "execution_monitoring": {
                "progress_tracking": "Real-time progress for long operations",
                "timeout_handling": "Configurable timeouts with user notification",
                "error_recovery": "Graceful error handling with retry options",
                "result_formatting": "Structured output with syntax highlighting"
            }
        }
        
        # Add environment information
        environment_info = {
            "tool_location": __file__,
            "working_directory": os.getcwd(),
            "python_executable": sys.executable,
            "environment_variables": {
                "PATH": os.environ.get("PATH", "")[:100] + "...",  # Truncated
                "PYTHON_PATH": os.environ.get("PYTHONPATH", "Not set")
            }
        }
        
        result = {
            "configuration_showcase": config_examples,
            "environment_info": environment_info,
            "web_interface_capabilities": {
                "visual_configuration": "Point-and-click tool configuration",
                "parameter_editor": "Form-based parameter input",
                "dependency_management": "One-click dependency installation",
                "execution_monitoring": "Real-time execution feedback",
                "result_viewer": "Formatted output with export options"
            },
            "demonstration_timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error in configuration showcase: {str(e)}"


if __name__ == "__main__":
    fire.Fire()