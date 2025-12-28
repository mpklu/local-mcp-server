# Tool Discovery System

## Overview

The Local MCP Server uses an **automatic discovery system** to find and configure tools. Tools are defined by their directory structure and standardized `run.sh` entry points, with metadata extracted from annotations and documentation.

**Key Principle:** Tools are self-describing through their `run.sh` files with `@param` annotations.

---

## Discovery Workflow

### 1. Directory Scanning

The system scans a specified tools directory:

```bash
tools/
├── pwod/
│   ├── run.sh              # REQUIRED: Universal entry point
│   ├── manager.py          # Tool implementation
│   ├── requirements.txt    # Dependencies
│   └── README.md           # Documentation
├── file-ops/
│   ├── run.sh
│   ├── manager.py
│   └── ...
└── TEMPLATE/
    └── run.sh
```

**Requirements:**
- Each tool = one directory
- Must contain executable `run.sh`
- Tool name = directory name

### 2. Metadata Extraction

For each tool found, discovery extracts:

**From run.sh header:**
```bash
#!/bin/bash
# Tool: pwod
# Description: Password of the Day - Generate deterministic passwords
#
# @param function: The function to execute (type: string, required: true)
# @param date_string: Date in YYYY-MM-DD format (type: string, required: false)
# @param custom_string: Custom string (type: string, required: false)
```

**Extracted:**
- Tool name and description
- Parameter names, types, descriptions
- Required/optional flags
- Default values

**From file analysis:**
- Script type (shell/python)
- Dependencies from requirements.txt
- Interactive mode detection

### 3. Config Generation

Two-tier configuration system:

**Individual Configs** (`config/tools/toolname.json`):
```json
{
  "enabled": true,
  "last_modified": "2025-12-27T14:23:16.947111",
  "auto_detected": true,
  "created_by": "discovery_tool",
  "tags": [],
  "script_config": {
    "name": "pwod",
    "title": null,
    "description": "Password of the Day...",
    "script_path": "pwod/run.sh",
    "script_type": "shell",
    "requires_confirmation": false,
    "parameters": [
      {
        "name": "function",
        "type": "string",
        "description": "The function to execute",
        "required": true
      }
    ],
    "interactive": false,
    "workspace_config": {
      "allowed_paths": ["{TOOL_DIR}/workspace"],
      "allow_absolute_paths": false,
      "follow_symlinks": true
    }
  }
}
```

**Compiled Config** (`config/tools.json`):
- Merged from all individual configs
- Used by server at runtime
- Only includes enabled tools

---

## Discovery Commands

### Run Full Discovery

Scans tools directory, creates/updates individual configs:

```bash
cd server
uv run python discover_tools.py --tools-dir /path/to/tools
```

**Options:**
- `--tools-dir PATH` - Override default tools directory
- `--list` - Show discovered tools status
- `--force` - Force full re-discovery (ignore timestamps)

**Output:**
```
2025-12-27 14:23:16,945 - INFO - Discovered 1 tools
2025-12-27 14:23:16,947 - INFO - ✅ Created config for: pwod
```

### Build Compiled Config

Merges individual configs into runtime config:

```bash
cd server
uv run python build_tools.py
```

**Output:**
```
2025-12-27 14:23:17,382 - INFO - Successfully built tools.json with 7 enabled tools
```

**When to rebuild:**
- After discovery
- After manually editing individual configs
- After enabling/disabling tools

### List Tools

Check discovery status:

```bash
cd server
uv run python discover_tools.py --tools-dir /path/to/tools --list
```

**Output:**
```
📋 Tool Configuration Status:
==================================================
✅ 📁 pwod
     Path: /path/to/tools/pwod
     Desc: Password of the Day...

✅ 🚫 old-tool
     ⚠️  Config exists but tool not found in filesystem

Legend:
  ✅/❌ = Has/Missing individual config file
  📁/🚫 = Found/Missing in tools directory
```

---

## Configuration Tiers

### Tier 1: Individual Configs

**Location:** `server/config/tools/*.json`

**Purpose:**
- Store per-tool settings
- Enable/disable individual tools
- Override auto-detected metadata
- Manual customization

**Editing:**
```bash
vim server/config/tools/pwod.json
# Change requires_confirmation, add tags, etc.
```

### Tier 2: Compiled Config

**Location:** `server/config/tools.json`

**Purpose:**
- Runtime configuration
- Loaded by server on startup
- Contains only enabled tools
- Optimized for fast loading

**Regeneration:**
```bash
cd server
uv run python build_tools.py
```

---

## Parameter Annotation System

### Format

```bash
# @param name: description (type: TYPE, required: BOOL, default: VALUE)
```

### Supported Types

- `string` - Text values
- `integer` - Whole numbers  
- `number` - Floating point numbers
- `boolean` - true/false values
- `array` - Lists of values
- `object` - Complex objects

### Examples

```bash
# Required string parameter
# @param input_file: Path to input file (type: string, required: true)

# Optional with default
# @param count: Number of iterations (type: integer, required: false, default: 10)

# Boolean flag
# @param verbose: Enable verbose output (type: boolean, required: false, default: false)

# Optional string
# @param format: Output format (type: string, required: false)
```

### Parsing

Discovery uses regex to extract annotations:

```python
pattern = r'@param\s+(\w+):\s*([^(]+)\s*\(type:\s*(\w+)(?:,\s*required:\s*(true|false))?(?:,\s*default:\s*([^)]+))?\)'
```

**Extracted fields:**
1. Parameter name
2. Description
3. Type
4. Required flag (defaults to false)
5. Default value (optional)

---

## Discovery Modes

### Incremental Discovery (Default)

Checks file modification times, only rescans changed tools:

```bash
uv run python discover_tools.py --tools-dir /path/to/tools
```

**Fast:** Skips unchanged tools

### Full Discovery (Force)

Rescans all tools regardless of timestamps:

```bash
uv run python discover_tools.py --tools-dir /path/to/tools --force
```

**Slower:** Use when metadata is corrupted or major changes

---

## Integration with Server

### Server Startup

1. Load compiled config: `config/tools.json`
2. Instantiate tool executors
3. Register tools with MCP protocol
4. Ready to serve requests

### Lazy Discovery

Server can optionally check for changes at startup:

```bash
# In start_server.sh
--discover        # Incremental check
--force-discover  # Full rescan
```

**Tradeoff:**
- **No discovery:** Fast startup, may miss new tools
- **Incremental:** Slight delay, catches new/changed tools
- **Force:** Slow startup, guaranteed fresh config

---

## Tool Metadata

### Auto-Detected

From run.sh analysis:
- ✅ Name (from directory)
- ✅ Description (from header comment)
- ✅ Parameters (from @param annotations)
- ✅ Script type (shell/python detection)
- ✅ Dependencies (from requirements.txt)

### Manual Configuration

Edit individual config for:
- `requires_confirmation` - Require user approval
- `enabled` - Enable/disable tool
- `tags` - Categorization
- `title` - Human-friendly display name
- `read_only` - Tool only reads data
- `destructive` - Tool performs destructive operations
- `workspace_config` - Path security settings

---

## Common Workflows

### Adding a New Tool

1. **Create tool directory:**
   ```bash
   mkdir tools/my-tool
   ```

2. **Add run.sh with annotations:**
   ```bash
   cp tools/TEMPLATE/run.sh tools/my-tool/run.sh
   # Edit and add @param annotations
   ```

3. **Run discovery:**
   ```bash
   cd server
   uv run python discover_tools.py --tools-dir ../tools
   uv run python build_tools.py
   ```

4. **Test:**
   ```bash
   cd ../tools/my-tool
   ./run.sh --health
   ```

### Updating Tool Parameters

1. **Edit run.sh @param annotations**
2. **Force rediscovery:**
   ```bash
   cd server
   uv run python discover_tools.py --tools-dir ../tools --force
   uv run python build_tools.py
   ```

3. **Restart server** (or refresh in Inspector)

### Disabling a Tool

**Option 1: Individual config**
```bash
vim server/config/tools/my-tool.json
# Change "enabled": true to "enabled": false
uv run python build_tools.py
```

**Option 2: Remove from filesystem**
```bash
rm -rf tools/my-tool
# Discovery will mark as missing
```

---

## Development Testing

### Quick Iteration

Use the test script with skip flags:

```bash
# First run - full discovery
./test_with_inspector.sh

# Subsequent runs - skip discovery
./test_with_inspector.sh --skip-discovery

# Fastest - skip all checks
./test_with_inspector.sh -s -d
```

### Manual Testing

Test tool directly without server:

```bash
cd tools/my-tool
./run.sh function_name --param="value"
```

Test with Inspector:

```bash
./test_with_inspector.sh
# Opens http://localhost:6274
# Connect → Call tools
```

---

## Troubleshooting

### Tool Not Discovered

**Check:**
1. Is `run.sh` present and executable?
   ```bash
   ls -la tools/my-tool/run.sh
   chmod +x tools/my-tool/run.sh
   ```

2. Are @param annotations correct?
   ```bash
   grep "@param" tools/my-tool/run.sh
   ```

3. Run with verbose output:
   ```bash
   cd server
   uv run python discover_tools.py --tools-dir ../tools --list
   ```

### Parameters Not Showing

**Cause:** @param annotations not parsed

**Fix:**
1. Check annotation format matches exactly
2. Ensure no syntax errors in run.sh
3. Force rediscovery:
   ```bash
   rm server/config/tools/my-tool.json
   uv run python discover_tools.py --tools-dir ../tools --force
   ```

### Config Not Updating

**Cause:** Forgot to rebuild

**Fix:**
```bash
cd server
uv run python build_tools.py
# Restart server or refresh Inspector
```

### JSON Serialization Error

**Cause:** Pydantic model serialization issue (fixed in Dec 2025)

**Symptom:**
```
ERROR - Object of type WorkspaceConfig is not JSON serializable
```

**Fix:** Update to latest server code with Pydantic v2 `model_dump()` support

---

## Discovery System Architecture

### Components

1. **ScriptDiscovery** (`discovery.py`)
   - Scans tool directories
   - Extracts metadata
   - Creates individual configs

2. **Config Manager** (`config.py`)
   - Loads/saves configs
   - Validates structure
   - Manages Pydantic models

3. **discover_tools.py**
   - CLI for discovery operations
   - Orchestrates scanning
   - Reports status

4. **build_tools.py**
   - Merges individual configs
   - Creates compiled config
   - Filters enabled tools

### Data Flow

```
tools/*/run.sh
    ↓ (discovery)
config/tools/*.json
    ↓ (build)
config/tools.json
    ↓ (server startup)
MCP Tool Objects
```

---

## Best Practices

1. **Always document parameters** with @param annotations
2. **Run discovery after** adding/modifying tools
3. **Use --skip-discovery** for rapid iteration
4. **Test directly first** before testing via MCP
5. **Keep run.sh headers accurate** - they're the source of truth
6. **Version control** individual configs for reproducibility
7. **Don't edit** compiled config directly (it gets regenerated)

---

**Last Updated:** December 27, 2025  
**Version:** 2.0.0
