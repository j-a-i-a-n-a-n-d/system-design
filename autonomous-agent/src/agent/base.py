"""Agent base classes and state machine."""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional
from pydantic import BaseModel, Field
import uuid
import time


class AgentState(str, Enum):
    """Agent execution states."""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    OBSERVING = "observing"
    REFLECTING = "reflecting"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AgentConfig:
    """Agent runtime configuration."""
    max_steps: int = 20
    max_retries: int = 3
    default_timeout: int = 30
    working_dir: str = "~/.agent/workspace"
    system_prompt: str = ""


class PlanStep(BaseModel):
    """A single step in the execution plan."""
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str
    tool_name: Optional[str] = None
    tool_args: dict[str, Any] = Field(default_factory=dict)
    expected_outcome: str = ""
    dependencies: list[str] = Field(default_factory=list)
    completed: bool = False
    result: Any = None
    error: Optional[str] = None
    retry_count: int = 0


class ExecutionResult(BaseModel):
    """Result of tool execution."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0
    tool_name: str = ""
    step_id: str = ""


class Observation(BaseModel):
    """Observation from executor."""
    step_id: str
    success: bool
    summary: str
    details: Any = None
    should_continue: bool = True
    next_action: Optional[str] = None
    modified_plan: Optional[list[PlanStep]] = None


class ConversationMessage(BaseModel):
    """A message in the conversation history."""
    role: str  # user, assistant, tool, system
    content: str
    tool_calls: list[dict] = Field(default_factory=list)
    tool_call_id: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    metadata: dict = Field(default_factory=dict)


class WorkingMemory(BaseModel):
    """Agent's working memory for the current task."""
    goal: str = ""
    plan: list[PlanStep] = Field(default_factory=list)
    current_step_index: int = 0
    context: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class Agent(BaseModel):
    """Base agent class with state machine."""
    
    # Configuration
    config: AgentConfig = Field(default_factory=AgentConfig)
    
    # State
    state: AgentState = AgentState.IDLE
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    memory: WorkingMemory = Field(default_factory=WorkingMemory)
    conversation: list[ConversationMessage] = Field(default_factory=list)
    
    # Metrics
    steps_taken: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    
    # Error handling
    last_error: Optional[str] = None
    consecutive_failures: int = 0

    class Config:
        arbitrary_types_allowed = True

    def transition(self, new_state: AgentState) -> None:
        """Transition to a new state."""
        self.state = new_state

    def add_message(self, role: str, content: str, **kwargs) -> None:
        """Add a message to conversation history."""
        self.conversation.append(ConversationMessage(role=role, content=content, **kwargs))

    def get_current_step(self) -> Optional[PlanStep]:
        """Get the current plan step."""
        if 0 <= self.memory.current_step_index < len(self.memory.plan):
            return self.memory.plan[self.memory.current_step_index]
        return None

    def advance_step(self) -> bool:
        """Advance to next step. Returns True if there are more steps."""
        self.memory.current_step_index += 1
        return self.memory.current_step_index < len(self.memory.plan)

    def record_execution(self, result: ExecutionResult) -> None:
        """Record tool execution result."""
        self.steps_taken += 1
        if result.success:
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1
            self.last_error = result.error
            self.memory.errors.append(result.error or "Unknown error")

    def is_complete(self) -> bool:
        """Check if agent has completed its task."""
        return (
            self.state == AgentState.COMPLETED or
            self.steps_taken >= self.config.max_steps or
            self.consecutive_failures >= self.config.max_retries
        )

    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        end = self.end_time or time.time()
        return end - self.start_time

    def to_dict(self) -> dict:
        """Serialize agent state."""
        return {
            "session_id": self.session_id,
            "state": self.state.value,
            "goal": self.memory.goal,
            "steps_taken": self.steps_taken,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "elapsed_time": self.get_elapsed_time(),
            "plan": [step.model_dump() for step in self.memory.plan],
            "conversation_length": len(self.conversation),
        }