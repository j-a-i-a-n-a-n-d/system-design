"""Model router for intelligent model selection."""

from typing import Any, Optional
from dataclasses import dataclass
from pydantic import BaseModel
from .base import LLMGateway, ModelCapabilities


@dataclass
class RoutingRule:
    """A routing rule for model selection."""
    name: str
    condition: str  # e.g., "simple", "complex", "code", "reasoning"
    model: str
    priority: int = 0


class ModelRouter:
    """Routes requests to appropriate models based on task complexity."""
    
    DEFAULT_RULES = [
        RoutingRule("simple", "simple", "gpt-4o-mini", priority=10),
        RoutingRule("complex", "complex", "gpt-4o", priority=10),
        RoutingRule("code", "code", "claude-3.5-sonnet", priority=10),
        RoutingRule("reasoning", "reasoning", "gpt-4o", priority=10),
        RoutingRule("default", "default", "gpt-4o-mini", priority=0),
    ]
    
    def __init__(
        self,
        gateways: dict[str, LLMGateway],
        rules: Optional[list[RoutingRule]] = None,
    ):
        self.gateways = gateways
        self.rules = rules or self.DEFAULT_RULES
        self._rule_map = {r.condition: r for r in self.rules}

    def get_gateway(self, task_type: str = "default") -> LLMGateway:
        """Get gateway for task type."""
        rule = self._rule_map.get(task_type, self._rule_map["default"])
        gateway = self.gateways.get(rule.model)
        if not gateway:
            # Fallback to first available
            gateway = next(iter(self.gateways.values()))
        return gateway

    def get_model_for_task(self, task_type: str) -> str:
        """Get model name for task type."""
        rule = self._rule_map.get(task_type, self._rule_map["default"])
        return rule.model

    def classify_task(self, prompt: str, tools: list = None) -> str:
        """Classify task type from prompt."""
        prompt_lower = prompt.lower()
        
        # Code-related keywords
        code_keywords = [
            "code", "function", "class", "api", "endpoint", "database",
            "sql", "query", "script", "program", "debug", "refactor",
            "implement", "write", "create", "build", "develop",
        ]
        
        # Complex reasoning keywords
        complex_keywords = [
            "analyze", "compare", "evaluate", "design", "architect",
            "strategy", "plan", "optimize", "research", "investigate",
        ]
        
        # Simple task keywords
        simple_keywords = [
            "summarize", "explain", "list", "what is", "define",
            "describe", "translate", "format", "convert",
        ]
        
        # Check for code task
        if any(kw in prompt_lower for kw in code_keywords):
            return "code"
        
        # Check for complex task
        if any(kw in prompt_lower for kw in complex_keywords):
            return "complex"
        
        # Check for simple task
        if any(kw in prompt_lower for kw in simple_keywords):
            return "simple"
        
        return "default"

    async def route_and_complete(
        self,
        messages: list,
        tools: list = None,
        task_type: str = None,
        **kwargs,
    ):
        """Route to appropriate model and complete."""
        if task_type is None:
            # Extract prompt for classification
            prompt = ""
            for msg in messages:
                if msg.role == "user":
                    prompt = msg.content
                    break
            task_type = self.classify_task(prompt, tools)
        
        gateway = self.get_gateway(task_type)
        return await gateway.complete(messages, tools, **kwargs)