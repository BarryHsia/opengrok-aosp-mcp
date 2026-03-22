"""Intelligent analysis tools combining multiple searches."""
from typing import Any, Dict, List, Optional
from core import OpenGrokClient, QueryCache, TokenOptimizer


class IntelligentTools:
    """Intelligent analysis tools that combine multiple searches."""
    
    def __init__(self, client: OpenGrokClient, cache: QueryCache, optimizer: TokenOptimizer):
        self.client = client
        self.cache = cache
        self.optimizer = optimizer
    
    def explain_code_flow(
        self,
        symbol: str,
        limit: int = 5,
    ) -> Dict[str, Any]:
        """
        智能代码流程解释（组合多个工具）。
        
        Args:
            symbol: 符号名，如 "startActivity"
            limit: 每个类型的最大结果数
        
        Returns:
            {
                "definition": [...],    # 定义
                "references": [...],    # 引用
                "related_code": [...]   # 相关代码
            }
        """
        cache_key = ("explain", {"symbol": symbol})
        if self.cache:
            cached = self.cache.get("intelligent", cache_key)
            if cached:
                return cached
        
        result = {
            "definition": [],
            "references": [],
            "related_code": []
        }
        
        # 1. 查找定义
        definitions = self.client.search(
            search_type="def",
            query=symbol,
            max_results=limit,
        )
        result["definition"] = self.optimizer.optimize_results(definitions)
        
        # 2. 查找引用
        references = self.client.search(
            search_type="symbol",
            query=symbol,
            max_results=limit,
        )
        result["references"] = self.optimizer.optimize_results(references)
        
        # 3. 查找相关代码（全文搜索）
        related = self.client.search(
            search_type="full",
            query=symbol,
            max_results=limit,
        )
        result["related_code"] = self.optimizer.optimize_results(related)
        
        if self.cache:
            self.cache.set("intelligent", cache_key, result)
        
        return result
    
    def find_similar_patterns(
        self,
        pattern: str,
        file_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        查找相似代码模式。
        
        Args:
            pattern: 代码模式，如 "synchronized.*notify"
            file_type: 文件类型过滤
            limit: 最大结果数
        
        Returns:
            List of similar code patterns
        """
        cache_key = ("pattern", {"pattern": pattern, "file_type": file_type})
        if self.cache:
            cached = self.cache.get("intelligent", cache_key)
            if cached:
                return cached
        
        # 使用正则搜索查找模式
        results = self.client.search(
            search_type="full",
            query=pattern,
            file_type=file_type,
            max_results=limit,
        )
        
        optimized = self.optimizer.optimize_results(results)
        
        if self.cache:
            self.cache.set("intelligent", cache_key, optimized)
        
        return optimized
