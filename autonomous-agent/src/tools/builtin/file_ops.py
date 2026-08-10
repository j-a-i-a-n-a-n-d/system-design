"""File operation tools."""

from typing import Any
from pathlib import Path
from ..base import tool, ToolResult
from ..sandbox import get_sandbox


@tool(
    name="read_file",
    description="Read contents of a file",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to file"},
            "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"},
        },
        "required": ["path"],
    },
)
async def read_file(path: str, encoding: str = "utf-8") -> ToolResult:
    """Read a file."""
    try:
        sandbox = get_sandbox()
        content = sandbox.read_file(path)
        return ToolResult(success=True, output=content)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


@tool(
    name="write_file",
    description="Write content to a file",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to file"},
            "content": {"type": "string", "description": "Content to write"},
            "encoding": {"type": "string", "description": "File encoding", "default": "utf-8"},
        },
        "required": ["path", "content"],
    },
)
async def write_file(path: str, content: str, encoding: str = "utf-8") -> ToolResult:
    """Write to a file."""
    try:
        sandbox = get_sandbox()
        sandbox.write_file(path, content)
        return ToolResult(success=True, output=f"Written {len(content)} bytes to {path}")
    except Exception as e:
        return ToolResult(success=False, error=str(e))


@tool(
    name="list_dir",
    description="List contents of a directory",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path to directory"},
        },
        "required": ["path"],
    },
)
async def list_dir(path: str) -> ToolResult:
    """List directory contents."""
    try:
        sandbox = get_sandbox()
        entries = sandbox.list_dir(path)
        return ToolResult(success=True, output=entries)
    except Exception as e:
        return ToolResult(success=False, error=str(e))


@tool(
    name="glob_search",
    description="Search for files matching a glob pattern",
    parameters={
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "Glob pattern"},
            "root": {"type": "string", "description": "Root directory", "default": "."},
        },
        "required": ["pattern"],
    },
)
async def glob_search(pattern: str, root: str = ".") -> ToolResult:
    """Search files by glob pattern."""
    try:
        sandbox = get_sandbox()
        root_path = sandbox.fs_jail.get_safe_path(root)
        
        matches = list(root_path.rglob(pattern))
        relative_matches = [str(p.relative_to(root_path)) for p in matches]
        
        return ToolResult(success=True, output=relative_matches)
    except Exception as e:
        return ToolResult(success=False, error=str(e))