"""Anthropic Gateway implementation."""

from typing import Any, Optional
import time
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from .base import LLMGateway, Message, ToolSchema, LLMResponse, ModelCapabilities, MessageRole


class AnthropicGateway(LLMGateway):
    """Anthropic API gateway."""
    
    def __init__(
        self,
        model: str = "claude-3.5-sonnet-20241022",
        api_key: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model, api_key, **kwargs)
        self.client = AsyncAnthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def _get_capabilities(self) -> ModelCapabilities:
        caps = ModelCapabilities()
        
        if "opus" in self.model:
            caps.max_context = 200000
            caps.max_output = 4096
        elif "sonnet" in self.model:
            caps.max_context = 200000
            caps.max_output = 8192
        elif "haiku" in self.model:
            caps.max_context = 200000
            caps.max_output = 4096
        
        return caps

    def _format_messages(self, messages: list[Message]) -> tuple[str, list[dict]]:
        """Format messages for Anthropic API. Returns (system_prompt, messages)."""
        system_parts = []
        formatted = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_parts.append(msg.content)
            elif msg.role == MessageRole.TOOL:
                # Tool results are user messages with tool_result content
                formatted.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg.tool_call_id,
                            "content": msg.content,
                        }
                    ],
                })
            elif msg.role == MessageRole.ASSISTANT and msg.tool_calls:
                # Assistant with tool calls
                content = []
                if msg.content:
                    content.append({"type": "text", "text": msg.content})
                for tc in msg.tool_calls:
                    content.append({
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "input": json.loads(tc["function"]["arguments"]),
                    })
                formatted.append({"role": "assistant", "content": content})
            else:
                formatted.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })
        
        system = "\n\n".join(system_parts) if system_parts else ""
        return system, formatted

    def _format_tools(self, tools: list[ToolSchema]) -> list[dict]:
        """Format tools for Anthropic API."""
        formatted = []
        for tool in tools:
            formatted.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters,
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
        
        system, formatted_messages = self._format_messages(messages)
        formatted_tools = self._format_tools(tools) if tools else None
        
        try:
            if stream:
                return await self._stream_complete(
                    system, formatted_messages, formatted_tools, temperature, max_tokens, **kwargs
                )
            
            response = await self.client.messages.create(
                model=self.model,
                system=system if system else None,
                messages=formatted_messages,
                tools=formatted_tools,
                tool_choice={"type": "auto"} if formatted_tools else None,
                temperature=temperature,
                max_tokens=max_tokens or 4096,
                **kwargs,
            )
            
            content = ""
            tool_calls = []
            
            for block in response.content:
                if block.type == "text":
                    content += block.text
                elif block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "type": "function",
                        "function": {
                            "name": block.name,
                            "arguments": json.dumps(block.input),
                        },
                    })
            
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }
            
            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                model=response.model,
                usage=usage,
                finish_reason=response.stop_reason,
                latency_ms=(time.perf_counter() - start) * 1000,
            )
            
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}") from e

    async def _stream_complete(
        self,
        system: str,
        messages: list[dict],
        tools: list[dict],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs,
    ) -> LLMResponse:
        """Handle streaming completion."""
        stream = await self.client.messages.create(
            model=self.model,
            system=system if system else None,
            messages=messages,
            tools=tools,
            tool_choice={"type": "auto"} if tools else None,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            stream=True,
            **kwargs,
        )
        
        content_parts = []
        tool_calls = []
        usage = {}
        
        async for chunk in stream:
            if chunk.type == "content_block_delta":
                if chunk.delta.type == "text_delta":
                    content_parts.append(chunk.delta.text)
                elif chunk.delta.type == "input_json_delta":
                    # Handle tool call streaming
                    pass
            elif chunk.type == "message_delta":
                if chunk.usage:
                    usage = {
                        "prompt_tokens": chunk.usage.input_tokens,
                        "completion_tokens": chunk.usage.output_tokens,
                        "total_tokens": chunk.usage.input_tokens + chunk.usage.output_tokens,
                    }
        
        return LLMResponse(
            content="".join(content_parts),
            tool_calls=tool_calls,
            model=self.model,
            usage=usage,
            finish_reason="end_turn",
            latency_ms=0,
        )

    async def embed(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[list[float]]:
        """Anthropic doesn't have embeddings API yet."""
        raise NotImplementedError("Anthropic embeddings not available")

import json