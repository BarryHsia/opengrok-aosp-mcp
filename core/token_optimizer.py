"""Token optimization utilities for MCP responses."""
import json
from typing import Any, Dict


class TokenOptimizer:
    """Optimize MCP responses to reduce token consumption."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.path_prefixes = config.get("token_optimization", {}).get("path_prefixes", {})
        self.abbreviate = config.get("token_optimization", {}).get("abbreviate_paths", True)
        self.max_snippet_lines = config.get("limits", {}).get("max_snippet_lines", 5)
    
    def abbreviate_path(self, path: str) -> str:
        """Abbreviate common AOSP paths to save tokens."""
        if not self.abbreviate:
            return path
        
        for prefix, abbrev in self.path_prefixes.items():
            if path.startswith(prefix):
                return path.replace(prefix, abbrev, 1)
        
        return path
    
    def truncate_snippet(self, snippet: str, max_lines: int = None) -> str:
        """Truncate code snippet to key lines only."""
        if max_lines is None:
            max_lines = self.max_snippet_lines
        
        lines = snippet.split('\n')
        if len(lines) <= max_lines:
            return snippet
        
        # Keep first few lines and add truncation marker
        return '\n'.join(lines[:max_lines]) + f'\n... ({len(lines) - max_lines} more lines)'
    
    def optimize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize a single search result."""
        optimized = {}
        
        # Abbreviate path
        if 'path' in result:
            optimized['path'] = self.abbreviate_path(result['path'])
        elif 'file_path' in result:
            optimized['path'] = self.abbreviate_path(result['file_path'])
        
        # Keep essential fields with short keys
        if 'line' in result or 'lineNumber' in result:
            optimized['line'] = result.get('line') or result.get('lineNumber')
        
        if 'snippet' in result:
            optimized['snippet'] = self.truncate_snippet(result['snippet'])
        elif 'line_text' in result:
            optimized['snippet'] = self.truncate_snippet(result['line_text'])
        
        # Add clickable URL
        if 'clickable_url' in result:
            optimized['url'] = result['clickable_url']
        elif 'url' in result:
            optimized['url'] = result['url']
        
        # Keep project if present
        if 'project' in result:
            optimized['proj'] = result['project']
        
        return optimized
    
    def optimize_results(self, results: list) -> list:
        """Optimize a list of search results."""
        return [self.optimize_result(r) for r in results]
