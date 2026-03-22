"""OpenGrok API client wrapper."""
import os
import re
from typing import Any, Dict, List, Optional
import httpx


class OpenGrokClient:
    """Client for OpenGrok REST API."""
    
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.token = token or os.environ.get("OPENGROK_TOKEN")
        self.timeout = 30.0
    
    def _headers(self) -> Dict[str, str]:
        """Build request headers."""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _url(self, path: str) -> str:
        """Build full URL."""
        return f"{self.base_url}{path}"
    
    def search(
        self,
        search_type: str,  # 'def', 'symbol', 'full'
        query: str,
        project: Optional[str] = None,
        path: Optional[str] = None,
        file_type: Optional[str] = None,
        max_results: int = 50,
        start: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Search code in OpenGrok.
        
        Args:
            search_type: 'def' (definitions), 'symbol' (references), 'full' (full-text)
            query: Search query
            project: Optional project filter
            path: Optional path filter
            file_type: Optional file type filter
            max_results: Maximum results to return
            start: Starting offset for pagination
        
        Returns:
            List of search hits with path, line, snippet, url
        """
        params = {
            search_type: query,
            "projects": project,
            "maxresults": max_results,
            "start": start,
            "path": path or "",
            "type": file_type or "",
        }
        
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(
                self._url("/api/v1/search"),
                headers=self._headers(),
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()
        
        # Parse results
        results_by_path = data.get("results", {})
        hits = []
        
        for file_path, matches in results_by_path.items():
            for match in matches:
                line_num = self._parse_line_number(match.get("lineNumber"))
                line_text = match.get("line", "")
                clean_text = re.sub(r"</?b>", "", line_text)
                
                hits.append({
                    "path": file_path,
                    "line": line_num,
                    "snippet": clean_text,
                    "tag": match.get("tag"),
                    "url": self._build_url(file_path, line_num),
                })
        
        return hits
    
    def get_file_content(
        self,
        path: str,
        start_line: int = 1,
        end_line: int = 200,
    ) -> Dict[str, Any]:
        """
        Get file content with line range.
        
        Args:
            path: File path
            start_line: Starting line (1-based)
            end_line: Ending line (inclusive)
        
        Returns:
            Dict with path, start_line, end_line, total_lines, text
        """
        rel_path = path.lstrip("/")
        
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(
                self._url(f"/raw/{rel_path}"),
                headers=self._headers(),
            )
            resp.raise_for_status()
            content = resp.text
        
        lines = content.splitlines()
        total = len(lines)
        
        # Clamp bounds
        start_idx = max(start_line - 1, 0)
        end_idx = min(end_line, total)
        
        snippet_lines = lines[start_idx:end_idx]
        numbered = [
            f"{i+1}: {line}"
            for i, line in enumerate(snippet_lines, start=start_idx)
        ]
        
        return {
            "path": path,
            "start_line": start_line,
            "end_line": end_idx,
            "total_lines": total,
            "text": "\n".join(numbered),
        }
    
    def list_projects(self) -> List[str]:
        """List all available projects."""
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.get(
                self._url("/api/v1/projects"),
                headers=self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()
        
        return [str(p) for p in data]
    
    def _parse_line_number(self, line_num: Any) -> Optional[int]:
        """Parse line number from various formats."""
        if line_num is None:
            return None
        try:
            return int(line_num)
        except (ValueError, TypeError):
            return None
    
    def _build_url(self, path: str, line_num: Optional[int]) -> str:
        """Build clickable URL for file location."""
        path_clean = path.lstrip("/")
        url = f"{self.base_url}/xref/{path_clean}"
        if line_num:
            url += f"#{line_num}"
        return url
