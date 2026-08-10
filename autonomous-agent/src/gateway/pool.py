"""Connection pool for HTTP clients."""

from typing import Any, Optional
import httpx
from contextlib import asynccontextmanager


class ConnectionPool:
    """Manages HTTP connection pools for LLM providers."""
    
    def __init__(
        self,
        max_connections: int = 100,
        max_keepalive: int = 20,
        keepalive_expiry: float = 30.0,
        timeout: float = 60.0,
    ):
        self.max_connections = max_connections
        self.max_keepalive = max_keepalive
        self.keepalive_expiry = keepalive_expiry
        self.timeout = timeout
        self._clients: dict[str, httpx.AsyncClient] = {}
        self._limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive,
            keepalive_expiry=keepalive_expiry,
        )

    def get_client(self, base_url: str, **kwargs) -> httpx.AsyncClient:
        """Get or create a client for the given base URL."""
        if base_url not in self._clients:
            timeout = httpx.Timeout(self.timeout)
            self._clients[base_url] = httpx.AsyncClient(
                base_url=base_url,
                limits=self._limits,
                timeout=timeout,
                **kwargs,
            )
        return self._clients[base_url]

    @asynccontextmanager
    async def request(
        self,
        base_url: str,
        method: str,
        path: str,
        **kwargs,
    ):
        """Make a request using pooled connection."""
        client = self.get_client(base_url)
        try:
            response = await client.request(method, path, **kwargs)
            yield response
        finally:
            pass  # Client stays in pool

    async def close(self) -> None:
        """Close all clients."""
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()

    async def __aenter__(self) -> "ConnectionPool":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()


# Global pool instance
_global_pool: Optional[ConnectionPool] = None


def get_global_pool() -> ConnectionPool:
    """Get global connection pool."""
    global _global_pool
    if _global_pool is None:
        _global_pool = ConnectionPool()
    return _global_pool


async def close_global_pool() -> None:
    """Close global connection pool."""
    global _global_pool
    if _global_pool:
        await _global_pool.close()
        _global_pool = None