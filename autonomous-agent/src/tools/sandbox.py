"""Tool execution sandbox for security."""

from typing import Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import os
import subprocess
import asyncio
import shlex
import tempfile
import signal


@dataclass
class SandboxConfig:
    """Sandbox configuration."""
    # Filesystem
    allowed_paths: list[str] = field(default_factory=lambda: [
        "~/projects",
        "/tmp/agent",
    ])
    denied_patterns: list[str] = field(default_factory=lambda: [
        "~/.ssh",
        "~/.aws",
        "/etc",
        "/root",
        "/home/*/.ssh",
    ])
    max_file_size_mb: int = 10
    allowed_extensions: list[str] = field(default_factory=lambda: [
        ".py", ".txt", ".md", ".json", ".yaml", ".yml",
        ".toml", ".cfg", ".ini", ".sh", ".js", ".ts",
        ".html", ".css", ".sql", ".csv",
    ])
    
    # Command execution
    allowed_commands: dict[str, list[str]] = field(default_factory=lambda: {
        "read": ["cat", "head", "tail", "less", "grep", "rg", "find", "wc", "ls", "tree"],
        "write": ["tee", "echo", "printf", "cat"],
        "list": ["ls", "tree", "find"],
        "git": ["git status", "git diff", "git log", "git show", "git branch"],
        "python": ["python", "python3", "pip", "uv"],
        "test": ["pytest", "python -m pytest", "python -m unittest"],
        "build": ["make", "cargo", "npm", "uv build"],
    })
    denied_patterns_cmd: list[str] = field(default_factory=lambda: [
        "rm\\s+-rf",
        "sudo",
        "chmod\\s+777",
        ">\\s*/dev/",
        "curl.*\\|.*sh",
        "wget.*\\|.*sh",
        "chown",
        "chgrp",
        "mount",
        "umount",
        "dd",
        "mkfs",
    ])
    
    # Resource limits
    default_timeout: int = 30
    max_memory_mb: int = 512
    max_cpu_percent: int = 80


class FilesystemJail:
    """Filesystem access control."""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self._allowed = [Path(p).expanduser().resolve() for p in config.allowed_paths]
        self._denied = [Path(p).expanduser().resolve() for p in config.denied_patterns]
    
    def check_path(self, path: str | Path) -> bool:
        """Check if path is allowed."""
        path = Path(path).expanduser().resolve()
        
        # Check denied patterns first
        for denied in self._denied:
            try:
                if path.is_relative_to(denied):
                    return False
            except ValueError:
                # Not relative, continue
                pass
        
        # Check allowed paths
        for allowed in self._allowed:
            try:
                if path.is_relative_to(allowed):
                    # Check extension
                    if path.suffix and path.suffix not in self.config.allowed_extensions:
                        return False
                    return True
            except ValueError:
                pass
        
        return False
    
    def check_file_size(self, path: str | Path) -> bool:
        """Check if file size is within limit."""
        path = Path(path)
        if not path.exists():
            return True
        size_mb = path.stat().st_size / (1024 * 1024)
        return size_mb <= self.config.max_file_size_mb
    
    def get_safe_path(self, path: str | Path) -> Path:
        """Get resolved path if allowed, otherwise raise."""
        path = Path(path).expanduser()
        if not self.check_path(path):
            raise PermissionError(f"Access denied: {path}")
        if not self.check_file_size(path):
            raise PermissionError(f"File too large: {path}")
        return path.resolve()


class CommandFilter:
    """Command allowlist/denylist filter."""
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self._allowed = config.allowed_commands
        self._denied_patterns = config.denied_patterns_cmd
        self._mode = "allowlist"  # or "denylist"
    
    def check_command(self, command: str) -> bool:
        """Check if command is allowed."""
        import re
        
        # Check denied patterns first
        for pattern in self._denied_patterns:
            if re.search(pattern, command):
                return False
        
        if self._mode == "allowlist":
            # Check if command matches any allowed pattern
            for category, cmds in self._allowed.items():
                for allowed in cmds:
                    if command.startswith(allowed) or command == allowed:
                        return True
            return False
        else:
            # Denylist mode - allow if not denied
            return True
    
    def filter_args(self, command: str, args: list[str]) -> list[str]:
        """Filter command arguments for safety."""
        # Remove potentially dangerous args
        dangerous = {"-rf", "--force", "--recursive", "-R"}
        return [arg for arg in args if arg not in dangerous]


class Sandbox:
    """Execution sandbox combining filesystem and command controls."""
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self.fs_jail = FilesystemJail(self.config)
        self.cmd_filter = CommandFilter(self.config)
    
    async def run_command(
        self,
        command: str,
        args: list[str] = None,
        timeout: int = None,
        cwd: str = None,
        env: dict = None,
    ) -> subprocess.CompletedProcess:
        """Run a command in sandbox."""
        full_cmd = command
        if args:
            full_cmd += " " + " ".join(shlex.quote(arg) for arg in args)
        
        # Check command
        if not self.cmd_filter.check_command(full_cmd):
            raise PermissionError(f"Command not allowed: {full_cmd}")
        
        # Filter args
        if args:
            args = self.cmd_filter.filter_args(command, args)
        
        # Check working directory
        if cwd:
            cwd = str(self.fs_jail.get_safe_path(cwd))
        
        # Prepare environment
        safe_env = os.environ.copy()
        if env:
            safe_env.update(env)
        
        # Run command
        timeout = timeout or self.config.default_timeout
        
        try:
            process = await asyncio.create_subprocess_exec(
                command,
                *args,
                cwd=cwd,
                env=safe_env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Command timed out after {timeout}s")
            
            return subprocess.CompletedProcess(
                args=[command] + (args or []),
                returncode=process.returncode,
                stdout=stdout,
                stderr=stderr,
            )
            
        except FileNotFoundError:
            raise PermissionError(f"Command not found: {command}")
    
    def read_file(self, path: str | Path) -> str:
        """Read file with sandbox checks."""
        safe_path = self.fs_jail.get_safe_path(path)
        with open(safe_path, "r") as f:
            return f.read()
    
    def write_file(self, path: str | Path, content: str) -> None:
        """Write file with sandbox checks."""
        safe_path = self.fs_jail.get_safe_path(path)
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        with open(safe_path, "w") as f:
            f.write(content)
    
    def list_dir(self, path: str | Path) -> list[str]:
        """List directory with sandbox checks."""
        safe_path = self.fs_jail.get_safe_path(path)
        return [str(p.relative_to(safe_path)) for p in safe_path.iterdir()]
    
    async def exec_python(
        self,
        code: str,
        timeout: int = None,
        allowed_imports: list[str] = None,
    ) -> Any:
        """Execute Python code in sandbox."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            # Check if file is in allowed path
            self.fs_jail.get_safe_path(temp_path)
            
            # Run with restricted environment
            result = await self.run_command(
                "python3",
                [temp_path],
                timeout=timeout or 10,
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.decode() if result.stdout else "",
                "stderr": result.stderr.decode() if result.stderr else "",
                "returncode": result.returncode,
            }
            
        finally:
            # Cleanup
            try:
                os.unlink(temp_path)
            except OSError:
                pass


# Global sandbox
_global_sandbox: Optional[Sandbox] = None


def get_sandbox() -> Sandbox:
    """Get global sandbox instance."""
    global _global_sandbox
    if _global_sandbox is None:
        _global_sandbox = Sandbox()
    return _global_sandbox