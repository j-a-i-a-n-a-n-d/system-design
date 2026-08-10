"""Search tools."""

from typing import Any
from pydantic import BaseModel
from ..base import tool, ToolResult
from ..sandbox import get_sandbox


class GrepMatch(BaseModel):
    """A grep match result."""
    file: str
    line_number: int
    line: str
    match: str


@tool(
    name="grep_search",
    description="Search for pattern in files using ripgrep",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Search pattern (regex)"},
            "path": {"type": "string", "description": "Path to search", "default": "."},
            "file_pattern": {"type": "string", "description": "File pattern to include"},
            "max_results": {"type": "integer", "description": "Maximum results", "default": 100},
        },
        "required": ["pattern"],
    },
)
async def grep_search(
    pattern: str,
    path: str = ".",
    file_pattern: str = None,
    max_results: int = 100,
) -> ToolResult:
    """Search for pattern in files."""
    import subprocess
    import shlex
    
    try:
        sandbox = get_sandbox()
        safe_path = sandbox.fs_jail.get_safe_path(path)
        
        # Build rg command
        cmd = ["rg", "--json", "--max-count", str(max_results)]
        
        if file_pattern:
            cmd.extend(["-g", file_pattern])
        
        cmd.append(pattern)
        cmd.append(str(safe_path))
        
        # Execute
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        
        matches = []
        if stdout:
            for line in stdout.decode().strip().split("\n"):
                if line:
                    import json
                    data = json.loads(line)
                    if data.get("type") == "match":
                        match_data = data["data"]
                        matches.append(GrepMatch(
                            file=match_data["path"]["text"],
                            line_number=match_data["line_number"],
                            line=match_data["lines"]["text"],
                            match=pattern,
                        ))
        
        return ToolResult(success=True, output=[m.model_dump() for m in matches])
        
    except FileNotFoundError:
        return ToolResult(success=False, error="ripgrep (rg) not installed")
    except Exception as e:
        return ToolResult(success=False, error=str(e))

import asyncio