"""Azure OpenAI Gateway implementation."""

from typing import Any, Optional
import time
from openai import AsyncAzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from .base import LLMGateway, Message, ToolSchema, LLMResponse, ModelCapabilities, MessageRole


class AzureOpenAIGateway(LLMGateway):
    """Azure OpenAI API gateway."""
    
    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        api_version: str = "2024-02-15-preview",
        deployment_name: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(model, api_key, **kwargs)
        self.deployment_name = deployment_name or model
        self.client = AsyncAzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
        )

    @property
    def provider_name(self) -> str:
        return "azure_openai"

    def _get_capabilities(self) -> ModelCapabilities:
        caps = ModelCapabilities()
        
        if "gpt-4o" in self.model:
            caps.max_context = 128000
            caps.max_output = 16384
        elif "gpt-4" in self.model:
            caps.max_context = 128000
            caps.max_output = 4096
        
        return caps

    def _format_messages(self, messages: list[Message]) -> list[dict]:
        """Format messages for Azure OpenAI API."""
        formatted = []
        for msg in messages:
            m = {"role": msg.role.value, "content": msg.content}
            
            if msg.tool_calls:
                m["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                m["tool_call_id"] = msg.tool_call_id
                m["role"] = "tool"
            if msg.name:
                m["name"] = msg.name
            
            formatted.append(m)
        return formatted

    def _format_tools(self, tools: list[ToolSchema]) -> list[dict]:
        """Format tools for Azure OpenAI API."""
        formatted = []
        for tool in tools:
            formatted.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
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
        formatted_tools = self._format_tools(tools) if tools else None
        
        try:
            if stream:
                return await self._stream_complete(
                    formatted_messages, formatted_tools, temperature, max_tokens, **kwargs
                )
            
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=formatted_messages,
                tools=formatted_tools,
                tool_choice="auto" if formatted_tools else None,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            
            choice = response.choices[0]
            tool_calls = []
            if choice.message.tool_calls:
                for tc in choice.message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    })
            
            usage = {}
            if response.usage:
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            
            return LLMResponse(
                content=choice.message.content or "",
                tool_calls=tool_calls,
                model=response.model,
                usage=usage,
                finish_reason=choice.finish_reason,
                latency_ms=(time.perf_counter() - start) * 1000,
            )
            
        except Exception as e:
            raise RuntimeError(f"Azure OpenAI API error: {e}") from e

    async def _stream_complete(
        self,
        messages: list[dict],
        tools: list[dict],
        temperature: float,
        max_tokens: Optional[int],
        **kwargs,
    ) -> LLMResponse:
        """Handle streaming completion."""
        stream = await self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            tools=tools,
            tool_choice="auto" if tools else None,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )
        
        content_parts = []
        tool_calls = []
        usage = {}
        
        async for chunk in stream:
            if chunk.choices:
                choice = chunk.choices[0]
                if choice.delta.content:
                    content_parts.append(choice.delta.content)
                if choice.delta.tool_calls:
                    for tc in choice.delta.tool_calls:
                        if tc.index >= len(tool_calls):
                            tool_calls.append({
                                "id": tc.id,
                                "type": "function",
                                "function": {"name": "", "arguments": ""},
                            })
                        if tc.function.name:
                            tool_calls[tc.index]["function"]["name"] = tc.function.name
                        if tc.function.arguments:
                            tool_calls[tc.index]["function"]["arguments"] += tc.function.arguments
            
            if chunk.usage:
                usage = {
                    "prompt_tokens": chunk.usage.prompt_tokens,
                    "completion_tokens": chunk.usage.completion_tokens,
                    "total_tokens": chunk.usage.total_tokens,
                }
        
        return LLMResponse(
            content="".join(content_parts),
            tool_calls=tool_calls,
            model=self.model,
            usage=usage,
            finish_reason="stop",
            latency_ms=0,
        )

    async def embed(
        self,
        texts: list[str],
        **kwargs,
    ) -> list[list[float]]:
        """Generate embeddings."""
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
            **kwargs,
        )
        return [d.embedding for d in response.data]