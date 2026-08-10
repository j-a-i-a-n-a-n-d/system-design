"""Observer - evaluates execution results and decides next actions."""

from typing import Any, Optional
from pydantic import BaseModel
from ..agent.base import Agent, PlanStep, ExecutionResult, Observation
from ..gateway.base import LLMGateway, Message
from ..config import get_settings
from ..observability import get_tracer, trace_agent_step
import json


class Observer:
    """Evaluates tool execution results and decides next actions."""
    
    OBSERVATION_PROMPT = """You are an observation agent. Evaluate the result of a tool execution and decide what to do next.

Goal: {goal}
Current Step: {step_description}
Tool Used: {tool_name}
Tool Arguments: {tool_args}

Execution Result:
- Success: {success}
- Output: {output}
- Error: {error}
- Duration: {duration_ms}ms

Full Plan:
{plan}

Recent Conversation:
{conversation}

Decide the next action. Output JSON:
{{
  "should_continue": true,
  "summary": "Brief summary of what happened",
  "details": {{}},
  "next_action": "continue|retry|skip|revise_plan|complete",
  "modified_plan": null
}}

Guidelines:
- should_continue: false only if goal is achieved or unrecoverable error
- next_action: 
  - "continue": proceed to next step normally
  - "retry": retry current step (increment retry_count)
  - "skip": skip current step, mark as failed, continue
  - "revise_plan": modify the plan (provide modified_plan)
  - "complete": goal achieved, stop execution
- modified_plan: if next_action is "revise_plan", provide full new plan as array of steps"""


    def __init__(self, gateway: LLMGateway):
        self.gateway = gateway
        self.settings = get_settings()

    async def observe(
        self,
        agent: Agent,
        step: PlanStep,
        result: ExecutionResult,
    ) -> Observation:
        """Observe execution result and decide next action."""
        with trace_agent_step("observation", agent.session_id, step_id=step.step_id) as span:
            span.set_attribute("success", result.success)
            
            # For simple cases, use heuristic
            if not result.success and step.retry_count < self.settings.agent.max_retries:
                return Observation(
                    step_id=step.step_id,
                    success=False,
                    summary=f"Step failed: {result.error}. Will retry.",
                    details={"error": result.error},
                    should_continue=True,
                    next_action="retry",
                )
            
            if not result.success and step.retry_count >= self.settings.agent.max_retries:
                return Observation(
                    step_id=step.step_id,
                    success=False,
                    summary=f"Step failed after {step.retry_count} retries: {result.error}",
                    details={"error": result.error, "retries": step.retry_count},
                    should_continue=True,
                    next_action="skip",
                )
            
            # For successful steps or complex decisions, use LLM
            return await self._llm_observe(agent, step, result)

    async def _llm_observe(
        self,
        agent: Agent,
        step: PlanStep,
        result: ExecutionResult,
    ) -> Observation:
        """Use LLM to observe and decide."""
        # Prepare plan summary
        plan_summary = "\n".join([
            f"  {i+1}. {s.description} {'✓' if s.completed else '○'} {'(current)' if i == agent.memory.current_step_index else ''}"
            for i, s in enumerate(agent.memory.plan)
        ])
        
        # Prepare conversation summary
        recent = agent.conversation[-5:] if agent.conversation else []
        conv_summary = "\n".join([
            f"  {msg.role}: {msg.content[:200]}..."
            for msg in recent
        ])
        
        prompt = self.OBSERVATION_PROMPT.format(
            goal=agent.memory.goal,
            step_description=step.description,
            tool_name=step.tool_name or "none",
            tool_args=json.dumps(step.tool_args, indent=2),
            success=result.success,
            output=str(result.output)[:2000] if result.output else "none",
            error=result.error or "none",
            duration_ms=result.duration_ms,
            plan=plan_summary,
            conversation=conv_summary or "none",
        )
        
        messages = [
            Message(role="system", content=self.settings.agent.system_prompt or "You are an observation assistant."),
            Message(role="user", content=prompt),
        ]
        
        response = await self.gateway.complete(messages, tools=[])
        
        # Parse response
        try:
            obs_data = self._parse_observation(response.content)
            return Observation(
                step_id=step.step_id,
                success=result.success,
                **obs_data,
            )
        except Exception:
            # Fallback to simple heuristic
            return Observation(
                step_id=step.step_id,
                success=result.success,
                summary="Step completed" if result.success else f"Step failed: {result.error}",
                should_continue=True,
                next_action="continue",
            )

    def _parse_observation(self, content: str) -> dict:
        """Parse observation from LLM response."""
        content = content.strip()
        
        # Extract JSON
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()
        
        import json
        return json.loads(content)