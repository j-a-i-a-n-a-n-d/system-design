"""Budget management for token and cost tracking."""

from typing import Optional
from dataclasses import dataclass, field
from pydantic import BaseModel
import time


@dataclass
class TokenBudget:
    """Token usage budget."""
    limit: int = 100000  # tokens per minute
    used: int = 0
    window_start: float = field(default_factory=time.time)
    window_seconds: int = 60

    def check(self, tokens: int) -> bool:
        """Check if tokens can be used."""
        self._reset_window()
        return self.used + tokens <= self.limit

    def consume(self, tokens: int) -> bool:
        """Consume tokens if available."""
        self._reset_window()
        if self.used + tokens <= self.limit:
            self.used += tokens
            return True
        return False

    def _reset_window(self) -> None:
        """Reset window if expired."""
        now = time.time()
        if now - self.window_start >= self.window_seconds:
            self.used = 0
            self.window_start = now

    def remaining(self) -> int:
        """Get remaining tokens in window."""
        self._reset_window()
        return max(0, self.limit - self.used)

    def reset(self) -> None:
        """Reset budget."""
        self.used = 0
        self.window_start = time.time()


@dataclass
class CostBudget:
    """Cost budget in USD."""
    limit_per_hour: float = 10.0
    limit_per_task: float = 0.50
    used_per_hour: float = 0.0
    used_per_task: float = 0.0
    hour_window_start: float = field(default_factory=time.time)
    task_start: float = field(default_factory=time.time)

    def check_hourly(self, cost: float) -> bool:
        """Check hourly budget."""
        self._reset_hourly()
        return self.used_per_hour + cost <= self.limit_per_hour

    def check_task(self, cost: float) -> bool:
        """Check task budget."""
        return self.used_per_task + cost <= self.limit_per_task

    def consume(self, cost: float) -> bool:
        """Consume cost if within both budgets."""
        self._reset_hourly()
        if self.used_per_hour + cost > self.limit_per_hour:
            return False
        if self.used_per_task + cost > self.limit_per_task:
            return False
        self.used_per_hour += cost
        self.used_per_task += cost
        return True

    def _reset_hourly(self) -> None:
        """Reset hourly window."""
        now = time.time()
        if now - self.hour_window_start >= 3600:
            self.used_per_hour = 0.0
            self.hour_window_start = now

    def reset_task(self) -> None:
        """Reset task budget."""
        self.used_per_task = 0.0
        self.task_start = time.time()

    def remaining_hourly(self) -> float:
        """Get remaining hourly budget."""
        self._reset_hourly()
        return max(0.0, self.limit_per_hour - self.used_per_hour)

    def remaining_task(self) -> float:
        """Get remaining task budget."""
        return max(0.0, self.limit_per_task - self.used_per_task)


class BudgetManager:
    """Manages token and cost budgets."""
    
    # Model pricing (USD per 1M tokens) - approximate
    MODEL_PRICING = {
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "claude-3.5-sonnet": {"input": 3.00, "output": 15.00},
        "claude-3.5-haiku": {"input": 0.25, "output": 1.25},
        "claude-3-opus": {"input": 15.00, "output": 75.00},
    }

    def __init__(
        self,
        token_limit: int = 100000,
        hourly_cost_limit: float = 10.0,
        task_cost_limit: float = 0.50,
    ):
        self.tokens = TokenBudget(limit=token_limit)
        self.cost = CostBudget(
            limit_per_hour=hourly_cost_limit,
            limit_per_task=task_cost_limit,
        )

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a model call."""
        pricing = self.MODEL_PRICING.get(model, {"input": 1.0, "output": 3.0})
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def can_afford(self, model: str, estimated_input: int, estimated_output: int) -> bool:
        """Check if estimated cost fits in budget."""
        estimated = self.estimate_cost(model, estimated_input, estimated_output)
        return self.cost.check_hourly(estimated) and self.cost.check_task(estimated)

    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Record actual usage and return cost."""
        cost = self.estimate_cost(model, input_tokens, output_tokens)
        self.cost.consume(cost)
        self.tokens.consume(input_tokens + output_tokens)
        return cost

    def get_status(self) -> dict:
        """Get budget status."""
        return {
            "tokens": {
                "limit": self.tokens.limit,
                "used": self.tokens.used,
                "remaining": self.tokens.remaining(),
            },
            "cost_hourly": {
                "limit": self.cost.limit_per_hour,
                "used": self.cost.used_per_hour,
                "remaining": self.cost.remaining_hourly(),
            },
            "cost_task": {
                "limit": self.cost.limit_per_task,
                "used": self.cost.used_per_task,
                "remaining": self.cost.remaining_task(),
            },
        }

    def reset_task(self) -> None:
        """Reset task-level budgets."""
        self.cost.reset_task()

    def reset_all(self) -> None:
        """Reset all budgets."""
        self.tokens.reset()
        self.cost.used_per_hour = 0.0
        self.cost.hour_window_start = time.time()
        self.cost.reset_task()