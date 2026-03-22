"""Basic code search tools."""
from typing import Any, Dict, List, Optional
from core import OpenGrokClient, QueryCache, TokenOptimizer


class BasicTools:
    """Basic code search tools for OpenGrok."""
    
    def __init__(self, client: OpenGrokClient, cache: QueryCache, optimizer: TokenOptimizer):
        self.client = client
        self.cache = cache
        self.optimizer = optimizer
    
    def search_definitions(
        self,
        symbol: str,
        project: Optional[str] = None,
        path: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find symbol definitions (functions, classes, methods).
        
        Args:
            symbol: Symbol name to search
            project: Optional project filter
            path: Optional path filter
            file_type: Optional file type (e.g., 'java', 'cpp')
            limit: Max results (default 10, max 50)
        
        Returns:
            List of {path, line, snippet, url}
        """
        # Check cache
        cache_key = ("def", {"symbol": symbol, "project": project, "path": path, "file_type": file_type})
        cached = self.cache.get("search", cache_key)
        if cached:
            return cached[:limit]
        
        # Query OpenGrok
        results = self.client.search(
            search_type="def",
            query=symbol,
            project=project,
            path=path,
            file_type=file_type,
            max_results=min(limit, 50),
        )
        
        # Optimize and cache
        optimized = self.optimizer.optimize_results(results)
        self.cache.set("search", cache_key, optimized)
        
        return optimized[:limit]
    
    def search_references(
        self,
        symbol: str,
        project: Optional[str] = None,
        path: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Find symbol references/usage points.
        
        Args:
            symbol: Symbol name to search
            project: Optional project filter
            path: Optional path filter
            file_type: Optional file type
            limit: Max results (default 10, max 50)
        
        Returns:
            List of {path, line, snippet, url}
        """
        cache_key = ("symbol", {"symbol": symbol, "project": project, "path": path, "file_type": file_type})
        cached = self.cache.get("search", cache_key)
        if cached:
            return cached[:limit]
        
        results = self.client.search(
            search_type="symbol",
            query=symbol,
            project=project,
            path=path,
            file_type=file_type,
            max_results=min(limit, 50),
        )
        
        optimized = self.optimizer.optimize_results(results)
        self.cache.set("search", cache_key, optimized)
        
        return optimized[:limit]
    
    def search_full(
        self,
        query: str,
        project: Optional[str] = None,
        path: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Full-text search across codebase.
        
        Args:
            query: Search query (supports regex)
            project: Optional project filter
            path: Optional path filter
            file_type: Optional file type
            limit: Max results (default 10, max 50)
        
        Returns:
            List of {path, line, snippet, url}
        """
        cache_key = ("full", {"query": query, "project": project, "path": path, "file_type": file_type})
        cached = self.cache.get("search", cache_key)
        if cached:
            return cached[:limit]
        
        results = self.client.search(
            search_type="full",
            query=query,
            project=project,
            path=path,
            file_type=file_type,
            max_results=min(limit, 50),
        )
        
        optimized = self.optimizer.optimize_results(results)
        self.cache.set("search", cache_key, optimized)
        
        return optimized[:limit]
    
    def get_file_content(
        self,
        path: str,
        start_line: int = 1,
        end_line: int = 50,
    ) -> Dict[str, Any]:
        """
        Get file content with line range.
        
        Args:
            path: File path
            start_line: Starting line (1-based, default 1)
            end_line: Ending line (inclusive, default 50)
        
        Returns:
            {path, start_line, end_line, total_lines, text}
        """
        # Limit range to avoid token bloat
        max_lines = 200
        if end_line - start_line > max_lines:
            end_line = start_line + max_lines
        
        cache_key = ("file", {"path": path, "start": start_line, "end": end_line})
        cached = self.cache.get("content", cache_key)
        if cached:
            return cached
        
        result = self.client.get_file_content(path, start_line, end_line)
        
        # Optimize path
        result["path"] = self.optimizer.abbreviate_path(result["path"])
        
        self.cache.set("content", cache_key, result)
        return result
    
    def list_projects(self) -> List[str]:
        """
        List all available OpenGrok projects.
        
        Returns:
            List of project names
        """
        cached = self.cache.get("projects", {})
        if cached:
            return cached
        
        projects = self.client.list_projects()
        self.cache.set("projects", {}, projects)
        
        return projects
