"""System Service and JNI analysis tools."""
from typing import Any, Dict, List, Optional
from core import OpenGrokClient, QueryCache, TokenOptimizer


class SystemServiceJniTools:
    """System Service and JNI analysis tools for AOSP."""
    
    def __init__(self, client: OpenGrokClient, cache: QueryCache, optimizer: TokenOptimizer):
        self.client = client
        self.cache = cache
        self.optimizer = optimizer
    
    def analyze_system_service(
        self,
        service_name: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        分析系统服务生命周期（启动、注册、获取）。
        
        Args:
            service_name: 服务名，如 "activity", "power", "window"
            limit: 每个类型的最大结果数
        
        Returns:
            {
                "service_class": [...],    # 服务类定义
                "registration": [...],     # 服务注册
                "startup": [...],          # 启动逻辑
                "client_usage": [...]      # 客户端使用
            }
        """
        cache_key = ("system_service", {"service": service_name})
        if self.cache:
            cached = self.cache.get("service", cache_key)
            if cached:
                return cached
        
        result = {
            "service_class": [],
            "registration": [],
            "startup": [],
            "client_usage": []
        }
        
        # 1. 查找服务类（通常是 XxxManagerService）
        service_class_name = f"{service_name.capitalize()}ManagerService"
        service_class = self.client.search(
            search_type="def",
            query=service_class_name,
            file_type="java",
            max_results=limit,
        )
        result["service_class"] = self.optimizer.optimize_results(service_class)
        
        # 2. 查找服务注册（ServiceManager.addService）
        registration = self.client.search(
            search_type="full",
            query=f'addService.*{service_name}',
            file_type="java",
            max_results=limit,
        )
        result["registration"] = self.optimizer.optimize_results(registration)
        
        # 3. 查找启动逻辑（SystemServer 中的启动）
        startup = self.client.search(
            search_type="full",
            query=f'start.*{service_class_name}',
            file_type="java",
            max_results=limit,
        )
        result["startup"] = self.optimizer.optimize_results(startup)
        
        # 4. 查找客户端使用（getSystemService）
        client_usage = self.client.search(
            search_type="full",
            query=f'getSystemService.*{service_name}',
            file_type="java",
            max_results=limit,
        )
        result["client_usage"] = self.optimizer.optimize_results(client_usage)
        
        if self.cache:
            self.cache.set("service", cache_key, result)
        
        return result
    
    def find_jni_bridge(
        self,
        java_class: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        查找 Java-Native 桥接（JNI 方法和实现）。
        
        Args:
            java_class: Java 类名，如 "android.os.Process"
            limit: 每个类型的最大结果数
        
        Returns:
            {
                "java_native_methods": [...],  # Java 中的 native 方法声明
                "jni_registration": [...],     # JNI 方法注册
                "native_impl": [...]           # Native 实现
            }
        """
        cache_key = ("jni", {"class": java_class})
        if self.cache:
            cached = self.cache.get("jni", cache_key)
            if cached:
                return cached
        
        result = {
            "java_native_methods": [],
            "jni_registration": [],
            "native_impl": []
        }
        
        # 提取类名（去掉包名）
        class_name = java_class.split(".")[-1]
        
        # 1. 查找 Java 中的 native 方法声明
        java_native = self.client.search(
            search_type="full",
            query=f'native.*{class_name}',
            file_type="java",
            max_results=limit,
        )
        result["java_native_methods"] = self.optimizer.optimize_results(java_native)
        
        # 2. 查找 JNI 方法注册（RegisterNatives）
        jni_reg = self.client.search(
            search_type="full",
            query=f'RegisterNatives.*{class_name}',
            file_type="cpp",
            max_results=limit,
        )
        result["jni_registration"] = self.optimizer.optimize_results(jni_reg)
        
        # 3. 查找 Native 实现（android_xxx_ClassName）
        native_prefix = f'android_{java_class.replace(".", "_").replace("android_", "")}'
        native_impl = self.client.search(
            search_type="full",
            query=native_prefix,
            file_type="cpp",
            max_results=limit,
        )
        result["native_impl"] = self.optimizer.optimize_results(native_impl)
        
        if self.cache:
            self.cache.set("jni", cache_key, result)
        
        return result
    
    def trace_permission(
        self,
        permission: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        追踪权限检查路径。
        
        Args:
            permission: 权限名，如 "android.permission.CAMERA"
            limit: 每个类型的最大结果数
        
        Returns:
            {
                "permission_definition": [...],  # 权限定义
                "check_points": [...],           # 检查点
                "enforcement": [...]             # 强制执行
            }
        """
        cache_key = ("permission", {"perm": permission})
        if self.cache:
            cached = self.cache.get("permission", cache_key)
            if cached:
                return cached
        
        result = {
            "permission_definition": [],
            "check_points": [],
            "enforcement": []
        }
        
        # 1. 查找权限定义（AndroidManifest.xml 或 permission 声明）
        perm_def = self.client.search(
            search_type="full",
            query=permission,
            file_type="xml",
            max_results=limit,
        )
        result["permission_definition"] = self.optimizer.optimize_results(perm_def)
        
        # 2. 查找检查点（checkPermission, enforcePermission）
        check_points = self.client.search(
            search_type="full",
            query=f'checkPermission.*{permission}',
            file_type="java",
            max_results=limit,
        )
        result["check_points"] = self.optimizer.optimize_results(check_points)
        
        # 3. 查找强制执行（enforcePermission）
        enforcement = self.client.search(
            search_type="full",
            query=f'enforcePermission.*{permission}',
            file_type="java",
            max_results=limit,
        )
        result["enforcement"] = self.optimizer.optimize_results(enforcement)
        
        if self.cache:
            self.cache.set("permission", cache_key, result)
        
        return result
