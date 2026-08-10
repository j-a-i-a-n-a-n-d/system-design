"""Memory management for agent."""

from typing import Any, Optional
from pydantic import BaseModel, Field
from ..agent.base import ConversationMessage, WorkingMemory
import time


class Memory:
    """Manages agent memory: conversation, working memory, and artifacts."""
    
    def __init__(self, max_conversation_length: int = 100):
        self.max_conversation_length = max_conversation_length
        self.conversation: list[ConversationMessage] = []
        self.working_memory = WorkingMemory()
        self._artifact_store: dict[str, Any] = {}

    def add_message(self, role: str, content: str, **kwargs) -> ConversationMessage:
        """Add a message to conversation history."""
        msg = ConversationMessage(role=role, content=content, **kwargs)
        self.conversation.append(msg)
        self._trim_conversation()
        return msg

    def _trim_conversation(self) -> None:
        """Trim conversation to max length, keeping system messages."""
        if len(self.conversation) <= self.max_conversation_length:
            return
        
        # Keep system messages and recent messages
        system_msgs = [m for m in self.conversation if m.role == "system"]
        other_msgs = [m for m in self.conversation if m.role != "system"]
        
        keep_count = self.max_conversation_length - len(system_msgs)
        if keep_count < 10:
            keep_count = 10
        
        self.conversation = system_msgs + other_msgs[-keep_count:]

    def get_recent(self, n: int = 10) -> list[ConversationMessage]:
        """Get N most recent messages."""
        return self.conversation[-n:]

    def get_messages_for_llm(self, include_system: bool = True) -> list[dict]:
        """Get messages formatted for LLM API."""
        msgs = []
        for msg in self.conversation:
            if msg.role == "system" and not include_system:
                continue
            
            llm_msg = {"role": msg.role, "content": msg.content}
            
            if msg.tool_calls:
                llm_msg["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                llm_msg["tool_call_id"] = msg.tool_call_id
            
            msgs.append(llm_msg)
        
        return msgs

    def set_goal(self, goal: str) -> None:
        """Set the current goal."""
        self.working_memory.goal = goal

    def set_plan(self, plan: list) -> None:
        """Set the execution plan."""
        self.working_memory.plan = plan
        self.working_memory.current_step_index = 0

    def get_current_step(self) -> Optional[Any]:
        """Get current plan step."""
        idx = self.working_memory.current_step_index
        if 0 <= idx < len(self.working_memory.plan):
            return self.working_memory.plan[idx]
        return None

    def advance_step(self) -> bool:
        """Advance to next step."""
        self.working_memory.current_step_index += 1
        return self.working_memory.current_step_index < len(self.working_memory.plan)

    def store_artifact(self, key: str, value: Any) -> None:
        """Store an artifact in working memory."""
        self._artifact_store[key] = value
        self.working_memory.artifacts[key] = value

    def get_artifact(self, key: str, default: Any = None) -> Any:
        """Retrieve an artifact."""
        return self._artifact_store.get(key, default)

    def update_context(self, key: str, value: Any) -> None:
        """Update working memory context."""
        self.working_memory.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get working memory context."""
        return self.working_memory.context.get(key, default)

    def add_error(self, error: str) -> None:
        """Record an error."""
        self.working_memory.errors.append({
            "error": error,
            "timestamp": time.time(),
        })

    def get_summary(self) -> dict:
        """Get memory summary for debugging."""
        return {
            "conversation_length": len(self.conversation),
            "goal": self.working_memory.goal,
            "plan_length": len(self.working_memory.plan),
            "current_step": self.working_memory.current_step_index,
            "artifacts": list(self._artifact_store.keys()),
            "context_keys": list(self.working_memory.context.keys()),
            "error_count": len(self.working_memory.errors),
        }

    def clear(self) -> None:
        """Clear all memory."""
        self.conversation.clear()
        self.working_memory = WorkingMemory()
        self._artifact_store.clear()