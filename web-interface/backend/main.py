"""
FastAPI backend for MCP tool configuration web interface.
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import aiofiles

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
TOOL_NOT_FOUND = "Tool not found"
MCP_AVAILABLE = True  # We'll implement a simple executor directly

# Dependency management
class SimpleDependencyManager:
    """Simple dependency management for web interface."""
    
    def __init__(self, config_dir: Path, tools_dir: Path):
        self.config_dir = config_dir
        self.tools_dir = tools_dir
        self.python_env_dir = config_dir / "python_env"
    
    def get_python_executable(self) -> str:
        """Get Python executable path."""
        if self.python_env_dir.exists():
            if sys.platform == "win32":
                return str(self.python_env_dir / "Scripts" / "python.exe")
            else:
                return str(self.python_env_dir / "bin" / "python")
        return "python3"
    
    async def check_dependencies(self, dependencies: List[str]) -> Dict[str, bool]:
        """Check if dependencies are available."""
        results = {}
        python_exe = self.get_python_executable()
        
        for dep in dependencies:
            try:
                process = await asyncio.create_subprocess_exec(
                    python_exe, "-c", f"import {dep}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                results[dep] = process.returncode == 0
            except Exception:
                results[dep] = False
        
        return results
    
    async def install_dependencies(self, dependencies: List[str]) -> Dict[str, Any]:
        """Install missing dependencies."""
        python_exe = self.get_python_executable()
        results = {"success": True, "installed": [], "failed": [], "output": ""}
        
        for dep in dependencies:
            try:
                logger.info(f"Installing dependency: {dep}")
                process = await asyncio.create_subprocess_exec(
                    python_exe, "-m", "pip", "install", dep,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    results["installed"].append(dep)
                    results["output"] += f"✅ {dep}: {stdout.decode()}\n"
                else:
                    results["failed"].append(dep)
                    results["output"] += f"❌ {dep}: {stderr.decode()}\n"
                    results["success"] = False
                    
            except Exception as e:
                results["failed"].append(dep)
                results["output"] += f"❌ {dep}: {str(e)}\n"
                results["success"] = False
        
        return results

# Configuration paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
MCP_SERVER_DIR = PROJECT_ROOT / "server"
CONFIG_DIR = MCP_SERVER_DIR / "config"
TOOLS_DIR = PROJECT_ROOT / "tools"
INDIVIDUAL_TOOLS_DIR = CONFIG_DIR / "tools"

# Initialize dependency manager
dependency_manager = SimpleDependencyManager(CONFIG_DIR, TOOLS_DIR)

app = FastAPI(
    title="MCP Tool Configuration",
    description="Web interface for configuring Local MCP Server tools",
    version="0.1.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ToolParameter(BaseModel):
    name: str
    type: str
    description: str = ""
    required: bool = True
    default: Optional[Any] = None


class ScriptConfig(BaseModel):
    name: str
    description: str
    script_path: str
    script_type: str
    requires_confirmation: bool = True
    parameters: List[ToolParameter] = Field(default_factory=list)
    interactive: bool = False
    wrapper_function: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    enabled: bool = True


class IndividualToolConfig(BaseModel):
    enabled: bool = True
    last_modified: str = Field(default_factory=lambda: datetime.now().isoformat())
    auto_detected: bool = True
    tags: List[str] = Field(default_factory=list)
    script_config: ScriptConfig


class ToolTestRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ToolScanResult(BaseModel):
    new_tools: List[str]
    updated_tools: List[str]
    total_scanned: int


class ServerStatus(BaseModel):
    running: bool
    uptime: Optional[str] = None
    process_id: Optional[int] = None
    server_name: str
    last_started: Optional[str] = None


class ServerConfig(BaseModel):
    server_name: str
    server_version: str
    timeout_seconds: int
    max_output_length: int


class ServerLogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    source: str = "mcp-server"


class TagRequest(BaseModel):
    tags: List[str]


class TagResponse(BaseModel):
    success: bool
    message: str = ""


# Helper functions
async def load_individual_tool_config(tool_name: str) -> Optional[IndividualToolConfig]:
    """Load an individual tool configuration."""
    config_path = INDIVIDUAL_TOOLS_DIR / f"{tool_name}.json"
    
    if not config_path.exists():
        return None
    
    try:
        async with aiofiles.open(config_path, 'r') as f:
            content = await f.read()
            data = json.loads(content)
            return IndividualToolConfig(**data)
    except Exception as e:
        logger.error(f"Error loading tool config {tool_name}: {e}")
        return None


async def save_individual_tool_config(tool_name: str, config: IndividualToolConfig):
    """Save an individual tool configuration."""
    INDIVIDUAL_TOOLS_DIR.mkdir(exist_ok=True)
    config_path = INDIVIDUAL_TOOLS_DIR / f"{tool_name}.json"
    
    # Update last_modified timestamp
    config.last_modified = datetime.now().isoformat()
    
    try:
        async with aiofiles.open(config_path, 'w') as f:
            await f.write(config.model_dump_json(indent=2))
        logger.info(f"Saved config for tool: {tool_name}")
    except Exception as e:
        logger.error(f"Error saving tool config {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting test script: {e}")


@app.post("/api/dependencies/check")
async def check_dependencies():
    """Check system dependencies for all tools."""


async def run_discovery_scan() -> Dict[str, Any]:
    """Run tool discovery scan and return results."""
    try:
        # For now, let's use a simpler approach and call the build script
        build_script = MCP_SERVER_DIR / "build_tools.py"
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(build_script),
            "--config-dir", str(CONFIG_DIR),
            "--migrate",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Discovery scan failed: {stderr.decode()}")
            raise HTTPException(status_code=500, detail="Discovery scan failed")
        
        return {
            "success": True,
            "message": "Discovery scan completed",
            "output": stdout.decode()
        }
        
    except Exception as e:
        logger.error(f"Error running discovery scan: {e}")
        raise HTTPException(status_code=500, detail=f"Discovery scan error: {e}")


async def execute_tool_for_testing(tool_name: str, config: IndividualToolConfig, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Simple tool executor for testing purposes."""
    try:
        script_config = config.script_config
        tools_dir = Path(__file__).parent.parent.parent / "tools"
        script_path = tools_dir / script_config.script_path
        
        if not script_path.exists():
            return {
                "success": False,
                "message": f"Script not found: {script_path}",
                "error": f"File does not exist: {script_path}"
            }
        
        # Build command based on script type
        if script_config.script_type == "python":
            # For uv run, use absolute paths and proper working directory
            local_mcp_server_dir = Path(__file__).parent.parent.parent / "local_mcp_server"
            cmd = ["uv", "--directory", str(local_mcp_server_dir), "run", "python3", str(script_path.absolute())]
        elif script_config.script_type == "shell":
            cmd = [str(script_path)]
        else:
            return {
                "success": False,
                "message": f"Unsupported script type: {script_config.script_type}",
                "error": f"Script type '{script_config.script_type}' is not supported"
            }
        
        # Add parameters as command line arguments
        for key, value in parameters.items():
            if key != 'confirm':  # Skip MCP-specific arguments
                if key.startswith('--'):
                    cmd.extend([key, str(value)])
                elif len(key) == 1:
                    cmd.extend([f'-{key}', str(value)])
                else:
                    cmd.append(str(value))
        
        # Execute the command
        logger.info(f"Executing: {' '.join(cmd)}")
        
        # Set working directory to the script's directory so it can find its config files
        work_dir = script_path.parent
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return {
                "success": False,
                "message": "Tool execution timed out after 30 seconds",
                "error": "Execution timeout"
            }
        
        stdout_text = stdout.decode('utf-8') if stdout else ''
        stderr_text = stderr.decode('utf-8') if stderr else ''
        
        output_parts = [
            f"Command: {' '.join(cmd)}",
            f"Exit code: {process.returncode}",
            ""
        ]
        
        if stdout_text:
            output_parts.extend(["=== STDOUT ===", stdout_text, ""])
        
        if stderr_text:
            output_parts.extend(["=== STDERR ===", stderr_text, ""])
        
        result_output = '\n'.join(output_parts)
        
        if process.returncode == 0:
            return {
                "success": True,
                "message": "Tool executed successfully",
                "output": result_output
            }
        else:
            return {
                "success": False,
                "message": f"Tool execution failed with exit code {process.returncode}",
                "output": result_output,
                "error": f"Non-zero exit code: {process.returncode}"
            }
            
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return {
            "success": False,
            "message": f"Tool execution error: {str(e)}",
            "error": str(e)
        }


# API Routes

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/tools", response_model=List[IndividualToolConfig])
async def list_tools():
    """List all configured tools."""
    tools = []
    
    if not INDIVIDUAL_TOOLS_DIR.exists():
        return tools
    
    for config_file in INDIVIDUAL_TOOLS_DIR.glob("*.json"):
        tool_name = config_file.stem
        config = await load_individual_tool_config(tool_name)
        if config:
            tools.append(config)
    
    return tools


@app.get("/api/tools/{tool_name}", response_model=IndividualToolConfig)
async def get_tool(tool_name: str):
    """Get a specific tool configuration."""
    config = await load_individual_tool_config(tool_name)
    if not config:
        raise HTTPException(status_code=404, detail=TOOL_NOT_FOUND)
    return config


@app.put("/api/tools/{tool_name}")
async def update_tool(tool_name: str, config: IndividualToolConfig):
    """Update a tool configuration."""
    await save_individual_tool_config(tool_name, config)
    return {"message": f"Tool {tool_name} updated successfully"}


@app.delete("/api/tools/{tool_name}")
async def delete_tool(tool_name: str):
    """Delete a tool configuration."""
    config_path = INDIVIDUAL_TOOLS_DIR / f"{tool_name}.json"
    
    if not config_path.exists():
        raise HTTPException(status_code=404, detail=TOOL_NOT_FOUND)
    
    try:
        config_path.unlink()
        logger.info(f"Deleted tool config: {tool_name}")
        return {"message": f"Tool {tool_name} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete tool: {e}")


class ToolCreationRequest(BaseModel):
    name: str
    description: str
    script_type: str  # 'python' or 'shell'
    method: str  # 'manual' or 'import'
    script_path: Optional[str] = None  # For import method
    parameters: List[ToolParameter] = Field(default_factory=list)


@app.post("/api/tools")
async def create_tool(request: ToolCreationRequest):
    """Create a new tool with directory structure and files."""
    tool_name = request.name.lower().replace(' ', '-').replace('_', '-')
    tool_dir = TOOLS_DIR / tool_name
    
    # Check if tool already exists
    if tool_dir.exists():
        raise HTTPException(status_code=409, detail=f"Tool '{tool_name}' already exists")
    
    try:
        # Create tool directory
        tool_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created tool directory: {tool_dir}")
        
        if request.method == 'manual':
            # Generate template files
            if request.script_type == 'python':
                await create_python_template(tool_dir, request)
            else:  # shell
                await create_shell_template(tool_dir, request)
        else:  # import
            # Handle import logic
            if request.script_path:
                await import_existing_script(tool_dir, request.script_path, request.script_type)
        
        # Create tool configuration
        script_filename = 'run.py' if request.script_type == 'python' else 'run'
        config = IndividualToolConfig(
            enabled=True,
            last_modified=datetime.now().isoformat(),
            auto_detected=False,
            tags=[],
            script_config=ScriptConfig(
                name=tool_name,
                description=request.description,
                script_path=f"{tool_name}/{script_filename}",
                script_type=request.script_type,
                requires_confirmation=True,
                parameters=request.parameters,
                interactive=False,
                wrapper_function=None,
                dependencies=[],
                examples=[],
                enabled=True
            )
        )
        
        await save_individual_tool_config(tool_name, config)
        
        return {
            "success": True,
            "tool_name": tool_name,
            "message": f"Tool '{tool_name}' created successfully",
            "directory": str(tool_dir)
        }
        
    except Exception as e:
        # Clean up on error
        if tool_dir.exists():
            import shutil
            shutil.rmtree(tool_dir)
        
        logger.error(f"Error creating tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create tool: {e}")


async def create_python_template(tool_dir: Path, request: ToolCreationRequest):
    """Create Python template files."""
    # Create run.py with text processor template
    run_content = '''#!/usr/bin/env python3
"""
{description}

A sample text processing tool that demonstrates various MCP tool features.
"""

import sys
import argparse
from pathlib import Path


def process_text(text: str, operation: str = "uppercase", output_file: str = None) -> str:
    """
    Process text with various operations.
    
    Args:
        text: Input text to process
        operation: Operation to perform (uppercase, lowercase, reverse, word_count)
        output_file: Optional output file path
    
    Returns:
        Processed text or result
    """
    operations = {{
        "uppercase": lambda t: t.upper(),
        "lowercase": lambda t: t.lower(),
        "reverse": lambda t: t[::-1],
        "word_count": lambda t: f"Word count: {{len(t.split())}}"
    }}
    
    if operation not in operations:
        raise ValueError(f"Invalid operation. Choose from: {{', '.join(operations.keys())}}")
    
    result = operations[operation](text)
    
    if output_file:
        Path(output_file).write_text(result)
        return f"Result saved to {{output_file}}: {{result}}"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("text", help="Text to process")
    parser.add_argument("--operation", "-o", 
                       choices=["uppercase", "lowercase", "reverse", "word_count"],
                       default="uppercase",
                       help="Operation to perform on text")
    parser.add_argument("--output-file", "-f", help="Output file path (optional)")
    
    args = parser.parse_args()
    
    try:
        result = process_text(args.text, args.operation, args.output_file)
        print(result)
        return 0
    except Exception as e:
        print(f"Error: {{e}}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
'''.format(description=request.description)
    
    # Create test.py
    test_content = '''#!/usr/bin/env python3
"""
Test script for {name} tool.
"""

import sys
import subprocess
from pathlib import Path


def test_basic_operations():
    """Test basic text processing operations."""
    test_cases = [
        ("hello world", "uppercase", "HELLO WORLD"),
        ("HELLO WORLD", "lowercase", "hello world"),
        ("hello", "reverse", "olleh"),
        ("hello world test", "word_count", "Word count: 3"),
    ]
    
    for text, operation, expected in test_cases:
        try:
            result = subprocess.run([
                sys.executable, "run.py", text, "--operation", operation
            ], capture_output=True, text=True, check=True)
            
            if expected in result.stdout:
                print(f"✅ Test passed: {{operation}} operation")
            else:
                print(f"❌ Test failed: {{operation}} operation")
                print(f"   Expected: {{expected}}")
                print(f"   Got: {{result.stdout.strip()}}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Test failed: {{operation}} operation - {{e}}")


def test_file_output():
    """Test file output functionality."""
    try:
        test_file = Path("test_output.txt")
        result = subprocess.run([
            sys.executable, "run.py", "test text", 
            "--operation", "uppercase", 
            "--output-file", str(test_file)
        ], capture_output=True, text=True, check=True)
        
        if test_file.exists() and "TEST TEXT" in test_file.read_text():
            print("✅ File output test passed")
            test_file.unlink()  # Clean up
        else:
            print("❌ File output test failed")
    except Exception as e:
        print(f"❌ File output test failed: {{e}}")


def main():
    print(f"Testing {name} tool...")
    test_basic_operations()
    test_file_output()
    print("Test completed.")


if __name__ == "__main__":
    main()
'''.format(name=request.name)
    
    # Create README.md
    readme_content = f'''# {request.name.title()} Tool

{request.description}

## Usage

```bash
python run.py "your text here" --operation uppercase
python run.py "your text here" --operation lowercase --output-file output.txt
```

## Operations

- `uppercase`: Convert text to uppercase
- `lowercase`: Convert text to lowercase  
- `reverse`: Reverse the text
- `word_count`: Count words in the text

## Testing

```bash
python test.py
```

## Parameters

- `text` (required): The text to process
- `--operation` (optional): Operation to perform (default: uppercase)
- `--output-file` (optional): Save result to file
'''
    
    # Write files
    async with aiofiles.open(tool_dir / "run.py", 'w') as f:
        await f.write(run_content)
    
    async with aiofiles.open(tool_dir / "test.py", 'w') as f:
        await f.write(test_content)
    
    async with aiofiles.open(tool_dir / "README.md", 'w') as f:
        await f.write(readme_content)
    
    # Make run.py executable
    (tool_dir / "run.py").chmod(0o755)
    (tool_dir / "test.py").chmod(0o755)


async def create_shell_template(tool_dir: Path, request: ToolCreationRequest):
    """Create shell script template files."""
    # Create run script
    run_content = f'''#!/bin/bash
# {request.description}

set -e

# Default values
OPERATION="uppercase"
OUTPUT_FILE=""

# Help function
show_help() {{
    echo "Usage: $0 <text> [--operation OPERATION] [--output-file FILE]"
    echo ""
    echo "Arguments:"
    echo "  text                Text to process"
    echo ""
    echo "Options:"
    echo "  --operation OP      Operation: uppercase, lowercase, reverse, word_count (default: uppercase)"
    echo "  --output-file FILE  Save result to file"
    echo "  -h, --help         Show this help"
}}

# Parse arguments
TEXT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --operation)
            OPERATION="$2"
            shift 2
            ;;
        --output-file)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            if [[ -z "$TEXT" ]]; then
                TEXT="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$TEXT" ]]; then
    echo "Error: Text argument is required" >&2
    show_help
    exit 1
fi

# Process text based on operation
case "$OPERATION" in
    uppercase)
        RESULT=$(echo "$TEXT" | tr '[:lower:]' '[:upper:]')
        ;;
    lowercase)
        RESULT=$(echo "$TEXT" | tr '[:upper:]' '[:lower:]')
        ;;
    reverse)
        RESULT=$(echo "$TEXT" | rev)
        ;;
    word_count)
        COUNT=$(echo "$TEXT" | wc -w | tr -d ' ')
        RESULT="Word count: $COUNT"
        ;;
    *)
        echo "Error: Invalid operation '$OPERATION'" >&2
        echo "Valid operations: uppercase, lowercase, reverse, word_count" >&2
        exit 1
        ;;
esac

# Output result
if [[ -n "$OUTPUT_FILE" ]]; then
    echo "$RESULT" > "$OUTPUT_FILE"
    echo "Result saved to $OUTPUT_FILE: $RESULT"
else
    echo "$RESULT"
fi
'''
    
    # Create test script  
    test_content = f'''#!/bin/bash
# Test script for {request.name} tool

echo "Testing {request.name} tool..."

# Test basic operations
test_operation() {{
    local text="$1"
    local operation="$2"
    local expected="$3"
    
    result=$(./run "$text" --operation "$operation" 2>/dev/null)
    if [[ "$result" == *"$expected"* ]]; then
        echo "✅ Test passed: $operation operation"
    else
        echo "❌ Test failed: $operation operation"
        echo "   Expected: $expected"
        echo "   Got: $result"
    fi
}}

# Run tests
test_operation "hello world" "uppercase" "HELLO WORLD"
test_operation "HELLO WORLD" "lowercase" "hello world"
test_operation "hello" "reverse" "olleh"
test_operation "hello world test" "word_count" "Word count: 3"

# Test file output
echo "Testing file output..."
./run "test text" --operation uppercase --output-file test_output.txt 2>/dev/null
if [[ -f "test_output.txt" ]] && grep -q "TEST TEXT" test_output.txt; then
    echo "✅ File output test passed"
    rm -f test_output.txt
else
    echo "❌ File output test failed"
fi

echo "Test completed."
'''
    
    # Create README.md (same as Python version)
    readme_content = f'''# {request.name.title()} Tool

{request.description}

## Usage

```bash
./run "your text here" --operation uppercase
./run "your text here" --operation lowercase --output-file output.txt
```

## Operations

- `uppercase`: Convert text to uppercase
- `lowercase`: Convert text to lowercase  
- `reverse`: Reverse the text
- `word_count`: Count words in the text

## Testing

```bash
./test
```

## Parameters

- `text` (required): The text to process
- `--operation` (optional): Operation to perform (default: uppercase)
- `--output-file` (optional): Save result to file
'''
    
    # Write files
    async with aiofiles.open(tool_dir / "run", 'w') as f:
        await f.write(run_content)
    
    async with aiofiles.open(tool_dir / "test", 'w') as f:
        await f.write(test_content)
    
    async with aiofiles.open(tool_dir / "README.md", 'w') as f:
        await f.write(readme_content)
    
    # Make scripts executable
    (tool_dir / "run").chmod(0o755)
    (tool_dir / "test").chmod(0o755)


async def import_existing_script(tool_dir: Path, script_path: str, script_type: str):
    """Import an existing script."""
    source_path = Path(script_path)
    
    if not source_path.exists():
        raise ValueError(f"Script not found: {script_path}")
    
    target_filename = 'run.py' if script_type == 'python' else 'run'
    target_path = tool_dir / target_filename
    
    # Copy the script
    import shutil
    shutil.copy2(source_path, target_path)
    target_path.chmod(0o755)
    
    # Create a basic README
    readme_content = f'''# Imported Tool

Imported from: {script_path}

This tool was imported from an existing script. Please review and update the configuration as needed.
'''
    
    async with aiofiles.open(tool_dir / "README.md", 'w') as f:
        await f.write(readme_content)


@app.post("/api/tools/bulk-update")
async def bulk_update_tools(updates: Dict[str, Dict[str, Any]]):
    """Bulk update multiple tools (enable/disable/delete)."""
    results = {}
    
    for tool_name, update_data in updates.items():
        try:
            action = update_data.get("action")
            
            if action == "delete":
                await delete_tool(tool_name)
                results[tool_name] = {"status": "deleted"}
            
            elif action == "update":
                config = await load_individual_tool_config(tool_name)
                if config:
                    # Apply updates
                    if "enabled" in update_data:
                        config.enabled = update_data["enabled"]
                    
                    await save_individual_tool_config(tool_name, config)
                    results[tool_name] = {"status": "updated"}
                else:
                    results[tool_name] = {"status": "error", "message": TOOL_NOT_FOUND}
            
        except Exception as e:
            results[tool_name] = {"status": "error", "message": str(e)}
    
    return {"results": results}


@app.post("/api/scan")
async def scan_for_tools(background_tasks: BackgroundTasks):
    """Scan for new tools in the tools directory."""
    try:
        result = await run_discovery_scan()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/build")
async def build_tools_json():
    """Build the main tools.json from individual configurations."""
    try:
        build_script = MCP_SERVER_DIR / "build_tools.py"
        
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(build_script),
            "--config-dir", str(CONFIG_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Build failed: {stderr.decode()}")
            raise HTTPException(status_code=500, detail="Build failed")
        
        return {
            "success": True,
            "message": "tools.json built successfully",
            "output": stdout.decode()
        }
        
    except Exception as e:
        logger.error(f"Error building tools.json: {e}")
        raise HTTPException(status_code=500, detail=f"Build error: {e}")


@app.post("/api/tools/{tool_name}/test")
async def test_tool_directly(tool_name: str, request: ToolTestRequest):
    """Test a tool directly by executing it with provided parameters."""
    try:
        # Load tool configuration
        config = await load_individual_tool_config(tool_name)
        if not config:
            raise HTTPException(status_code=404, detail=TOOL_NOT_FOUND)
        
        # First check if there's a test script - if so, run that instead
        script_config = config.script_config
        tools_dir = Path(__file__).parent.parent.parent / "tools"
        script_path = tools_dir / script_config.script_path
        tool_dir = script_path.parent
        
        # Look for test script first
        test_scripts = ["test.py", "test"]
        test_script_path = None
        
        for test_script_name in test_scripts:
            potential_path = tool_dir / test_script_name
            if potential_path.exists():
                test_script_path = potential_path
                break
        
        if test_script_path:
            # If test script exists, run it instead
            return await run_tool_test_script(tool_name)
        else:
            # No test script, execute the tool directly with parameters
            result = await execute_tool_for_testing(tool_name, config, request.parameters)
            
            return {
                "success": result["success"],
                "message": result["message"],
                "parameters": request.parameters,
                "output": result.get("output", ""),
                "error": result.get("error"),
                "execution_type": "direct_tool_execution"
            }
            
    except Exception as e:
        logger.error(f"Error testing tool {tool_name}: {e}")
        return {
            "success": False,
            "message": f"Tool test error: {str(e)}",
            "parameters": request.parameters,
            "error": str(e),
            "execution_type": "error"
        }


@app.post("/api/tools/{tool_name}/test-script")
async def run_tool_test_script(tool_name: str):
    """Run a tool's test script if it exists."""
    try:
        # Load tool configuration to get the tool directory
        config = await load_individual_tool_config(tool_name)
        if not config:
            raise HTTPException(status_code=404, detail=TOOL_NOT_FOUND)
        
        # Determine tool directory from script path
        script_config = config.script_config
        tools_dir = Path(__file__).parent.parent.parent / "tools"
        script_path = tools_dir / script_config.script_path
        tool_dir = script_path.parent
        
        # Look for test script (test.py for Python tools, test for shell tools)
        test_scripts = ["test.py", "test"]
        test_script_path = None
        
        for test_script_name in test_scripts:
            potential_path = tool_dir / test_script_name
            if potential_path.exists():
                test_script_path = potential_path
                break
        
        if not test_script_path:
            return {
                "success": False,
                "message": "No test script found",
                "has_test_script": False,
                "output": f"No test script found in {tool_dir}. Looked for: {', '.join(test_scripts)}"
            }
        
        # Execute the test script
        if test_script_path.name.endswith('.py'):
            # Python test script
            local_mcp_server_dir = Path(__file__).parent.parent.parent / "local_mcp_server"
            cmd = ["uv", "--directory", str(local_mcp_server_dir), "run", "python3", str(test_script_path.absolute())]
        else:
            # Shell test script
            cmd = [str(test_script_path)]
        
        logger.info(f"Executing test script: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tool_dir
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60.0)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return {
                "success": False,
                "message": "Test script execution timed out after 60 seconds",
                "has_test_script": True,
                "output": "Execution timeout",
                "error": "Test script timeout"
            }
        
        stdout_text = stdout.decode('utf-8') if stdout else ''
        stderr_text = stderr.decode('utf-8') if stderr else ''
        
        output_parts = [
            f"Test Script: {test_script_path.name}",
            f"Command: {' '.join(cmd)}",
            f"Exit code: {process.returncode}",
            ""
        ]
        
        if stdout_text:
            output_parts.extend(["=== TEST OUTPUT ===", stdout_text, ""])
        
        if stderr_text:
            output_parts.extend(["=== TEST STDERR ===", stderr_text, ""])
        
        result_output = '\n'.join(output_parts)
        
        return {
            "success": process.returncode == 0,
            "message": "Test script completed successfully" if process.returncode == 0 else f"Test script failed with exit code {process.returncode}",
            "has_test_script": True,
            "test_script_path": str(test_script_path),
            "output": result_output,
            "exit_code": process.returncode,
            "error": stderr_text if process.returncode != 0 else None
        }
        
    except Exception as e:
        logger.error(f"Error running test script for {tool_name}: {e}")
        return {
            "success": False,
            "message": f"Test script execution error: {str(e)}",
            "has_test_script": True,
            "output": f"Error: {str(e)}",
            "error": str(e)
        }


@app.get("/api/tools/{tool_name}/test-script")
async def get_tool_test_script(tool_name: str):
    """Get the content of a tool's test script."""
    try:
        # Load tool configuration to get the tool directory
        config = await load_individual_tool_config(tool_name)
        if not config:
            raise HTTPException(status_code=404, detail=TOOL_NOT_FOUND)
        
        # Determine tool directory from script path
        script_config = config.script_config
        tools_dir = Path(__file__).parent.parent.parent / "tools"
        script_path = tools_dir / script_config.script_path
        tool_dir = script_path.parent
        
        # Look for test script
        test_scripts = ["test.py", "test"]
        test_script_path = None
        
        for test_script_name in test_scripts:
            potential_path = tool_dir / test_script_name
            if potential_path.exists():
                test_script_path = potential_path
                break
        
        if not test_script_path:
            return {
                "exists": False,
                "message": "No test script found",
                "content": "",
                "script_type": None,
                "path": None
            }
        
        # Read the test script content
        async with aiofiles.open(test_script_path, 'r') as f:
            content = await f.read()
        
        script_type = "python" if test_script_path.name.endswith('.py') else "shell"
        
        return {
            "exists": True,
            "content": content,
            "script_type": script_type,
            "path": str(test_script_path),
            "name": test_script_path.name
        }
            
    except Exception as e:
        logger.error(f"Error reading test script for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading test script: {e}")


@app.put("/api/tools/{tool_name}/test-script")
async def save_tool_test_script(tool_name: str, request: Dict[str, Any]):
    """Save or create a tool's test script."""
    try:
        content = request.get("content", "")
        script_type = request.get("script_type", "python")
        
        # Load tool configuration to get the tool directory
        config = await load_individual_tool_config(tool_name)
        if not config:
            raise HTTPException(status_code=404, detail=TOOL_NOT_FOUND)
        
        # Determine tool directory from script path
        script_config = config.script_config
        tools_dir = Path(__file__).parent.parent.parent / "tools"
        script_path = tools_dir / script_config.script_path
        tool_dir = script_path.parent
        
        # Determine test script filename
        test_script_name = "test.py" if script_type == "python" else "test"
        test_script_path = tool_dir / test_script_name
        
        # Save the test script
        async with aiofiles.open(test_script_path, 'w') as f:
            await f.write(content)
        
        # Make shell scripts executable
        if script_type == "shell":
            import stat
            test_script_path.chmod(test_script_path.stat().st_mode | stat.S_IEXEC)
        
        logger.info(f"Saved test script for tool: {tool_name}")
        
        return {
            "success": True,
            "message": f"Test script saved successfully",
            "path": str(test_script_path),
            "script_type": script_type
        }
            
    except Exception as e:
        logger.error(f"Error saving test script for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving test script: {e}")


@app.delete("/api/tools/{tool_name}/test-script")
async def delete_tool_test_script(tool_name: str):
    """Delete a tool's test script."""
    try:
        # Load tool configuration to get the tool directory
        config = await load_individual_tool_config(tool_name)
        if not config:
            raise HTTPException(status_code=404, detail=TOOL_NOT_FOUND)
        
        # Determine tool directory from script path
        script_config = config.script_config
        tools_dir = Path(__file__).parent.parent.parent / "tools"
        script_path = tools_dir / script_config.script_path
        tool_dir = script_path.parent
        
        # Look for test script and delete it
        test_scripts = ["test.py", "test"]
        deleted_scripts = []
        
        for test_script_name in test_scripts:
            test_script_path = tool_dir / test_script_name
            if test_script_path.exists():
                test_script_path.unlink()
                deleted_scripts.append(test_script_name)
        
        if deleted_scripts:
            return {
                "success": True,
                "message": f"Deleted test scripts: {', '.join(deleted_scripts)}",
                "deleted": deleted_scripts
            }
        else:
            return {
                "success": False,
                "message": "No test script found to delete",
                "deleted": []
            }
            
    except Exception as e:
        logger.error(f"Error deleting test script for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting test script: {e}")


@app.post("/api/tools/{tool_name}/dependencies/check")
async def check_tool_dependencies(tool_name: str):
    """Check if a tool's dependencies are available."""
    try:
        config = await load_individual_tool_config(tool_name)
        if not config:
            raise HTTPException(status_code=404, detail=TOOL_NOT_FOUND)
        
        deps_status = await dependency_manager.check_dependencies(config.script_config.dependencies)
        missing_deps = [dep for dep, available in deps_status.items() if not available]
        
        return {
            "tool_name": tool_name,
            "dependencies": config.script_config.dependencies,
            "status": deps_status,
            "missing": missing_deps,
            "all_available": len(missing_deps) == 0
        }
        
    except Exception as e:
        logger.error(f"Error checking dependencies for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Dependency check error: {e}")


@app.post("/api/tools/{tool_name}/dependencies/install")
async def install_tool_dependencies(tool_name: str):
    """Install missing dependencies for a tool."""
    try:
        config = await load_individual_tool_config(tool_name)
        if not config:
            raise HTTPException(status_code=404, detail=TOOL_NOT_FOUND)
        
        deps_status = await dependency_manager.check_dependencies(config.script_config.dependencies)
        missing_deps = [dep for dep, available in deps_status.items() if not available]
        
        if not missing_deps:
            return {
                "success": True,
                "message": "All dependencies already installed",
                "missing": [],
                "installed": [],
                "failed": []
            }
        
        result = await dependency_manager.install_dependencies(missing_deps)
        
        return {
            "success": result["success"],
            "message": f"Installation completed. Installed: {len(result['installed'])}, Failed: {len(result['failed'])}",
            "missing": missing_deps,
            "installed": result["installed"],
            "failed": result["failed"],
            "output": result["output"]
        }
        
    except Exception as e:
        logger.error(f"Error installing dependencies for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Dependency installation error: {e}")


@app.get("/api/environment/info")
async def get_environment_info():
    """Get information about the Python environment."""
    try:
        python_exe = dependency_manager.get_python_executable()
        env_exists = Path(dependency_manager.python_env_dir).exists()
        
        # Check Python version
        try:
            process = await asyncio.create_subprocess_exec(
                python_exe, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            python_version = stdout.decode().strip() if stdout else "Unknown"
        except Exception:
            python_version = "Unknown"
        
        return {
            "python_executable": python_exe,
            "python_version": python_version,
            "virtual_env_exists": env_exists,
            "virtual_env_path": str(dependency_manager.python_env_dir),
            "config_dir": str(CONFIG_DIR),
            "tools_dir": str(TOOLS_DIR)
        }
        
    except Exception as e:
        logger.error(f"Error getting environment info: {e}")
        raise HTTPException(status_code=500, detail=f"Environment info error: {e}")


# Tag management endpoints
@app.get("/api/tags")
async def get_all_tags():
    """Get all unique tags across all tools."""
    try:
        all_tags = set()
        
        # Iterate through all individual tool configs
        if INDIVIDUAL_TOOLS_DIR.exists():
            for config_file in INDIVIDUAL_TOOLS_DIR.glob("*.json"):
                try:
                    async with aiofiles.open(config_file, 'r') as f:
                        content = await f.read()
                        data = json.loads(content)
                        tool_config = IndividualToolConfig(**data)
                        all_tags.update(tool_config.tags)
                except Exception as e:
                    logger.warning(f"Error reading tags from {config_file}: {e}")
                    continue
        
        return {
            "tags": sorted(all_tags)
        }
        
    except Exception as e:
        logger.error(f"Error getting all tags: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting tags: {e}")


@app.post("/api/tools/{tool_name}/tags", response_model=TagResponse)
async def manage_tool_tags(tool_name: str, tag_request: TagRequest):
    """Add or update tags for a specific tool."""
    try:
        config = await load_individual_tool_config(tool_name)
        if not config:
            raise HTTPException(status_code=404, detail=TOOL_NOT_FOUND)
        
        # Remove duplicates and empty strings
        new_tags = [tag.strip() for tag in tag_request.tags if tag.strip()]
        config.tags = list(dict.fromkeys(new_tags))  # Preserve order while removing duplicates
        
        await save_individual_tool_config(tool_name, config)
        
        return TagResponse(
            success=True,
            message=f"Tags updated for {tool_name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tags for {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating tags: {e}")


@app.delete("/api/tools/{tool_name}/tags/{tag}")
async def delete_tool_tag(tool_name: str, tag: str):
    """Remove a specific tag from a tool."""
    try:
        config = await load_individual_tool_config(tool_name)
        if not config:
            raise HTTPException(status_code=404, detail=TOOL_NOT_FOUND)
        
        if tag in config.tags:
            config.tags.remove(tag)
            await save_individual_tool_config(tool_name, config)
            return {"success": True, "message": f"Tag '{tag}' removed from {tool_name}"}
        else:
            return {"success": False, "message": f"Tag '{tag}' not found in {tool_name}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing tag from {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error removing tag: {e}")


@app.get("/api/tags/suggestions")
async def get_tag_suggestions(q: str = ""):
    """Get tag suggestions based on existing tags and query."""
    try:
        # Get all existing tags
        all_tags_response = await get_all_tags()
        all_tags = all_tags_response["tags"]
        
        if not q:
            return {"suggestions": all_tags[:20]}  # Return first 20 tags if no query
        
        # Filter tags that contain the query (case insensitive)
        query_lower = q.lower()
        matching_tags = [tag for tag in all_tags if query_lower in tag.lower()]
        
        # Sort by relevance (exact match first, then starts with, then contains)
        exact_match = [tag for tag in matching_tags if tag.lower() == query_lower]
        starts_with = [tag for tag in matching_tags if tag.lower().startswith(query_lower) and tag.lower() != query_lower]
        contains = [tag for tag in matching_tags if query_lower in tag.lower() and not tag.lower().startswith(query_lower)]
        
        suggestions = exact_match + starts_with + contains
        
        return {"suggestions": suggestions[:10]}  # Return top 10 suggestions
        
    except Exception as e:
        logger.error(f"Error getting tag suggestions: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting tag suggestions: {e}")


# Server monitoring endpoints (read-only)
@app.get("/api/server/status", response_model=ServerStatus)
async def get_server_status():
    """Get MCP server status (monitoring only - server managed by Claude Desktop)."""
    try:
        global_config_path = CONFIG_DIR / "global.json"
        
        server_name = "local-mcp-server"  # default
        if global_config_path.exists():
            async with aiofiles.open(global_config_path, 'r') as f:
                global_config = json.loads(await f.read())
                server_name = global_config.get("server_name", "local-mcp-server")
        
        # Check multiple indicators of server activity
        log_file = CONFIG_DIR / "server.log"
        running = False
        last_started = None
        
        # Method 1: Check log file modification time
        if log_file.exists():
            import os
            import time
            stat = os.stat(log_file)
            last_modified = stat.st_mtime
            if time.time() - last_modified < 300:  # 5 minutes
                running = True
                last_started = datetime.fromtimestamp(last_modified).isoformat()
        
        # Method 2: Check for running MCP server process (more reliable)
        try:
            import subprocess
            result = subprocess.run(
                ["pgrep", "-f", "local_mcp.server"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                running = True
                if not last_started:
                    # Get process start time if available
                    pid = result.stdout.strip().split('\n')[0]
                    try:
                        ps_result = subprocess.run(
                            ["ps", "-o", "lstart=", "-p", pid],
                            capture_output=True,
                            text=True
                        )
                        if ps_result.returncode == 0:
                            last_started = ps_result.stdout.strip()
                    except:
                        pass
        except Exception:
            pass  # Fall back to log-based detection
        
        return ServerStatus(
            running=running,
            server_name=server_name,
            uptime=None,  # Cannot determine uptime without process access
            process_id=None,  # Cannot access PID of Claude-managed process
            last_started=last_started
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting server status: {str(e)}")


@app.get("/api/server/config", response_model=ServerConfig)
async def get_server_config():
    """Get MCP server configuration."""
    try:
        global_config_path = CONFIG_DIR / "global.json"
        
        if not global_config_path.exists():
            raise HTTPException(status_code=404, detail="Global config file not found")
        
        async with aiofiles.open(global_config_path, 'r') as f:
            config_data = json.loads(await f.read())
        
        return ServerConfig(
            server_name=config_data.get("server_name", "local-mcp-server"),
            server_version=config_data.get("server_version", "1.0.0"),
            timeout_seconds=config_data.get("timeout_seconds", 300),
            max_output_length=config_data.get("max_output_length", 10000)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting server config: {str(e)}")


@app.post("/api/server/config")
async def update_server_config(config: ServerConfig):
    """Update MCP server configuration."""
    try:
        global_config_path = CONFIG_DIR / "global.json"
        
        # Load existing config
        existing_config = {}
        if global_config_path.exists():
            async with aiofiles.open(global_config_path, 'r') as f:
                existing_config = json.loads(await f.read())
        
        # Update with new values
        existing_config.update({
            "server_name": config.server_name,
            "server_version": config.server_version,
            "timeout_seconds": config.timeout_seconds,
            "max_output_length": config.max_output_length
        })
        
        # Save updated config
        async with aiofiles.open(global_config_path, 'w') as f:
            await f.write(json.dumps(existing_config, indent=2))
        
        return {"message": "Server configuration updated successfully. Restart required for changes to take effect."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating server config: {str(e)}")


# Note: Server start/stop endpoints removed - server is managed by Claude Desktop


@app.get("/api/server/logs")
async def get_server_logs(lines: int = 100):
    """Get recent server logs from actual log file."""
    try:
        log_file = CONFIG_DIR / "server.log"
        
        if not log_file.exists():
            # Provide helpful information when no log file exists
            return [
                ServerLogEntry(
                    timestamp=datetime.now().isoformat(),
                    level="INFO",
                    message="No log file found. When MCP server is managed by Claude Desktop, logs may not be redirected to file.",
                    source="monitoring"
                ),
                ServerLogEntry(
                    timestamp=datetime.now().isoformat(),
                    level="INFO", 
                    message="To enable file logging, restart Claude Desktop - the startup script now redirects logs to this file.",
                    source="monitoring"
                )
            ]
        
        # Read the last N lines from the log file
        async with aiofiles.open(log_file, 'r') as f:
            content = await f.read()
        
        if not content.strip():
            # Check if server is running despite empty log file
            import subprocess
            try:
                result = subprocess.run(
                    ["pgrep", "-f", "local_mcp.server"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return [
                        ServerLogEntry(
                            timestamp=datetime.now().isoformat(),
                            level="INFO",
                            message="MCP server is running but logs are not being written to file.",
                            source="monitoring"
                        ),
                        ServerLogEntry(
                            timestamp=datetime.now().isoformat(),
                            level="INFO",
                            message="This happens when Claude Desktop manages the server without log redirection. Restart Claude Desktop to enable file logging.",
                            source="monitoring"
                        )
                    ]
            except:
                pass
            
            return [
                ServerLogEntry(
                    timestamp=datetime.now().isoformat(),
                    level="INFO",
                    message="Log file exists but is empty. No server activity recorded.",
                    source="monitoring"
                )
            ]
        
        # Split into lines and get the last N lines
        log_lines = content.strip().split('\n')
        recent_lines = log_lines[-lines:] if len(log_lines) > lines else log_lines
        
        # Parse log entries
        logs = []
        for line in recent_lines:
            if not line.strip():
                continue
                
            # Try to parse structured log entries
            # Format: "2025-08-26 21:37:42,757 - local_mcp.config - INFO - Loaded global configuration"
            try:
                if ' - ' in line and len(line.split(' - ')) >= 4:
                    parts = line.split(' - ')
                    timestamp = parts[0]
                    source = parts[1]
                    level = parts[2]
                    message = ' - '.join(parts[3:])
                    
                    logs.append(ServerLogEntry(
                        timestamp=timestamp,
                        level=level,
                        message=message,
                        source=source
                    ))
                else:
                    # Handle unstructured log lines (warnings, etc.)
                    logs.append(ServerLogEntry(
                        timestamp=datetime.now().isoformat(),
                        level="INFO",
                        message=line,
                        source="mcp-server"
                    ))
            except Exception:
                # Fallback for any parsing errors
                logs.append(ServerLogEntry(
                    timestamp=datetime.now().isoformat(),
                    level="INFO", 
                    message=line,
                    source="mcp-server"
                ))
        
        return logs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading server logs: {str(e)}")


# Serve static files (React build) when in production
if Path("frontend/dist").exists():
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")


def main():
    """Main entry point for the web server."""
    import uvicorn
    import asyncio
    
    # Ensure required imports are available
    try:
        import asyncio
    except ImportError:
        logger.error("asyncio module not available")
        sys.exit(1)
    
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
