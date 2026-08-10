"""Planner - decomposes goals into executable steps."""

from typing import Any, Optional
from pydantic import BaseModel, Field
from ..agent.base import PlanStep, Agent, AgentState
from ..gateway.base import LLMGateway, Message, ToolSchema
from ..config import get_settings
from ..observability import get_tracer, trace_agent_step
import json


class Planner:
    """Decomposes high-level goals into executable plan steps."""
    
    PLANNING_PROMPT = """You are a planning agent. Break down the user's goal into a sequence of executable steps.

Goal: {goal}

Available Tools:
{tools}

Context:
{context}

Create a detailed plan with the following JSON structure:
{{
  "plan": [
    {{
      "step_id": "step_1",
      "description": "Clear description of what this step accomplishes",
      "tool_name": "tool_name_or_null",
      "tool_args": {{"arg1": "value1"}},
      "expected_outcome": "What should be true after this step",
      "dependencies": ["step_id_of_prerequisite"]
    }}
  ]
}}

Guidelines:
- Each step should be atomic and independently verifiable
- Use tools when external action is needed
- Steps with no tool are reasoning/synthesis steps
- Include dependencies between steps
- Aim for 3-10 steps for typical tasks
- Be specific about tool arguments

Output ONLY valid JSON."""

    def __init__(self, gateway: LLMGateway):
        self.gateway = gateway
        self.settings = get_settings()

    async def create_plan(
        self,
        agent: Agent,
        goal: str,
        available_tools: list[ToolSchema],
        context: Optional[dict[str, Any]] = None,
    ) -> list[PlanStep]:
        """Create an execution plan for the goal."""
        with trace_agent_step("planning", agent.session_id) as span:
            span.set_attribute("goal", goal)
            
            # Prepare tools description
            tools_desc = self._format_tools(available_tools)
            
            # Prepare context
            ctx = context or {}
            ctx_str = json.dumps(ctx, indent=2) if ctx else "{}"
            
            # Build prompt
            prompt = self.PLANNING_PROMPT.format(
                goal=goal,
                tools=tools_desc,
                context=ctx_str,
            )
            
            # Call LLM
            messages = [
                Message(role="system", content=self.settings.agent.system_prompt or "You are a helpful planning assistant."),
                Message(role="user", content=prompt),
            ]
            
            response = await self.gateway.complete(messages, tools=[])
            
            # Parse response
            plan_data = self._parse_plan_response(response.content)
            
            # Convert to PlanStep objects
            steps = [PlanStep(**step) for step in plan_data.get("plan", [])]
            
            # Update agent
            agent.memory.goal = goal
            agent.memory.plan = steps
            agent.memory.current_step_index = 0
            
            span.set_attribute("num_steps", len(steps))
            return steps

    def _format_tools(self, tools: list[ToolSchema]) -> str:
        """Format tools for prompt."""
        if not tools:
            return "No tools available."
        
        lines = []
        for tool in tools:
            params = tool.parameters
            param_desc = ""
            if params and "properties" in params:
                for name, info in params["properties"].items():
                    required = name in params.get("required", [])
                    req_str = " (required)" if required else ""
                    param_desc += f"    - {name}: {info.get('description', '')}{req_str}\n"
            
            lines.append(f"- {tool.name}: {tool.description}\n{param_desc}")
        
        return "\n".join(lines)

    def _parse_plan_response(self, content: str) -> dict:
        """Parse JSON plan from LLM response."""
        # Try to extract JSON from response
        content = content.strip()
        
        # Find JSON block
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end].strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Fallback: try to find JSON object
            import re
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Failed to parse plan: {e}")

    async def revise_plan(
        self,
        agent: Agent,
        observation: str,
        available_tools: list[ToolSchema],
    ) -> list[PlanStep]:
        """Revise plan based on observation."""
        # For now, return current plan unchanged
        # In future, implement plan revision logic
        return agent.memory.plan