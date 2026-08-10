"""Filesystem jail for guardrails."""

from typing import Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class JailConfig:
    """Filesystem jail configuration."""
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


class FilesystemJail:
    """Filesystem access control for guardrails."""
    
    def __init__(self, config: JailConfig = None):
        self.config = config or JailConfig()
        self._allowed = [Path(p).expanduser().resolve() for p in self.config.allowed_paths]
        self._denied = [Path(p).expanduser().resolve() for p in self.config.denied_patterns]
    
    def check_path(self, path: str | Path) -> bool:
        """Check if path is allowed."""
        path = Path(path).expanduser().resolve()
        
        # Check denied patterns first
        for denied in self._denied:
            try:
                if path.is_relative_to(denied):
                    return False
            except ValueError:
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
    
    def list_allowed_roots(self) -> list[str]:
        """List allowed root directories."""
        return [str(p) for p in self._allowed]
    
    def list_denied_patterns(self) -> list[str]:
        """List denied patterns."""
        return [str(p) for p in self._denied]