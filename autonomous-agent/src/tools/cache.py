"""Tool result cache."""

from typing import Any, Optional
import hashlib
import json
import time
from dataclasses import dataclass, field
from collections import OrderedDict


@dataclass
class ToolCacheEntry:
    """Cached tool result."""
    key: str
    result: Any
    created_at: float = field(default_factory=time.time)
    access_count: int = 0
    ttl_seconds: int = 300


class ToolCache:
    """Cache for tool execution results."""
    
    def __init__(
        self,
        max_size: int = 500,
        default_ttl: int = 300,
    ):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, ToolCacheEntry] = OrderedDict()
    
    def _make_key(self, tool_name: str, args: dict) -> str:
        """Create cache key from tool name and arguments."""
        data = {"tool": tool_name, "args": args}
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()[:32]
    
    def get(self, tool_name: str, args: dict) -> Optional[Any]:
        """Get cached result if available and not expired."""
        key = self._make_key(tool_name, args)
        
        if key in self._cache:
            entry = self._cache[key]
            
            # Check TTL
            if time.time() - entry.created_at > entry.ttl_seconds:
                del self._cache[key]
                return None
            
            # Move to end (LRU)
            self._cache.move_to_end(key)
            entry.access_count += 1
            
            return entry.result
        
        return None
    
    def set(
        self,
        tool_name: str,
        args: dict,
        result: Any,
        ttl: int = None,
    ) -> None:
        """Store result in cache."""
        key = self._make_key(tool_name, args)
        
        # Evict if at capacity
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
        
        entry = ToolCacheEntry(
            key=key,
            result=result,
            ttl_seconds=ttl or self.default_ttl,
        )
        self._cache[key] = entry
    
    def invalidate(self, tool_name: str, args: dict = None) -> bool:
        """Invalidate cache entry."""
        if args:
            key = self._make_key(tool_name, args)
            if key in self._cache:
                del self._cache[key]
                return True
            return False
        else:
            # Invalidate all entries for tool
            keys_to_delete = [
                k for k, v in self._cache.items()
                if v.key.startswith(f'{{"tool": "{tool_name}"')
            ]
            for key in keys_to_delete:
                del self._cache[key]
            return len(keys_to_delete) > 0
    
    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()
    
    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_accesses = sum(e.access_count for e in self._cache.values())
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "total_accesses": total_accesses,
        }


# Global tool cache
_global_tool_cache: Optional[ToolCache] = None


def get_tool_cache() -> ToolCache:
    """Get global tool cache."""
    global _global_tool_cache
    if _global_tool_cache is None:
        _global_tool_cache = ToolCache()
    return _global_tool_cache