"""Code execution tool."""

from typing import Any
from pydantic import BaseModel
from ..base import tool, ToolResult
from ..sandbox import get_sandbox


class ExecutionResult(BaseModel):
    """Result of code execution."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    duration_ms: float = 0


@tool(
    name="exec_python",
    description="Execute Python code in sandbox",
    parameters={
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code to execute"},
            "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 10},
        },
        "required": ["code"],
    },
)
async def exec_python(code: str, timeout: int = 10) -> ToolResult:
    """Execute Python code."""
    import time
    
    try:
        sandbox = get_sandbox()
        start = time.perf_counter()
        
        result = await sandbox.exec_python(code, timeout=timeout)
        
        duration = (time.perf_counter() - start) * 1000
        
        exec_result = ExecutionResult(
            success=result["success"],
            stdout=result["stdout"],
            stderr=result["stderr"],
            returncode=result["returncode"],
            duration_ms=duration,
        )
        
        return ToolResult(success=exec_result.success, output=exec_result.model_dump())
        
    except TimeoutError as e:
        return ToolResult(success=False, error=str(e))
    except PermissionError as e:
        return ToolResult(success=False, error=str(e))
    except Exception as e:
        return ToolResult(success=False, error=f"{type(e).__name__}: {e}")