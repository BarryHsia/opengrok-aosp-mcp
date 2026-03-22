"""Disk-based cache for OpenGrok queries."""
import hashlib
import json
from pathlib import Path
from typing import Any, Optional
from diskcache import Cache


class QueryCache:
    """Cache OpenGrok query results to reduce API calls and token usage."""
    
    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl_hours * 3600  # Convert to seconds
        self.cache = Cache(str(self.cache_dir))
    
    def _make_key(self, endpoint: str, params: dict) -> str:
        """Generate cache key from endpoint and parameters."""
        # Sort params for consistent keys
        sorted_params = json.dumps(params, sort_keys=True)
        key_str = f"{endpoint}:{sorted_params}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, endpoint: str, params: dict) -> Optional[Any]:
        """Get cached result if available and not expired."""
        key = self._make_key(endpoint, params)
        return self.cache.get(key)
    
    def set(self, endpoint: str, params: dict, value: Any) -> None:
        """Cache a query result."""
        key = self._make_key(endpoint, params)
        self.cache.set(key, value, expire=self.ttl)
    
    def clear(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
    
    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "volume": self.cache.volume()
        }
