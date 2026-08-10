"""Rate limiter for API calls and costs."""

from typing import Any, Optional
from dataclasses import dataclass, field
import time
import asyncio
from collections import defaultdict


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests_per_minute: int = 60
    tokens_per_minute: int = 100000
    cost_per_hour_usd: float = 10.0
    burst_allowance: float = 1.5  # Allow 1.5x burst


class RateLimiter:
    """Token bucket rate limiter with multiple dimensions."""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        
        # Request rate limiting
        self._request_tokens = self.config.requests_per_minute * self.config.burst_allowance
        self._request_rate = self.config.requests_per_minute / 60.0  # per second
        self._request_last = time.time()
        
        # Token rate limiting
        self._token_tokens = self.config.tokens_per_minute * self.config.burst_allowance
        self._token_rate = self.config.tokens_per_minute / 60.0
        self._token_last = time.time()
        
        # Cost tracking
        self._cost_used = 0.0
        self._cost_window_start = time.time()
        self._cost_limit = self.config.cost_per_hour_usd
        
        # Per-key limits (for multi-tenant)
        self._key_limits: dict[str, dict] = defaultdict(lambda: {
            "requests": self.config.requests_per_minute * self.config.burst_allowance,
            "tokens": self.config.tokens_per_minute * self.config.burst_allowance,
            "last_update": time.time(),
        })
        
        self._lock = asyncio.Lock()
    
    async def check_limit(
        self,
        key: str = "default",
        tokens: int = 0,
        cost: float = 0.0,
    ) -> bool:
        """Check if request is within limits."""
        async with self._lock:
            now = time.time()
            
            # Refill request tokens
            elapsed = now - self._request_last
            self._request_tokens = min(
                self.config.requests_per_minute * self.config.burst_allowance,
                self._request_tokens + elapsed * self._request_rate,
            )
            self._request_last = now
            
            # Refill token tokens
            elapsed = now - self._token_last
            self._token_tokens = min(
                self.config.tokens_per_minute * self.config.burst_allowance,
                self._token_tokens + elapsed * self._token_rate,
            )
            self._token_last = now
            
            # Check cost window
            if now - self._cost_window_start >= 3600:
                self._cost_used = 0.0
                self._cost_window_start = now
            
            # Check global limits
            if self._request_tokens < 1:
                return False
            if self._token_tokens < tokens:
                return False
            if self._cost_used + cost > self._cost_limit:
                return False
            
            # Check per-key limits
            key_data = self._key_limits[key]
            elapsed = now - key_data["last_update"]
            key_data["requests"] = min(
                self.config.requests_per_minute,
                key_data["requests"] + elapsed * (self.config.requests_per_minute / 60.0),
            )
            key_data["tokens"] = min(
                self.config.tokens_per_minute,
                key_data["tokens"] + elapsed * (self.config.tokens_per_minute / 60.0),
            )
            key_data["last_update"] = now
            
            if key_data["requests"] < 1:
                return False
            if key_data["tokens"] < tokens:
                return False
            
            return True
    
    async def consume(
        self,
        key: str = "default",
        tokens: int = 0,
        cost: float = 0.0,
    ) -> bool:
        """Consume rate limit tokens."""
        async with self._lock:
            if not await self.check_limit(key, tokens, cost):
                return False
            
            # Consume global
            self._request_tokens -= 1
            self._token_tokens -= tokens
            self._cost_used += cost
            
            # Consume per-key
            key_data = self._key_limits[key]
            key_data["requests"] -= 1
            key_data["tokens"] -= tokens
            
            return True
    
    def get_status(self) -> dict:
        """Get current rate limit status."""
        return {
            "requests": {
                "available": int(self._request_tokens),
                "limit": self.config.requests_per_minute,
                "rate_per_sec": self._request_rate,
            },
            "tokens": {
                "available": int(self._token_tokens),
                "limit": self.config.tokens_per_minute,
                "rate_per_sec": self._token_rate,
            },
            "cost": {
                "used": self._cost_used,
                "limit": self._cost_limit,
                "remaining": max(0, self._cost_limit - self._cost_used),
            },
        }
    
    def reset(self) -> None:
        """Reset all limits."""
        self._request_tokens = self.config.requests_per_minute * self.config.burst_allowance
        self._token_tokens = self.config.tokens_per_minute * self.config.burst_allowance
        self._cost_used = 0.0
        self._cost_window_start = time.time()
        self._key_limits.clear()