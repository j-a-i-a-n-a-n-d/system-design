"""Ollama Gateway implementation for local models."""

from typing import Any, Optional
import time
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from .base import LLMGateway, Message, ToolSchema, LLMResponse, ModelCapabilities, MessageRole


class OllamaGateway(LLMGateway):
    """Ollama local model gateway."""
    
    def __init__(
        self,
        model: str = "llama3.1",
        base_url: str = "http://localhost:11434",
        **kwargs,
    ):
        super().__init__(model, api_key=None, **kwargs)
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

    @property
    def provider_name(self) -> str:
        return "ollama"

    def _get_capabilities(self) -> ModelCapabilities:
        caps = ModelCapabilities()
        caps.supports_tools = False  # Most local models don't support tools well
        caps.supports_streaming = True
        caps.max_context = 8192
        caps.max_output = 4096
        return caps

    def _format_messages(self, messages: list[Message]) -> list[dict]:
        """Format messages for Ollama API."""
        formatted = []
        for msg in messages:
            formatted.append({
                "role": msg.role.value,
                "content": msg.content,
            })
        return formatted

    @retry(
        wait=wait_exponential_jitter(initial=1, max=10),
        stop=stop_after_attempt(3),
    )
    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] = None,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """Complete a chat conversation."""
        start = time.perf_counter()
        
        formatted_messages = self._format_messages(messages)
        
        # Ollama doesn't support tools natively, inject tool descriptions into system prompt
        if tools and formatted_messages and formatted_messages[0]["role"] == "system":
            tool_desc = "\n\nAvailable tools:\n"
            for tool in tools:
                tool_desc += f"- {tool.name}: {tool.description}\n"
            formatted_messages[0]["content"] += tool_desc
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens or 4096,
            },
        }
        
        try:
            if stream:
                return await self._stream_complete(payload, start)
            
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["message"]["content"],
                tool_calls=[],  # Not supported
                model=self.model,
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                },
                finish_reason="stop" if data.get("done") else "length",
                latency_ms=(time.perf_counter() - start) * 1000,
            )
            
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Ollama API error: {e.response.text}") from e
        except Exception as e:
            raise RuntimeError(f"Ollama error: {e}") from e

    async def _stream_complete(self, payload: dict, start: float) -> LLMResponse:
        """Handle streaming completion."""
        payload["stream"] = True
        content_parts = []
        
        async with self.client.stream("POST", "/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    import json
                    data = json.loads(line)
                    if "message" in data and "content" in data["message"]:
                        content_parts.append(data["message"]["content"])
                    if data.get("done"):
                        usage = {
                            "prompt_tokens": data.get("prompt_eval_count", 0),
                            "completion_tokens": data.get("eval_count", 0),
                            "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                        }
                        break
        
        return LLMResponse(
            content="".join(content_parts),
            tool_calls=[],
            model=self.model,
            usage=usage,
            finish_reason="stop",
            latency_ms=(time.perf_counter() - start) * 1000,
        )

    async def embed(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[list[float]]:
        """Generate embeddings using Ollama."""
        embeddings = []
        for text in texts:
            response = await self.client.post(
                "/api/embeddings",
                json={"model": self.model, "prompt": text},
            )
            response.raise_for_status()
            data = response.json()
            embeddings.append(data["embedding"])
        return embeddings

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()