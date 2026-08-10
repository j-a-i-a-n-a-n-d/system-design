"""Tool schema generation utilities."""

from typing import Any
from pydantic import BaseModel, Field
from .base import Tool, ToolSchema


def generate_schema(tool: Tool) -> ToolSchema:
    """Generate schema for a tool."""
    return tool.get_schema()


def generate_schemas(tools: list[Tool]) -> list[ToolSchema]:
    """Generate schemas for multiple tools."""
    return [generate_schema(tool) for tool in tools]


def schema_to_openai(tool_schema: ToolSchema) -> dict:
    """Convert tool schema to OpenAI format."""
    return {
        "type": "function",
        "function": {
            "name": tool_schema.name,
            "description": tool_schema.description,
            "parameters": tool_schema.parameters,
        },
    }


def schema_to_anthropic(tool_schema: ToolSchema) -> dict:
    """Convert tool schema to Anthropic format."""
    return {
        "name": tool_schema.name,
        "description": tool_schema.description,
        "input_schema": tool_schema.parameters,
    }


def schema_to_mcp(tool_schema: ToolSchema) -> dict:
    """Convert tool schema to MCP format."""
    return {
        "name": tool_schema.name,
        "description": tool_schema.description,
        "inputSchema": tool_schema.parameters,
    }


class SchemaGenerator:
    """Generates schemas in multiple formats."""
    
    def __init__(self):
        self._formatters = {
            "openai": schema_to_openai,
            "anthropic": schema_to_anthropic,
            "mcp": schema_to_mcp,
        }
    
    def register_formatter(self, format_name: str, formatter: callable) -> None:
        """Register a custom formatter."""
        self._formatters[format_name] = formatter
    
    def generate(self, tool: Tool, format: str = "openai") -> dict:
        """Generate schema in specified format."""
        schema = generate_schema(tool)
        formatter = self._formatters.get(format)
        if not formatter:
            raise ValueError(f"Unknown format: {format}")
        return formatter(schema)
    
    def generate_all(self, tools: list[Tool], format: str = "openai") -> list[dict]:
        """Generate schemas for all tools in specified format."""
        return [self.generate(tool, format) for tool in tools]