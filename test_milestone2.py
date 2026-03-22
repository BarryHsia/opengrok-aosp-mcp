#!/usr/bin/env python3
"""测试 Milestone 2 工具（AIDL + Binder）"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import OpenGrokClient, QueryCache, TokenOptimizer
from tools import AidlBinderTools


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def test_find_aidl_impl(tools):
    """测试 find_aidl_impl"""
    print_header("工具 1/2: find_aidl_impl")
    
    print("\n【功能】分析 AIDL 接口（Stub/Proxy/注册）")
    print("【参数】interface_name (必需), limit")
    
    print("\n【示例】分析 IActivityManager 接口")
    print("调用: find_aidl_impl('IActivityManager', limit=3)")
    
    try:
        result = tools.find_aidl_impl("IActivityManager", limit=3)
        
        print(f"\n结果:")
        print(f"  接口定义: {1 if result['interface'] else 0} 条")
        if result['interface']:
            print(f"    {result['interface'].get('path')}")
        
        print(f"  Stub 实现: {len(result['stub'])} 条")
        for s in result['stub'][:2]:
            print(f"    {s.get('path')}:{s.get('line')}")
        
        print(f"  Proxy 实现: {len(result['proxy'])} 条")
        for p in result['proxy'][:2]:
            print(f"    {p.get('path')}:{p.get('line')}")
        
        print(f"  服务注册: {len(result['registration'])} 条")
        for r in result['registration'][:2]:
            print(f"    {r.get('path')}:{r.get('line')}")
        
        if not any([result['interface'], result['stub'], result['proxy'], result['registration']]):
            print("  (OpenGrok 可能还在索引中，暂无结果)")
            
    except Exception as e:
        print(f"  错误: {e}")


def test_trace_binder_chain(tools):
    """测试 trace_binder_chain"""
    print_header("工具 2/2: trace_binder_chain")
    
    print("\n【功能】追踪 Binder IPC 调用链（Java -> JNI -> Native）")
    print("【参数】interface_name (必需), method_name (必需), limit")
    
    print("\n【示例】追踪 IActivityManager.startActivity 调用链")
    print("调用: trace_binder_chain('IActivityManager', 'startActivity', limit=3)")
    
    try:
        result = tools.trace_binder_chain("IActivityManager", "startActivity", limit=3)
        
        print(f"\n结果:")
        print(f"  Java 接口: {len(result['java_interface'])} 条")
        for j in result['java_interface'][:2]:
            print(f"    {j.get('path')}:{j.get('line')}")
        
        print(f"  Java 实现: {len(result['java_impl'])} 条")
        for j in result['java_impl'][:2]:
            print(f"    {j.get('path')}:{j.get('line')}")
        
        print(f"  JNI 桥接: {len(result['jni_bridge'])} 条")
        for j in result['jni_bridge'][:2]:
            print(f"    {j.get('path')}:{j.get('line')}")
        
        print(f"  Native 实现: {len(result['native_impl'])} 条")
        for n in result['native_impl'][:2]:
            print(f"    {n.get('path')}:{n.get('line')}")
        
        if not any([result['java_interface'], result['java_impl'], result['jni_bridge'], result['native_impl']]):
            print("  (OpenGrok 可能还在索引中，暂无结果)")
            
    except Exception as e:
        print(f"  错误: {e}")


def show_return_format():
    """展示返回格式"""
    print_header("返回数据格式")
    
    print("\n【find_aidl_impl】")
    print(json.dumps({
        "interface": {
            "path": "f/b/core/java/android/app/IActivityManager.aidl",
            "line": 1,
            "snippet": "interface IActivityManager {",
            "url": "http://localhost:8080/xref/..."
        },
        "stub": [
            {
                "path": "f/b/core/java/android/app/IActivityManager.java",
                "line": 123,
                "snippet": "public static abstract class Stub extends Binder",
                "url": "http://localhost:8080/xref/..."
            }
        ],
        "proxy": [],
        "registration": []
    }, indent=2, ensure_ascii=False))
    
    print("\n【trace_binder_chain】")
    print(json.dumps({
        "java_interface": [],
        "java_impl": [],
        "jni_bridge": [],
        "native_impl": []
    }, indent=2, ensure_ascii=False))


def main():
    """主函数"""
    print_header("Milestone 2: AIDL + Binder 工具测试")
    
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
    tools = AidlBinderTools(client, cache, optimizer)
    
    # 测试工具
    test_find_aidl_impl(tools)
    test_trace_binder_chain(tools)
    
    # 展示返回格式
    show_return_format()
    
    # 总结
    print_header("测试完成")
    print("\n✅ Milestone 2 工具测试完成")
    print("\n📝 在 Kiro 中使用:")
    print("   find_aidl_impl('IActivityManager')")
    print("   trace_binder_chain('IActivityManager', 'startActivity')")
    print()


if __name__ == "__main__":
    main()
