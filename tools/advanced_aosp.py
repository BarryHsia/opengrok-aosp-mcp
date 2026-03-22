"""Advanced AOSP analysis tools (HAL, Broadcast, SELinux, etc.)."""
from typing import Any, Dict, List, Optional
from core import OpenGrokClient, QueryCache, TokenOptimizer


class AdvancedAospTools:
    """Advanced AOSP-specific analysis tools."""
    
    def __init__(self, client: OpenGrokClient, cache: QueryCache, optimizer: TokenOptimizer):
        self.client = client
        self.cache = cache
        self.optimizer = optimizer
    
    def find_hal_interface(
        self,
        hal_name: str,
        hal_type: str = "aidl",
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        查找 HAL 接口定义和实现。
        
        Args:
            hal_name: HAL 名称，如 "camera", "audio", "power"
            hal_type: HAL 类型，"aidl" 或 "hidl"
            limit: 最大结果数
        
        Returns:
            {
                "interface": [...],     # HAL 接口定义
                "implementation": [...], # HAL 实现
                "client_usage": [...]   # 客户端使用
            }
        """
        cache_key = ("hal", {"name": hal_name, "type": hal_type})
        if self.cache:
            cached = self.cache.get("hal", cache_key)
            if cached:
                return cached
        
        result = {
            "interface": [],
            "implementation": [],
            "client_usage": []
        }
        
        # 查找 HAL 接口定义
        if hal_type == "aidl":
            interface = self.client.search(
                search_type="full",
                query=f"interface.*{hal_name}",
                path="hardware/interfaces",
                file_type="aidl",
                max_results=limit,
            )
        else:  # hidl
            interface = self.client.search(
                search_type="full",
                query=f"interface.*{hal_name}",
                path="hardware/interfaces",
                file_type="hal",
                max_results=limit,
            )
        result["interface"] = self.optimizer.optimize_results(interface)
        
        # 查找实现
        impl = self.client.search(
            search_type="full",
            query=f"class.*{hal_name}.*Impl",
            path="hardware",
            file_type="cpp",
            max_results=limit,
        )
        result["implementation"] = self.optimizer.optimize_results(impl)
        
        # 查找客户端使用
        usage = self.client.search(
            search_type="full",
            query=f"get.*{hal_name}.*Service",
            file_type="cpp",
            max_results=limit,
        )
        result["client_usage"] = self.optimizer.optimize_results(usage)
        
        if self.cache:
            self.cache.set("hal", cache_key, result)
        
        return result
    
    def trace_broadcast(
        self,
        action: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        追踪广播流程（发送者和接收者）。
        
        Args:
            action: 广播 Action，如 "android.intent.action.BOOT_COMPLETED"
            limit: 最大结果数
        
        Returns:
            {
                "senders": [...],    # 广播发送者
                "receivers": [...]   # 广播接收者
            }
        """
        cache_key = ("broadcast", {"action": action})
        if self.cache:
            cached = self.cache.get("broadcast", cache_key)
            if cached:
                return cached
        
        result = {
            "senders": [],
            "receivers": []
        }
        
        # 查找发送者（sendBroadcast）
        senders = self.client.search(
            search_type="full",
            query=f"sendBroadcast.*{action}",
            file_type="java",
            max_results=limit,
        )
        result["senders"] = self.optimizer.optimize_results(senders)
        
        # 查找接收者（BroadcastReceiver）
        receivers = self.client.search(
            search_type="full",
            query=f"onReceive.*{action}",
            file_type="java",
            max_results=limit,
        )
        result["receivers"] = self.optimizer.optimize_results(receivers)
        
        if self.cache:
            self.cache.set("broadcast", cache_key, result)
        
        return result
    
    def search_selinux_policy(
        self,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        搜索 SELinux 策略。
        
        Args:
            query: 搜索关键词，如 "camera", "allow", "neverallow"
            limit: 最大结果数
        
        Returns:
            List of policy matches
        """
        cache_key = ("selinux", {"query": query})
        if self.cache:
            cached = self.cache.get("selinux", cache_key)
            if cached:
                return cached
        
        # 搜索 .te 文件（SELinux 策略文件）
        results = self.client.search(
            search_type="full",
            query=query,
            path="system/sepolicy",
            file_type="te",
            max_results=limit,
        )
        
        optimized = self.optimizer.optimize_results(results)
        
        if self.cache:
            self.cache.set("selinux", cache_key, optimized)
        
        return optimized
    
    def find_resource_overlay(
        self,
        resource_name: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        查找 Framework 资源和 RRO（Runtime Resource Overlay）。
        
        Args:
            resource_name: 资源名，如 "config_enableTranslucentDecor"
            limit: 最大结果数
        
        Returns:
            {
                "framework_resource": [...],  # Framework 资源定义
                "overlay": [...]              # RRO 覆盖
            }
        """
        cache_key = ("resource", {"name": resource_name})
        if self.cache:
            cached = self.cache.get("resource", cache_key)
            if cached:
                return cached
        
        result = {
            "framework_resource": [],
            "overlay": []
        }
        
        # 查找 Framework 资源
        framework = self.client.search(
            search_type="full",
            query=resource_name,
            path="frameworks/base/core/res",
            file_type="xml",
            max_results=limit,
        )
        result["framework_resource"] = self.optimizer.optimize_results(framework)
        
        # 查找 RRO 覆盖
        overlay = self.client.search(
            search_type="full",
            query=resource_name,
            path="vendor",
            file_type="xml",
            max_results=limit,
        )
        result["overlay"] = self.optimizer.optimize_results(overlay)
        
        if self.cache:
            self.cache.set("resource", cache_key, result)
        
        return result
    
    def trace_init_service(
        self,
        service_name: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        追踪 Init 进程服务。
        
        Args:
            service_name: 服务名，如 "surfaceflinger", "zygote"
            limit: 最大结果数
        
        Returns:
            {
                "init_rc": [...],      # init.rc 配置
                "service_code": [...]  # 服务代码
            }
        """
        cache_key = ("init", {"service": service_name})
        if self.cache:
            cached = self.cache.get("init", cache_key)
            if cached:
                return cached
        
        result = {
            "init_rc": [],
            "service_code": []
        }
        
        # 查找 init.rc 配置
        init_rc = self.client.search(
            search_type="full",
            query=f"service.*{service_name}",
            file_type="rc",
            max_results=limit,
        )
        result["init_rc"] = self.optimizer.optimize_results(init_rc)
        
        # 查找服务代码（main 函数）
        service_code = self.client.search(
            search_type="full",
            query=f"main.*{service_name}",
            file_type="cpp",
            max_results=limit,
        )
        result["service_code"] = self.optimizer.optimize_results(service_code)
        
        if self.cache:
            self.cache.set("init", cache_key, result)
        
        return result
    
    def analyze_build_module(
        self,
        module_name: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        分析构建系统模块。
        
        Args:
            module_name: 模块名，如 "framework", "services"
            limit: 最大结果数
        
        Returns:
            {
                "android_bp": [...],  # Android.bp 定义
                "android_mk": [...]   # Android.mk 定义
            }
        """
        cache_key = ("build", {"module": module_name})
        if self.cache:
            cached = self.cache.get("build", cache_key)
            if cached:
                return cached
        
        result = {
            "android_bp": [],
            "android_mk": []
        }
        
        # 查找 Android.bp
        bp = self.client.search(
            search_type="full",
            query=f'name.*"{module_name}"',
            file_type="bp",
            max_results=limit,
        )
        result["android_bp"] = self.optimizer.optimize_results(bp)
        
        # 查找 Android.mk
        mk = self.client.search(
            search_type="full",
            query=f"LOCAL_MODULE.*{module_name}",
            file_type="mk",
            max_results=limit,
        )
        result["android_mk"] = self.optimizer.optimize_results(mk)
        
        if self.cache:
            self.cache.set("build", cache_key, result)
        
        return result
