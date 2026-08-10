"""Command filter for guardrails."""

from typing import Any
from dataclasses import dataclass, field
import re


@dataclass
class FilterConfig:
    """Command filter configuration."""
    mode: str = "allowlist"  # "allowlist" or "denylist"
    allowed_commands: dict[str, list[str]] = field(default_factory=lambda: {
        "read": ["cat", "head", "tail", "less", "grep", "rg", "find", "wc", "ls", "tree"],
        "write": ["tee", "echo", "printf", "cat"],
        "list": ["ls", "tree", "find"],
        "git": ["git status", "git diff", "git log", "git show", "git branch"],
        "python": ["python", "python3", "pip", "uv"],
        "test": ["pytest", "python -m pytest", "python -m unittest"],
        "build": ["make", "cargo", "npm", "uv build"],
    })
    denied_patterns: list[str] = field(default_factory=lambda: [
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


class CommandFilter:
    """Command allowlist/denylist filter."""
    
    def __init__(self, config: FilterConfig = None):
        self.config = config or FilterConfig()
        self._allowed = self.config.allowed_commands
        self._denied_patterns = [re.compile(p) for p in self.config.denied_patterns]
        self._mode = self.config.mode
    
    def check_command(self, command: str) -> bool:
        """Check if command is allowed."""
        # Check denied patterns first
        for pattern in self._denied_patterns:
            if pattern.search(command):
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
        dangerous = {"-rf", "--force", "--recursive", "-R", "--no-preserve-root"}
        return [arg for arg in args if arg not in dangerous]
    
    def get_allowed_commands(self) -> dict[str, list[str]]:
        """Get allowed commands by category."""
        return self._allowed.copy()
    
    def add_allowed(self, category: str, command: str) -> None:
        """Add command to allowlist."""
        if category not in self._allowed:
            self._allowed[category] = []
        if command not in self._allowed[category]:
            self._allowed[category].append(command)
    
    def remove_allowed(self, category: str, command: str) -> bool:
        """Remove command from allowlist."""
        if category in self._allowed and command in self._allowed[category]:
            self._allowed[category].remove(command)
            return True
        return False