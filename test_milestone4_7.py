#!/usr/bin/env python3
"""测试 Milestone 4-7 工具（Advanced AOSP）"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import OpenGrokClient, QueryCache, TokenOptimizer
from tools import AdvancedAospTools


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def test_all_tools(tools):
    """测试所有 6 个工具"""
    
    # 1. find_hal_interface
    print_header("工具 1/6: find_hal_interface")
    print("【功能】查找 HAL 接口定义和实现")
    print("【示例】find_hal_interface('camera', 'aidl', limit=2)")
    try:
        result = tools.find_hal_interface("camera", "aidl", limit=2)
        print(f"✓ 接口: {len(result['interface'])} 条")
        print(f"✓ 实现: {len(result['implementation'])} 条")
        print(f"✓ 使用: {len(result['client_usage'])} 条")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    # 2. trace_broadcast
    print_header("工具 2/6: trace_broadcast")
    print("【功能】追踪广播流程（发送者和接收者）")
    print("【示例】trace_broadcast('android.intent.action.BOOT_COMPLETED', limit=2)")
    try:
        result = tools.trace_broadcast("android.intent.action.BOOT_COMPLETED", limit=2)
        print(f"✓ 发送者: {len(result['senders'])} 条")
        print(f"✓ 接收者: {len(result['receivers'])} 条")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    # 3. search_selinux_policy
    print_header("工具 3/6: search_selinux_policy")
    print("【功能】搜索 SELinux 策略")
    print("【示例】search_selinux_policy('camera', limit=2)")
    try:
        result = tools.search_selinux_policy("camera", limit=2)
        print(f"✓ 找到: {len(result)} 条策略")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    # 4. find_resource_overlay
    print_header("工具 4/6: find_resource_overlay")
    print("【功能】查找 Framework 资源和 RRO")
    print("【示例】find_resource_overlay('config_enableTranslucentDecor', limit=2)")
    try:
        result = tools.find_resource_overlay("config_enableTranslucentDecor", limit=2)
        print(f"✓ Framework 资源: {len(result['framework_resource'])} 条")
        print(f"✓ RRO 覆盖: {len(result['overlay'])} 条")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    # 5. trace_init_service
    print_header("工具 5/6: trace_init_service")
    print("【功能】追踪 Init 进程服务")
    print("【示例】trace_init_service('surfaceflinger', limit=2)")
    try:
        result = tools.trace_init_service("surfaceflinger", limit=2)
        print(f"✓ init.rc: {len(result['init_rc'])} 条")
        print(f"✓ 服务代码: {len(result['service_code'])} 条")
    except Exception as e:
        print(f"✗ 错误: {e}")
    
    # 6. analyze_build_module
    print_header("工具 6/6: analyze_build_module")
    print("【功能】分析构建系统模块")
    print("【示例】analyze_build_module('framework', limit=2)")
    try:
        result = tools.analyze_build_module("framework", limit=2)
        print(f"✓ Android.bp: {len(result['android_bp'])} 条")
        print(f"✓ Android.mk: {len(result['android_mk'])} 条")
    except Exception as e:
        print(f"✗ 错误: {e}")


def main():
    """主函数"""
    print_header("Milestone 4-7: Advanced AOSP 工具测试")
    
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
    tools = AdvancedAospTools(client, cache, optimizer)
    
    # 测试所有工具
    test_all_tools(tools)
    
    # 总结
    print_header("测试完成")
    print("\n✅ Milestone 4-7 工具测试完成")
    print("\n📝 在 Kiro 中使用:")
    print("   find_hal_interface('camera', 'aidl')")
    print("   trace_broadcast('android.intent.action.BOOT_COMPLETED')")
    print("   search_selinux_policy('camera')")
    print("   find_resource_overlay('config_enableTranslucentDecor')")
    print("   trace_init_service('surfaceflinger')")
    print("   analyze_build_module('framework')")
    print()


if __name__ == "__main__":
    main()
