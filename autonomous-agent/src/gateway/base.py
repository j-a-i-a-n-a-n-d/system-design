"""LLM Gateway base classes and types."""

from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """Chat message."""
    role: MessageRole
    content: str
    tool_calls: list[dict] = Field(default_factory=list)
    tool_call_id: Optional[str] = None
    name: Optional[str] = None


class ToolSchema(BaseModel):
    """Tool schema for LLM function calling."""
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ModelCapabilities(BaseModel):
    """Model capabilities."""
    supports_tools: bool = True
    supports_streaming: bool = True
    supports_vision: bool = False
    max_context: int = 128000
    max_output: int = 4096


class LLMResponse(BaseModel):
    """LLM response."""
    content: str
    tool_calls: list[dict] = Field(default_factory=list)
    model: str = ""
    usage: dict[str, int] = Field(default_factory=dict)
    finish_reason: Optional[str] = None
    latency_ms: float = 0


class LLMGateway(ABC):
    """Abstract LLM gateway."""
    
    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        self.model = model
        self.api_key = api_key
        self.kwargs = kwargs
        self._capabilities = self._get_capabilities()

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider name."""
        pass

    @property
    def model_name(self) -> str:
        """Model name."""
        return self.model

    @property
    def capabilities(self) -> ModelCapabilities:
        """Model capabilities."""
        return self._capabilities

    @property
    def supports_tools(self) -> bool:
        """Whether model supports tool calling."""
        return self._capabilities.supports_tools

    @abstractmethod
    def _get_capabilities(self) -> ModelCapabilities:
        """Get model capabilities."""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def embed(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[list[float]]:
        """Generate embeddings."""
        pass

    def count_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)."""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4

    def count_message_tokens(self, messages: list[Message]) -> int:
        """Count tokens in messages."""
        total = 0
        for msg in messages:
            total += self.count_tokens(msg.content)
            if msg.tool_calls:
                import json
                total += self.count_tokens(json.dumps(msg.tool_calls))
        return total