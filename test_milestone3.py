#!/usr/bin/env python3
"""测试 Milestone 3 工具（System Service + JNI）"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import OpenGrokClient, QueryCache, TokenOptimizer
from tools import SystemServiceJniTools


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def test_analyze_system_service(tools):
    """测试 analyze_system_service"""
    print_header("工具 1/3: analyze_system_service")
    
    print("\n【功能】分析系统服务生命周期（启动、注册、获取）")
    print("【参数】service_name (必需), limit")
    
    print("\n【示例】分析 ActivityManagerService")
    print("调用: analyze_system_service('activity', limit=3)")
    
    try:
        result = tools.analyze_system_service("activity", limit=3)
        
        print(f"\n结果:")
        print(f"  服务类: {len(result['service_class'])} 条")
        for s in result['service_class'][:2]:
            print(f"    {s.get('path')}:{s.get('line')}")
        
        print(f"  服务注册: {len(result['registration'])} 条")
        for r in result['registration'][:2]:
            print(f"    {r.get('path')}:{r.get('line')}")
        
        print(f"  启动逻辑: {len(result['startup'])} 条")
        for s in result['startup'][:2]:
            print(f"    {s.get('path')}:{s.get('line')}")
        
        print(f"  客户端使用: {len(result['client_usage'])} 条")
        for c in result['client_usage'][:2]:
            print(f"    {c.get('path')}:{c.get('line')}")
        
        if not any([result['service_class'], result['registration'], result['startup'], result['client_usage']]):
            print("  (OpenGrok 可能还在索引中，暂无结果)")
            
    except Exception as e:
        print(f"  错误: {e}")


def test_find_jni_bridge(tools):
    """测试 find_jni_bridge"""
    print_header("工具 2/3: find_jni_bridge")
    
    print("\n【功能】查找 Java-Native 桥接（JNI 方法和实现）")
    print("【参数】java_class (必需), limit")
    
    print("\n【示例】查找 android.os.Process 的 JNI 桥接")
    print("调用: find_jni_bridge('android.os.Process', limit=3)")
    
    try:
        result = tools.find_jni_bridge("android.os.Process", limit=3)
        
        print(f"\n结果:")
        print(f"  Java native 方法: {len(result['java_native_methods'])} 条")
        for j in result['java_native_methods'][:2]:
            print(f"    {j.get('path')}:{j.get('line')}")
        
        print(f"  JNI 注册: {len(result['jni_registration'])} 条")
        for j in result['jni_registration'][:2]:
            print(f"    {j.get('path')}:{j.get('line')}")
        
        print(f"  Native 实现: {len(result['native_impl'])} 条")
        for n in result['native_impl'][:2]:
            print(f"    {n.get('path')}:{n.get('line')}")
        
        if not any([result['java_native_methods'], result['jni_registration'], result['native_impl']]):
            print("  (OpenGrok 可能还在索引中，暂无结果)")
            
    except Exception as e:
        print(f"  错误: {e}")


def test_trace_permission(tools):
    """测试 trace_permission"""
    print_header("工具 3/3: trace_permission")
    
    print("\n【功能】追踪权限检查路径")
    print("【参数】permission (必需), limit")
    
    print("\n【示例】追踪 CAMERA 权限")
    print("调用: trace_permission('android.permission.CAMERA', limit=3)")
    
    try:
        result = tools.trace_permission("android.permission.CAMERA", limit=3)
        
        print(f"\n结果:")
        print(f"  权限定义: {len(result['permission_definition'])} 条")
        for p in result['permission_definition'][:2]:
            print(f"    {p.get('path')}:{p.get('line')}")
        
        print(f"  检查点: {len(result['check_points'])} 条")
        for c in result['check_points'][:2]:
            print(f"    {c.get('path')}:{c.get('line')}")
        
        print(f"  强制执行: {len(result['enforcement'])} 条")
        for e in result['enforcement'][:2]:
            print(f"    {e.get('path')}:{e.get('line')}")
        
        if not any([result['permission_definition'], result['check_points'], result['enforcement']]):
            print("  (OpenGrok 可能还在索引中，暂无结果)")
            
    except Exception as e:
        print(f"  错误: {e}")


def show_return_format():
    """展示返回格式"""
    print_header("返回数据格式")
    
    print("\n【analyze_system_service】")
    print(json.dumps({
        "service_class": [],
        "registration": [],
        "startup": [],
        "client_usage": []
    }, indent=2, ensure_ascii=False))
    
    print("\n【find_jni_bridge】")
    print(json.dumps({
        "java_native_methods": [],
        "jni_registration": [],
        "native_impl": []
    }, indent=2, ensure_ascii=False))
    
    print("\n【trace_permission】")
    print(json.dumps({
        "permission_definition": [],
        "check_points": [],
        "enforcement": []
    }, indent=2, ensure_ascii=False))


def main():
    """主函数"""
    print_header("Milestone 3: System Service + JNI 工具测试")
    
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
    tools = SystemServiceJniTools(client, cache, optimizer)
    
    # 测试工具
    test_analyze_system_service(tools)
    test_find_jni_bridge(tools)
    test_trace_permission(tools)
    
    # 展示返回格式
    show_return_format()
    
    # 总结
    print_header("测试完成")
    print("\n✅ Milestone 3 工具测试完成")
    print("\n📝 在 Kiro 中使用:")
    print("   analyze_system_service('activity')")
    print("   find_jni_bridge('android.os.Process')")
    print("   trace_permission('android.permission.CAMERA')")
    print()


if __name__ == "__main__":
    main()
