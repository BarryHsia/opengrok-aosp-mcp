"""OpenGrok AOSP MCP Server - Main entry point."""
import json
import os
from pathlib import Path
from typing import Optional
from mcp.server.fastmcp import FastMCP

from core import OpenGrokClient, QueryCache, TokenOptimizer
from tools import BasicTools, AidlBinderTools


# Load configuration
def load_config() -> dict:
    """Load configuration from file or environment."""
    config_path = Path("config.json")
    
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    else:
        # Fallback to environment variables
        config = {
            "opengrok": {
                "base_url": os.environ.get("OPENGROK_BASE_URL", "http://localhost:8080/source"),
                "token": os.environ.get("OPENGROK_TOKEN"),
            },
            "cache": {
                "enabled": True,
                "ttl_hours": 24,
                "directory": ".cache",
            },
            "limits": {
                "default_results": 10,
                "max_results": 50,
                "max_snippet_lines": 5,
            },
            "token_optimization": {
                "abbreviate_paths": True,
                "path_prefixes": {
                    "frameworks/base": "f/b",
                    "frameworks/native": "f/n",
                    "system/core": "s/c",
                    "hardware/interfaces": "h/i",
                    "packages/apps": "p/a",
                },
            },
        }
    
    return config


# Initialize MCP server
mcp = FastMCP("opengrok-aosp")

# Load config and initialize components
config = load_config()
client = OpenGrokClient(
    base_url=config["opengrok"]["base_url"],
    token=config["opengrok"]["token"],
)
cache = QueryCache(
    cache_dir=config["cache"]["directory"],
    ttl_hours=config["cache"]["ttl_hours"],
) if config["cache"]["enabled"] else None
optimizer = TokenOptimizer(config)

# Initialize tools
basic_tools = BasicTools(client, cache, optimizer)
aidl_binder_tools = AidlBinderTools(client, cache, optimizer)


# Register MCP tools
@mcp.tool()
def search_definitions(
    symbol: str,
    project: Optional[str] = None,
    path: Optional[str] = None,
    file_type: Optional[str] = None,
    limit: int = 10,
):
    """Find symbol definitions (functions, classes, methods)."""
    return basic_tools.search_definitions(symbol, project, path, file_type, limit)


@mcp.tool()
def search_references(
    symbol: str,
    project: Optional[str] = None,
    path: Optional[str] = None,
    file_type: Optional[str] = None,
    limit: int = 10,
):
    """Find symbol references/usage points."""
    return basic_tools.search_references(symbol, project, path, file_type, limit)


@mcp.tool()
def search_full(
    query: str,
    project: Optional[str] = None,
    path: Optional[str] = None,
    file_type: Optional[str] = None,
    limit: int = 10,
):
    """Full-text search across codebase (supports regex)."""
    return basic_tools.search_full(query, project, path, file_type, limit)


@mcp.tool()
def get_file_content(
    path: str,
    start_line: int = 1,
    end_line: int = 50,
):
    """Get file content with line range."""
    return basic_tools.get_file_content(path, start_line, end_line)


@mcp.tool()
def list_projects():
    """List all available OpenGrok projects."""
    return basic_tools.list_projects()


# AIDL and Binder tools
@mcp.tool()
def find_aidl_impl(
    interface_name: str,
    limit: int = 10,
):
    """Analyze AIDL interface (Stub/Proxy/registration)."""
    return aidl_binder_tools.find_aidl_impl(interface_name, limit)


@mcp.tool()
def trace_binder_chain(
    interface_name: str,
    method_name: str,
    limit: int = 10,
):
    """Trace Binder IPC call chain (Java -> JNI -> Native)."""
    return aidl_binder_tools.trace_binder_chain(interface_name, method_name, limit)


if __name__ == "__main__":
    mcp.run()
