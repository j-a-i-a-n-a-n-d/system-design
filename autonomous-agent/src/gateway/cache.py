"""Prompt cache for LLM responses."""

from typing import Any, Optional
import hashlib
import json
import time
from dataclasses import dataclass, field
from collections import OrderedDict


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    response: Any
    created_at: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    tokens_saved: int = 0
    cost_saved: float = 0.0


class PromptCache:
    """LRU cache for LLM prompts and responses."""
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: int = 3600,
        enable_semantic: bool = False,
    ):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.enable_semantic = enable_semantic
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._semantic_index: dict[str, list[str]] = {}  # embedding -> keys

    def _make_key(self, messages: list[dict], tools: list = None, **kwargs) -> str:
        """Create cache key from request."""
        # Create deterministic representation
        data = {
            "messages": messages,
            "tools": tools,
            "params": {k: v for k, v in kwargs.items() if k not in ("stream",)},
        }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()[:32]

    def get(self, messages: list[dict], tools: list = None, **kwargs) -> Optional[Any]:
        """Get cached response if available."""
        key = self._make_key(messages, tools, **kwargs)
        
        if key in self._cache:
            entry = self._cache[key]
            
            # Check TTL
            if time.time() - entry.created_at > self.ttl_seconds:
                del self._cache[key]
                return None
            
            # Move to end (LRU)
            self._cache.move_to_end(key)
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            return entry.response
        
        return None

    def set(
        self,
        messages: list[dict],
        response: Any,
        tools: list = None,
        tokens_saved: int = 0,
        cost_saved: float = 0.0,
        **kwargs,
    ) -> None:
        """Store response in cache."""
        key = self._make_key(messages, tools, **kwargs)
        
        # Evict if at capacity
        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
        
        entry = CacheEntry(
            key=key,
            response=response,
            tokens_saved=tokens_saved,
            cost_saved=cost_saved,
        )
        self._cache[key] = entry

    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
        self._semantic_index.clear()

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_saved_tokens = sum(e.tokens_saved for e in self._cache.values())
        total_saved_cost = sum(e.cost_saved for e in self._cache.values())
        total_accesses = sum(e.access_count for e in self._cache.values())
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_rate": total_accesses / max(1, total_accesses + len(self._cache)),
            "tokens_saved": total_saved_tokens,
            "cost_saved": total_saved_cost,
        }

    def prune_expired(self) -> int:
        """Remove expired entries. Returns count removed."""
        now = time.time()
        expired = [
            key for key, entry in self._cache.items()
            if now - entry.created_at > self.ttl_seconds
        ]
        for key in expired:
            del self._cache[key]
        return len(expired)