#!/usr/bin/env python3
"""测试 Milestone 8 工具（Intelligent Analysis）"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import OpenGrokClient, QueryCache, TokenOptimizer
from tools import IntelligentTools


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def main():
    """主函数"""
    print_header("Milestone 8: Intelligent Analysis 工具测试")
    
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
    tools = IntelligentTools(client, cache, optimizer)
    
    # 测试 explain_code_flow
    print_header("工具 1/2: explain_code_flow")
    print("【功能】智能代码流程解释（组合多个搜索）")
    print("【示例】explain_code_flow('startActivity', limit=2)")
    try:
        result = tools.explain_code_flow("startActivity", limit=2)
        print(f"✓ 定义: {len(result['definition'])} 条")
        print(f"✓ 引用: {len(result['references'])} 条")
        print(f"✓ 相关代码: {len(result['related_code'])} 条")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    # 测试 find_similar_patterns
    print_header("工具 2/2: find_similar_patterns")
    print("【功能】查找相似代码模式（正则搜索）")
    print("【示例】find_similar_patterns('synchronized.*notify', limit=2)")
    try:
        result = tools.find_similar_patterns("synchronized.*notify", limit=2)
        print(f"✓ 找到: {len(result)} 个相似模式")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    # 总结
    print_header("测试完成")
    print("\n✅ Milestone 8 工具测试完成")
    print("\n📝 在 Kiro 中使用:")
    print("   explain_code_flow('startActivity')")
    print("   find_similar_patterns('synchronized.*notify')")
    print()


if __name__ == "__main__":
    main()
