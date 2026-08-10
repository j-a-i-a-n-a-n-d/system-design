"""Tool base classes and registry."""

from abc import ABC, abstractmethod
from typing import Any, Optional, Callable
from pydantic import BaseModel, Field
from functools import wraps
import inspect
import json


class ToolSchema(BaseModel):
    """Tool schema for LLM function calling."""
    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    """Tool execution result."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class Tool(ABC):
    """Base tool class."""
    
    name: str = ""
    description: str = ""
    parameters: dict[str, Any] = {}
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool."""
        pass
    
    def get_schema(self) -> ToolSchema:
        """Get tool schema for LLM."""
        return ToolSchema(
            name=self.name or self.__class__.__name__,
            description=self.description or self.__doc__ or "",
            parameters=self.parameters,
        )
    
    def validate_args(self, args: dict) -> dict:
        """Validate and coerce arguments."""
        return args


class FunctionTool(Tool):
    """Tool wrapping a function."""
    
    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[dict] = None,
    ):
        self.func = func
        self.name = name or func.__name__
        self.description = description or func.__doc__ or ""
        self.parameters = parameters or self._infer_schema(func)
    
    def _infer_schema(self, func: Callable) -> dict:
        """Infer JSON schema from function signature."""
        sig = inspect.signature(func)
        properties = {}
        required = []
        
        for name, param in sig.parameters.items():
            if param.default == inspect.Parameter.empty:
                required.append(name)
            
            # Get type annotation
            ann = param.annotation
            prop = {"type": "string"}  # default
            
            if ann == int:
                prop = {"type": "integer"}
            elif ann == float:
                prop = {"type": "number"}
            elif ann == bool:
                prop = {"type": "boolean"}
            elif ann == list:
                prop = {"type": "array", "items": {"type": "string"}}
            elif ann == dict:
                prop = {"type": "object"}
            
            # Check for docstring parameter descriptions
            if func.__doc__:
                # Simple extraction - could be enhanced
                pass
            
            properties[name] = prop
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }
    
    async def execute(self, **kwargs) -> Any:
        """Execute the wrapped function."""
        if inspect.iscoroutinefunction(self.func):
            return await self.func(**kwargs)
        return self.func(**kwargs)


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parameters: Optional[dict] = None,
) -> Callable:
    """Decorator to create a tool from a function."""
    def decorator(func: Callable) -> FunctionTool:
        return FunctionTool(
            func=func,
            name=name,
            description=description,
            parameters=parameters,
        )
    return decorator


class ToolRegistry:
    """Registry for managing tools."""
    
    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._categories: dict[str, list[str]] = {}
    
    def register(self, tool: Tool, category: str = "general") -> None:
        """Register a tool."""
        tool_name = tool.name or tool.__class__.__name__
        self._tools[tool_name] = tool
        
        if category not in self._categories:
            self._categories[category] = []
        if tool_name not in self._categories[category]:
            self._categories[category].append(tool_name)
    
    def unregister(self, name: str) -> bool:
        """Unregister a tool."""
        if name in self._tools:
            del self._tools[name]
            for cat, tools in self._categories.items():
                if name in tools:
                    tools.remove(name)
            return True
        return False
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_all(self) -> list[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_schemas(self) -> list[ToolSchema]:
        """Get schemas for all tools."""
        return [tool.get_schema() for tool in self._tools.values()]
    
    def get_by_category(self, category: str) -> list[Tool]:
        """Get tools by category."""
        names = self._categories.get(category, [])
        return [self._tools[name] for name in names if name in self._tools]
    
    def list_categories(self) -> list[str]:
        """List all categories."""
        return list(self._categories.keys())
    
    def __contains__(self, name: str) -> bool:
        return name in self._tools
    
    def __len__(self) -> int:
        return len(self._tools)


# Global registry
_global_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get global tool registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry