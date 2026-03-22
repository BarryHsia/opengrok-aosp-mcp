#!/usr/bin/env python3
"""测试所有 18 个工具"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import OpenGrokClient, QueryCache, TokenOptimizer
from tools import BasicTools, AidlBinderTools, SystemServiceJniTools, AdvancedAospTools, IntelligentTools


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def main():
    """主函数"""
    print_header("OpenGrok AOSP MCP - 完整工具测试")
    print("\n共 18 个工具，分 5 个类别\n")
    
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
    
    # 初始化所有工具
    basic = BasicTools(client, cache, optimizer)
    aidl_binder = AidlBinderTools(client, cache, optimizer)
    service_jni = SystemServiceJniTools(client, cache, optimizer)
    advanced = AdvancedAospTools(client, cache, optimizer)
    intelligent = IntelligentTools(client, cache, optimizer)
    
    tools = [
        ("基础搜索工具", [
            ("search_definitions", lambda: basic.search_definitions("ActivityManagerService", limit=1)),
            ("search_references", lambda: basic.search_references("startActivity", limit=1)),
            ("search_full", lambda: basic.search_full("Binder", limit=1)),
            ("get_file_content", lambda: basic.get_file_content("frameworks/base/core/java/android/app/Activity.java", 1, 10)),
            ("list_projects", lambda: basic.list_projects()),
        ]),
        ("AIDL + Binder 工具", [
            ("find_aidl_impl", lambda: aidl_binder.find_aidl_impl("IActivityManager", limit=1)),
            ("trace_binder_chain", lambda: aidl_binder.trace_binder_chain("IActivityManager", "startActivity", limit=1)),
        ]),
        ("System Service + JNI 工具", [
            ("analyze_system_service", lambda: service_jni.analyze_system_service("activity", limit=1)),
            ("find_jni_bridge", lambda: service_jni.find_jni_bridge("android.os.Process", limit=1)),
            ("trace_permission", lambda: service_jni.trace_permission("android.permission.CAMERA", limit=1)),
        ]),
        ("Advanced AOSP 工具", [
            ("find_hal_interface", lambda: advanced.find_hal_interface("camera", "aidl", limit=1)),
            ("trace_broadcast", lambda: advanced.trace_broadcast("android.intent.action.BOOT_COMPLETED", limit=1)),
            ("search_selinux_policy", lambda: advanced.search_selinux_policy("camera", limit=1)),
            ("find_resource_overlay", lambda: advanced.find_resource_overlay("config_enableTranslucentDecor", limit=1)),
            ("trace_init_service", lambda: advanced.trace_init_service("surfaceflinger", limit=1)),
            ("analyze_build_module", lambda: advanced.analyze_build_module("framework", limit=1)),
        ]),
        ("Intelligent 工具", [
            ("explain_code_flow", lambda: intelligent.explain_code_flow("startActivity", limit=1)),
            ("find_similar_patterns", lambda: intelligent.find_similar_patterns("synchronized.*notify", limit=1)),
        ]),
    ]
    
    total = 0
    passed = 0
    
    for category, category_tools in tools:
        print_header(category)
        for name, func in category_tools:
            total += 1
            try:
                result = func()
                print(f"  [{total:2d}] ✓ {name}")
                passed += 1
            except Exception as e:
                print(f"  [{total:2d}] ✗ {name}: {str(e)[:50]}")
    
    # 总结
    print_header("测试总结")
    print(f"\n  总计: {total} 个工具")
    print(f"  通过: {passed} 个")
    print(f"  失败: {total - passed} 个")
    print(f"  成功率: {passed*100//total}%")
    
    if passed == total:
        print("\n  🎉 所有工具测试通过！")
    else:
        print(f"\n  ⚠️  {total - passed} 个工具测试失败（可能是 OpenGrok 还在索引）")
    
    print()


if __name__ == "__main__":
    main()
