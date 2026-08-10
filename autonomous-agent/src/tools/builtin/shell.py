"""Shell command execution tool."""

from typing import Any
from pydantic import BaseModel
from ..base import tool, ToolResult
from ..sandbox import get_sandbox


class CommandResult(BaseModel):
    """Result of command execution."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    duration_ms: float = 0


@tool(
    name="run_command",
    description="Execute a shell command",
    parameters={
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Command to execute"},
            "args": {"type": "array", "items": {"type": "string"}, "description": "Command arguments"},
            "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 30},
            "cwd": {"type": "string", "description": "Working directory"},
        },
        "required": ["command"],
    },
)
async def run_command(
    command: str,
    args: list[str] = None,
    timeout: int = 30,
    cwd: str = None,
) -> ToolResult:
    """Run a shell command."""
    import time
    
    try:
        sandbox = get_sandbox()
        start = time.perf_counter()
        
        result = await sandbox.run_command(
            command=command,
            args=args,
            timeout=timeout,
            cwd=cwd,
        )
        
        duration = (time.perf_counter() - start) * 1000
        
        cmd_result = CommandResult(
            success=result.returncode == 0,
            stdout=result.stdout.decode() if result.stdout else "",
            stderr=result.stderr.decode() if result.stderr else "",
            returncode=result.returncode,
            duration_ms=duration,
        )
        
        return ToolResult(success=cmd_result.success, output=cmd_result.model_dump())
        
    except TimeoutError as e:
        return ToolResult(success=False, error=str(e))
    except PermissionError as e:
        return ToolResult(success=False, error=str(e))
    except Exception as e:
        return ToolResult(success=False, error=f"{type(e).__name__}: {e}")