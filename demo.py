#!/usr/bin/env python3
"""
完整的工具测试和演示脚本

展示所有 5 个工具的使用方法和返回格式
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import OpenGrokClient, QueryCache, TokenOptimizer
from tools import BasicTools


def print_header(title):
    """打印标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def print_tool_info(tool_name, description, params):
    """打印工具信息"""
    print(f"\n【工具】{tool_name}")
    print(f"【功能】{description}")
    print(f"【参数】{params}")


def test_search_definitions(tools):
    """测试 search_definitions"""
    print_tool_info(
        "search_definitions",
        "查找符号定义（函数、类、方法）",
        "symbol (必需), project, path, file_type, limit"
    )
    
    print("\n【示例 1】查找 ActivityManagerService 的定义")
    print("调用: search_definitions('ActivityManagerService', limit=3)")
    
    try:
        results = tools.search_definitions("ActivityManagerService", limit=3)
        print(f"\n结果: 找到 {len(results)} 条")
        
        if results:
            for i, r in enumerate(results, 1):
                print(f"\n  [{i}] {r.get('path')}:{r.get('line')}")
                print(f"      {r.get('snippet', '')[:80]}...")
                print(f"      URL: {r.get('url')}")
        else:
            print("  (OpenGrok 可能还在索引中，暂无结果)")
            
    except Exception as e:
        print(f"  错误: {e}")


def test_search_references(tools):
    """测试 search_references"""
    print_tool_info(
        "search_references",
        "查找符号引用/使用点",
        "symbol (必需), project, path, file_type, limit"
    )
    
    print("\n【示例 2】查找 startActivity 的所有调用")
    print("调用: search_references('startActivity', limit=3)")
    
    try:
        results = tools.search_references("startActivity", limit=3)
        print(f"\n结果: 找到 {len(results)} 条")
        
        if results:
            for i, r in enumerate(results, 1):
                print(f"\n  [{i}] {r.get('path')}:{r.get('line')}")
                print(f"      {r.get('snippet', '')[:80]}...")
        else:
            print("  (OpenGrok 可能还在索引中，暂无结果)")
            
    except Exception as e:
        print(f"  错误: {e}")


def test_search_full(tools):
    """测试 search_full"""
    print_tool_info(
        "search_full",
        "全文搜索（支持正则表达式）",
        "query (必需), project, path, file_type, limit"
    )
    
    print("\n【示例 3】搜索包含 'Binder transaction' 的代码")
    print("调用: search_full('Binder transaction', limit=3)")
    
    try:
        results = tools.search_full("Binder transaction", limit=3)
        print(f"\n结果: 找到 {len(results)} 条")
        
        if results:
            for i, r in enumerate(results, 1):
                print(f"\n  [{i}] {r.get('path')}:{r.get('line')}")
                print(f"      {r.get('snippet', '')[:80]}...")
        else:
            print("  (OpenGrok 可能还在索引中，暂无结果)")
            
    except Exception as e:
        print(f"  错误: {e}")


def test_get_file_content(tools):
    """测试 get_file_content"""
    print_tool_info(
        "get_file_content",
        "获取文件内容（指定行范围）",
        "path (必需), start_line, end_line"
    )
    
    print("\n【示例 4】读取 ActivityManagerService.java 的前 20 行")
    print("调用: get_file_content('frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java', 1, 20)")
    
    try:
        result = tools.get_file_content(
            "frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java",
            start_line=1,
            end_line=20
        )
        
        print(f"\n结果:")
        print(f"  文件: {result.get('path')}")
        print(f"  行范围: {result.get('start_line')}-{result.get('end_line')}")
        print(f"  总行数: {result.get('total_lines')}")
        print(f"\n  内容预览:")
        
        lines = result.get('text', '').split('\n')
        for line in lines[:5]:
            print(f"    {line}")
        if len(lines) > 5:
            print(f"    ... (还有 {len(lines) - 5} 行)")
            
    except Exception as e:
        print(f"  错误: {e}")


def test_list_projects(tools):
    """测试 list_projects"""
    print_tool_info(
        "list_projects",
        "列出所有 OpenGrok 项目",
        "无"
    )
    
    print("\n【示例 5】列出所有项目")
    print("调用: list_projects()")
    
    try:
        projects = tools.list_projects()
        print(f"\n结果: 找到 {len(projects)} 个项目")
        
        for i, p in enumerate(projects[:10], 1):
            print(f"  [{i}] {p}")
        
        if len(projects) > 10:
            print(f"  ... (还有 {len(projects) - 10} 个项目)")
            
    except Exception as e:
        print(f"  错误: {e}")


def show_return_format():
    """展示返回格式"""
    print_header("返回数据格式说明")
    
    print("\n【搜索类工具】search_definitions, search_references, search_full")
    print("返回: List[Dict]")
    print(json.dumps([
        {
            "path": "f/b/services/core/java/com/android/server/am/ActivityManagerService.java",
            "line": 123,
            "snippet": "public class ActivityManagerService extends IActivityManager.Stub",
            "url": "http://localhost:8080/xref/frameworks/base/services/.../ActivityManagerService.java#123"
        }
    ], indent=2, ensure_ascii=False))
    
    print("\n【文件内容工具】get_file_content")
    print("返回: Dict")
    print(json.dumps({
        "path": "f/b/services/core/java/com/android/server/am/ActivityManagerService.java",
        "start_line": 1,
        "end_line": 20,
        "total_lines": 5234,
        "text": "1: package com.android.server.am;\n2: \n3: import android.app.ActivityManager;\n..."
    }, indent=2, ensure_ascii=False))
    
    print("\n【项目列表工具】list_projects")
    print("返回: List[str]")
    print(json.dumps([
        "frameworks",
        "system",
        "hardware",
        "packages"
    ], indent=2, ensure_ascii=False))


def main():
    """主函数"""
    print_header("OpenGrok AOSP MCP 工具测试和演示")
    
    # 加载配置
    with open("config.json") as f:
        config = json.load(f)
    
    # 初始化组件
    client = OpenGrokClient(
        base_url=config["opengrok"]["base_url"],
        token=config["opengrok"]["token"],
    )
    cache = QueryCache(
        cache_dir=config["cache"]["directory"],
        ttl_hours=config["cache"]["ttl_hours"],
    ) if config["cache"]["enabled"] else None
    
    optimizer = TokenOptimizer(config)
    tools = BasicTools(client, cache, optimizer)
    
    # 测试所有工具
    print_header("工具 1/5: search_definitions")
    test_search_definitions(tools)
    
    print_header("工具 2/5: search_references")
    test_search_references(tools)
    
    print_header("工具 3/5: search_full")
    test_search_full(tools)
    
    print_header("工具 4/5: get_file_content")
    test_get_file_content(tools)
    
    print_header("工具 5/5: list_projects")
    test_list_projects(tools)
    
    # 展示返回格式
    show_return_format()
    
    # 总结
    print_header("测试完成")
    print("\n✅ 所有 5 个工具测试完成")
    print("\n📝 在 Kiro 中使用:")
    print("   1. 配置 MCP: 编辑 ~/.kiro/settings/mcp.json")
    print("   2. 启动 Kiro: kiro-cli chat")
    print("   3. 信任工具: /tools trust-all")
    print("   4. 开始使用: '查找 ActivityManagerService 的定义'")
    print()


if __name__ == "__main__":
    main()
