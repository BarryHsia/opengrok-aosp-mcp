# OpenGrok AOSP MCP Server

A specialized Model Context Protocol (MCP) server for Android Open Source Project (AOSP) development, providing intelligent code navigation and analysis through OpenGrok.

## Features

### Basic Code Search (5 tools)
- **search_definitions** - Find symbol definitions (functions, classes, methods)
- **search_references** - Find symbol references/usage points
- **search_full** - Full-text search with regex support
- **get_file_content** - Retrieve file content with line range support
- **list_projects** - List all available OpenGrok projects

### AOSP-Specific Tools (13 tools)
- **trace_binder_chain** - Trace Binder IPC call chains across Java/JNI/Native layers
- **find_aidl_impl** - Analyze AIDL interfaces (Stub/Proxy/registration)
- **analyze_system_service** - System Service lifecycle analysis
- **trace_permission** - Permission check path tracing
- **find_hal_interface** - HAL interface definition and usage (HIDL/AIDL)
- **find_jni_bridge** - Java-Native bridging analysis
- **analyze_build_module** - Build system module analysis (Android.bp/mk)
- **trace_broadcast** - Broadcast flow tracing (senders/receivers)
- **search_selinux_policy** - SELinux policy search
- **find_resource_overlay** - Framework resource and RRO analysis
- **trace_init_service** - Init process service tracing
- **find_hidl_passthrough** - HIDL Passthrough mode analysis
- **analyze_vintf_manifest** - VINTF manifest analysis

### Intelligent Tools (2 tools)
- **explain_code_flow** - Smart code flow explanation (combines multiple tools)
- **find_similar_patterns** - Find similar code patterns (AST-based)

## Token Optimization

This server is designed to minimize token consumption:
- Concise tool descriptions (<50 words)
- Abbreviated return paths (e.g., `f/b/services/...`)
- Limited result sets (default 10, max 50)
- Smart caching (24h for AOSP code)
- Snippet-only responses with clickable URLs

## Installation

### Prerequisites
- Python 3.10+
- OpenGrok server with API access
- `uv` package manager (recommended)

### Quick Install

```bash
# Clone repository
git clone https://github.com/your-org/opengrok-aosp-mcp.git
cd opengrok-aosp-mcp

# Run install script
./install.sh
```

The script will:
1. Check Python version
2. Install `uv` if needed
3. Create virtual environment and install dependencies
4. Generate config file
5. Output Kiro configuration example

### Manual Install

```bash
# Install dependencies
uv sync

# Configure OpenGrok
cp config.example.json config.json
# Edit config.json with your OpenGrok URL and token

# Test run
uv run python server.py
```

## Configuration

### OpenGrok Setup

Your OpenGrok server needs API token authentication enabled. Add to read-only config:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<java version="1.8.0_121" class="java.beans.XMLDecoder">
  <object class="org.opengrok.indexer.configuration.Configuration">
    <void property="authenticationTokens">
      <void method="add">
        <string>your-token</string>
      </void>
    </void>
    <void property="allowInsecureTokens">
      <boolean>true</boolean>
    </void>
  </object>
</java>
```

### Kiro CLI Configuration

Add to `~/.kiro/settings/mcp.json` (global) or `.kiro/settings/mcp.json` (workspace):

```json
{
  "mcpServers": {
    "opengrok-aosp": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/opengrok-aosp-mcp",
        "run",
        "python",
        "server.py"
      ],
      "env": {
        "OPENGROK_BASE_URL": "http://your-opengrok:8080/source",
        "OPENGROK_TOKEN": "your-token-here"
      }
    }
  }
}
```

### Trust Tools (Optional)

To avoid confirmation prompts in Kiro:

```bash
# In Kiro chat
/tools trust-all

# Or trust specific tools
/tools trust search_definitions search_references
```

## Usage Examples

### Basic Search
```
User: Find the definition of ActivityManagerService
Kiro: [calls search_definitions("ActivityManagerService")]
```

### AOSP-Specific Analysis
```
User: Trace the Binder call chain from IActivityManager.startActivity
Kiro: [calls trace_binder_chain("IActivityManager", "startActivity")]

User: Where is the CAMERA permission checked?
Kiro: [calls trace_permission("android.permission.CAMERA")]

User: Find the JNI bridge for android.os.Process
Kiro: [calls find_jni_bridge("android.os.Process")]
```

## Development Roadmap

- [x] **Milestone 1**: Basic framework + 5 basic search tools
- [ ] **Milestone 2**: AIDL + Binder analysis tools
- [ ] **Milestone 3**: System Service + JNI tools
- [ ] **Milestone 4-7**: Remaining AOSP tools
- [ ] **Milestone 8**: Intelligent analysis tools

## Uninstall

```bash
# 1. Remove from Kiro config (~/.kiro/settings/mcp.json)
# 2. Delete project directory
rm -rf /path/to/opengrok-aosp-mcp
```

## Architecture

### Token Optimization Strategy
1. **Concise descriptions**: Tool descriptions <50 words
2. **Path abbreviation**: `frameworks/base/...` → `f/b/...`
3. **Snippet-only**: Return 5 key lines + clickable URL
4. **Smart caching**: 24h cache for AOSP code (slow-changing)
5. **Result limits**: Default 10, max 50 results

### Project Structure
```
opengrok-aosp-mcp/
├── README.md                    # This file
├── pyproject.toml              # Dependencies
├── server.py                   # MCP entry point
├── config.example.json         # Config template
├── install.sh                  # Install script
├── core/
│   ├── opengrok_client.py     # OpenGrok API wrapper
│   ├── cache.py               # Query cache
│   └── token_optimizer.py     # Token optimization
├── tools/
│   ├── basic.py               # 5 basic search tools
│   ├── aidl.py                # AIDL tools
│   ├── binder.py              # Binder tools
│   └── ...                    # Other AOSP tools
└── tests/
    └── test_basic.py
```

## Common AOSP Development Scenarios

### Scenario 1: Trace Binder Call Chain
**Problem**: "How does ActivityManagerService.startActivity reach Zygote?"
**Solution**: `trace_binder_chain("IActivityManager", "startActivity")`

### Scenario 2: Find AIDL Implementation
**Problem**: "Where is IWindowManager.aidl implemented?"
**Solution**: `find_aidl_impl("IWindowManager")`

### Scenario 3: System Service Startup
**Problem**: "When does PowerManagerService start?"
**Solution**: `analyze_system_service("power")`

### Scenario 4: Permission Check Path
**Problem**: "Where is CAMERA permission enforced?"
**Solution**: `trace_permission("android.permission.CAMERA")`

### Scenario 5: HAL Interface
**Problem**: "Where is Camera HAL defined?"
**Solution**: `find_hal_interface("camera", "aidl")`

### Scenario 6: JNI Bridge
**Problem**: "How does android.os.Process call native code?"
**Solution**: `find_jni_bridge("android.os.Process")`

## Contributing

Contributions welcome! Please:
1. Follow existing code style
2. Add tests for new tools
3. Update README with new features
4. Keep token optimization in mind

## License

Apache 2.0

## Credits

- Based on [opengrok-mcp](https://github.com/SleepyDog053/opengrok-mcp) by SleepyDog053
- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Designed for [Kiro CLI](https://kiro.dev)
