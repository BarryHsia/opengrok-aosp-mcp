"""AIDL and Binder analysis tools."""
from typing import Any, Dict, List, Optional
from core import OpenGrokClient, QueryCache, TokenOptimizer


class AidlBinderTools:
    """AIDL and Binder analysis tools for AOSP."""
    
    def __init__(self, client: OpenGrokClient, cache: QueryCache, optimizer: TokenOptimizer):
        self.client = client
        self.cache = cache
        self.optimizer = optimizer
    
    def find_aidl_impl(
        self,
        interface_name: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        分析 AIDL 接口实现（Stub/Proxy/注册）。
        
        Args:
            interface_name: AIDL 接口名，如 "IActivityManager"
            limit: 每个类型的最大结果数
        
        Returns:
            {
                "interface": {...},  # AIDL 接口定义
                "stub": [...],       # Stub 实现
                "proxy": [...],      # Proxy 实现
                "registration": [...] # 服务注册点
            }
        """
        cache_key = ("aidl", {"interface": interface_name})
        if self.cache:
            cached = self.cache.get("aidl", cache_key)
            if cached:
                return cached
        
        result = {
            "interface": None,
            "stub": [],
            "proxy": [],
            "registration": []
        }
        
        # 1. 查找 AIDL 接口定义
        aidl_results = self.client.search(
            search_type="def",
            query=interface_name,
            file_type="aidl",
            max_results=5,
        )
        if aidl_results:
            result["interface"] = self.optimizer.optimize_result(aidl_results[0])
        
        # 2. 查找 Stub 实现（通常是 interface_name.Stub）
        stub_results = self.client.search(
            search_type="def",
            query=f"{interface_name}.Stub",
            file_type="java",
            max_results=limit,
        )
        result["stub"] = self.optimizer.optimize_results(stub_results)
        
        # 3. 查找 Proxy 实现
        proxy_results = self.client.search(
            search_type="def",
            query=f"{interface_name}.Proxy",
            file_type="java",
            max_results=limit,
        )
        result["proxy"] = self.optimizer.optimize_results(proxy_results)
        
        # 4. 查找服务注册（addService）
        registration_results = self.client.search(
            search_type="full",
            query=f"addService.*{interface_name}",
            file_type="java",
            max_results=limit,
        )
        result["registration"] = self.optimizer.optimize_results(registration_results)
        
        if self.cache:
            self.cache.set("aidl", cache_key, result)
        
        return result
    
    def trace_binder_chain(
        self,
        interface_name: str,
        method_name: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        追踪 Binder IPC 调用链（Java -> JNI -> Native）。
        
        Args:
            interface_name: 接口名，如 "IActivityManager"
            method_name: 方法名，如 "startActivity"
            limit: 每层的最大结果数
        
        Returns:
            {
                "java_interface": [...],  # Java 接口定义
                "java_impl": [...],       # Java 实现
                "jni_bridge": [...],      # JNI 桥接
                "native_impl": [...]      # Native 实现
            }
        """
        cache_key = ("binder_chain", {"interface": interface_name, "method": method_name})
        if self.cache:
            cached = self.cache.get("binder", cache_key)
            if cached:
                return cached
        
        result = {
            "java_interface": [],
            "java_impl": [],
            "jni_bridge": [],
            "native_impl": []
        }
        
        # 1. Java 接口定义
        java_interface = self.client.search(
            search_type="def",
            query=f"{interface_name}.{method_name}",
            file_type="java",
            max_results=limit,
        )
        result["java_interface"] = self.optimizer.optimize_results(java_interface)
        
        # 2. Java 实现（Stub 中的实现）
        java_impl = self.client.search(
            search_type="full",
            query=f"class.*Stub.*{method_name}",
            file_type="java",
            max_results=limit,
        )
        result["java_impl"] = self.optimizer.optimize_results(java_impl)
        
        # 3. JNI 桥接（native 方法声明和实现）
        jni_bridge = self.client.search(
            search_type="full",
            query=f"native.*{method_name}",
            file_type="java",
            max_results=limit,
        )
        result["jni_bridge"] = self.optimizer.optimize_results(jni_bridge)
        
        # 4. Native 实现（C++ 中的 JNI 函数）
        native_impl = self.client.search(
            search_type="full",
            query=f"JNI.*{method_name}",
            file_type="cpp",
            max_results=limit,
        )
        result["native_impl"] = self.optimizer.optimize_results(native_impl)
        
        if self.cache:
            self.cache.set("binder", cache_key, result)
        
        return result
