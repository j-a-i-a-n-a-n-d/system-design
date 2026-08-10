"""Executor - executes tools and handles errors."""

from typing import Any, Optional
from pydantic import BaseModel
from ..agent.base import Agent, ExecutionResult, PlanStep, AgentState
from ..tools.registry import ToolRegistry
from ..guardrails import CommandFilter, FilesystemJail, RateLimiter
from ..observability import get_tracer, trace_agent_step
from ..config import get_settings
import time
import traceback


class Executor:
    """Executes plan steps using registered tools."""
    
    def __init__(
        self,
        tool_registry: ToolRegistry,
        command_filter: Optional[CommandFilter] = None,
        fs_jail: Optional[FilesystemJail] = None,
        rate_limiter: Optional[RateLimiter] = None,
    ):
        self.tool_registry = tool_registry
        self.command_filter = command_filter
        self.fs_jail = fs_jail
        self.rate_limiter = rate_limiter
        self.settings = get_settings()

    async def execute_step(
        self,
        agent: Agent,
        step: PlanStep,
    ) -> ExecutionResult:
        """Execute a single plan step."""
        with trace_agent_step("execution", agent.session_id, step_id=step.step_id) as span:
            span.set_attribute("tool", step.tool_name or "none")
            span.set_attribute("description", step.description)
            
            start_time = time.perf_counter()
            
            # Check if step has a tool
            if not step.tool_name:
                # Reasoning step - no tool execution needed
                result = ExecutionResult(
                    success=True,
                    output="Reasoning step completed",
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                    step_id=step.step_id,
                )
                return result
            
            # Get tool
            tool = self.tool_registry.get(step.tool_name)
            if not tool:
                return ExecutionResult(
                    success=False,
                    error=f"Tool '{step.tool_name}' not found",
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                    tool_name=step.tool_name,
                    step_id=step.step_id,
                )
            
            # Validate tool arguments
            try:
                validated_args = self._validate_args(tool, step.tool_args)
            except ValueError as e:
                return ExecutionResult(
                    success=False,
                    error=f"Invalid arguments: {e}",
                    duration_ms=(time.perf_counter() - start_time) * 1000,
                    tool_name=step.tool_name,
                    step_id=step.step_id,
                )
            
            # Check rate limits
            if self.rate_limiter:
                allowed = await self.rate_limiter.check_limit("tool_execution")
                if not allowed:
                    return ExecutionResult(
                        success=False,
                        error="Rate limit exceeded",
                        duration_ms=(time.perf_counter() - start_time) * 1000,
                        tool_name=step.tool_name,
                        step_id=step.step_id,
                    )
            
            # Execute tool with retries
            last_error = None
            for attempt in range(self.settings.agent.max_retries + 1):
                try:
                    # Run tool
                    output = await tool.execute(**validated_args)
                    
                    duration = (time.perf_counter() - start_time) * 1000
                    
                    result = ExecutionResult(
                        success=True,
                        output=output,
                        duration_ms=duration,
                        tool_name=step.tool_name,
                        step_id=step.step_id,
                    )
                    
                    span.set_attribute("success", True)
                    span.set_attribute("duration_ms", duration)
                    return result
                    
                except Exception as e:
                    last_error = e
                    duration = (time.perf_counter() - start_time) * 1000
                    
                    if attempt < self.settings.agent.max_retries:
                        # Wait before retry
                        import asyncio
                        await asyncio.sleep(0.5 * (attempt + 1))
                        continue
                    
                    # All retries exhausted
                    error_msg = f"{type(e).__name__}: {e}"
                    span.set_attribute("success", False)
                    span.set_attribute("error", error_msg)
                    span.record_exception(e)
                    
                    return ExecutionResult(
                        success=False,
                        error=error_msg,
                        duration_ms=duration,
                        tool_name=step.tool_name,
                        step_id=step.step_id,
                    )
            
            # Should not reach here
            return ExecutionResult(
                success=False,
                error=f"Execution failed after retries: {last_error}",
                duration_ms=(time.perf_counter() - start_time) * 1000,
                tool_name=step.tool_name,
                step_id=step.step_id,
            )

    def _validate_args(self, tool, args: dict) -> dict:
        """Validate and coerce tool arguments."""
        # Get tool schema
        schema = tool.get_schema()
        if not schema or "parameters" not in schema:
            return args
        
        params = schema["parameters"]
        required = params.get("required", [])
        properties = params.get("properties", {})
        
        # Check required args
        for req in required:
            if req not in args:
                raise ValueError(f"Missing required argument: {req}")
        
        # Coerce types
        validated = {}
        for key, value in args.items():
            if key in properties:
                prop = properties[key]
                validated[key] = self._coerce_type(value, prop)
            else:
                validated[key] = value
        
        return validated

    def _coerce_type(self, value: Any, prop: dict) -> Any:
        """Coerce value to match property type."""
        prop_type = prop.get("type", "string")
        
        if prop_type == "integer" and isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return value
        elif prop_type == "number" and isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return value
        elif prop_type == "boolean" and isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        elif prop_type == "array" and not isinstance(value, list):
            return [value]
        
        return value

    async def execute_plan(
        self,
        agent: Agent,
        planner,
        observer,
    ) -> None:
        """Execute the full plan with observation loop."""
        agent.transition(AgentState.EXECUTING)
        
        while not agent.is_complete():
            step = agent.get_current_step()
            if not step:
                break
            
            # Execute step
            result = await self.execute_step(agent, step)
            agent.record_execution(result)
            
            # Update step with result
            step.completed = True
            step.result = result.output if result.success else None
            step.error = result.error
            
            # Observe result
            observation = await observer.observe(agent, step, result)
            
            # Check if we should continue
            if not observation.should_continue:
                agent.transition(AgentState.COMPLETED)
                break
            
            # Handle plan modifications
            if observation.modified_plan:
                agent.memory.plan = observation.modified_plan
            
            # Advance to next step
            if not agent.advance_step():
                agent.transition(AgentState.COMPLETED)
                break
        
        agent.end_time = time.time()