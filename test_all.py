#!/usr/bin/env python3
"""Test all 5 basic tools."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import OpenGrokClient, QueryCache, TokenOptimizer
from tools import BasicTools


def test_tools():
    """Test all 5 basic tools."""
    with open("config.json") as f:
        config = json.load(f)
    
    client = OpenGrokClient(
        base_url=config["opengrok"]["base_url"],
        token=config["opengrok"]["token"],
    )
    cache = QueryCache(
        cache_dir=config["cache"]["directory"],
        ttl_hours=config["cache"]["ttl_hours"],
    )
    optimizer = TokenOptimizer(config)
    tools = BasicTools(client, cache, optimizer)
    
    print("=" * 60)
    print("Testing OpenGrok AOSP MCP Tools")
    print("=" * 60)
    
    # Test 1: search_definitions
    print("\n[1/5] search_definitions('ActivityManagerService')...")
    try:
        results = tools.search_definitions("ActivityManagerService", limit=3)
        print(f"✓ Found {len(results)} results")
        for r in results[:2]:
            print(f"  {r.get('path')}:{r.get('line')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: search_references
    print("\n[2/5] search_references('startActivity')...")
    try:
        results = tools.search_references("startActivity", limit=3)
        print(f"✓ Found {len(results)} results")
        for r in results[:2]:
            print(f"  {r.get('path')}:{r.get('line')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: search_full
    print("\n[3/5] search_full('Binder transaction')...")
    try:
        results = tools.search_full("Binder transaction", limit=3)
        print(f"✓ Found {len(results)} results")
        for r in results[:2]:
            print(f"  {r.get('path')}:{r.get('line')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: get_file_content
    print("\n[4/5] get_file_content()...")
    try:
        result = tools.get_file_content(
            "frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java",
            start_line=1,
            end_line=20
        )
        print(f"✓ Retrieved lines 1-{result.get('end_line')} from {result.get('path')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: list_projects
    print("\n[5/5] list_projects()...")
    try:
        projects = tools.list_projects()
        print(f"✓ Found {len(projects)} projects")
        for p in projects[:5]:
            print(f"  {p}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_tools()
