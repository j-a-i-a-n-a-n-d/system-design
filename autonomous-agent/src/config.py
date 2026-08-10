"""Configuration management."""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Agent configuration."""
    max_steps: int = Field(default=20, ge=1, le=100)
    max_retries: int = Field(default=3, ge=0, le=10)
    default_timeout: int = Field(default=30, ge=1, le=300)
    working_dir: str = Field(default="~/.agent/workspace")
    system_prompt: str = Field(default="")

    model_config = SettingsConfigDict(env_prefix="AGENT_")


class GatewaySettings(BaseSettings):
    """Gateway configuration."""
    primary: str = Field(default="openai")
    fallback: str = Field(default="anthropic")
    timeout: int = Field(default=60, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    models: dict[str, str] = Field(default_factory=lambda: {
        "planner": "gpt-4o-mini",
        "executor": "gpt-4o",
        "observer": "gpt-4o-mini",
        "judge": "claude-3.5-sonnet",
    })
    routing: dict[str, str] = Field(default_factory=lambda: {
        "simple_tasks": "gpt-4o-mini",
        "complex_tasks": "gpt-4o",
        "code_tasks": "claude-3.5-sonnet",
    })
    fallback_models: list[str] = Field(default_factory=lambda: [
        "gpt-4o-mini",
        "claude-3.5-haiku",
    ])

    model_config = SettingsConfigDict(env_prefix="GATEWAY_")


class GuardrailsSettings(BaseSettings):
    """Guardrails configuration."""
    rate_limits: dict[str, int] = Field(default_factory=lambda: {
        "requests_per_minute": 60,
        "tokens_per_minute": 100000,
        "cost_per_hour_usd": 10,
    })
    fs_jail: dict[str, list[str]] = Field(default_factory=lambda: {
        "allowed_paths": ["~/projects", "/tmp/agent"],
        "denied_patterns": ["~/.ssh", "~/.aws", "/etc", "/root"],
    })
    command_filter: dict = Field(default_factory=lambda: {
        "mode": "allowlist",
        "allowed_commands": {
            "read": ["cat", "head", "tail", "less", "grep", "rg", "find", "wc", "ls", "tree"],
            "write": ["tee", "echo", "printf", "cat"],
            "list": ["ls", "tree", "find"],
            "git": ["git status", "git diff", "git log", "git show", "git branch"],
            "python": ["python", "python3", "pip", "uv"],
            "test": ["pytest", "python -m pytest", "python -m unittest"],
            "build": ["make", "cargo", "npm", "uv build"],
        },
        "denied_patterns": [
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
        ],
    })
    pii_detection: bool = True
    secrets_detection: bool = True
    max_output_length: int = 100000

    model_config = SettingsConfigDict(env_prefix="GUARDRAILS_")


class ObservabilitySettings(BaseSettings):
    """Observability configuration."""
    tracing_enabled: bool = True
    tracing_endpoint: str = "http://localhost:4317"
    service_name: str = "autonomous-agent"
    sample_rate: float = 1.0
    logging_level: str = "INFO"
    logging_format: str = "json"
    logging_output: str = "stdout"
    cost_tracking: bool = True
    metrics_port: int = 9090

    model_config = SettingsConfigDict(env_prefix="OBS_")


class MCPSettings(BaseSettings):
    """MCP configuration."""
    enabled: bool = False
    transport: str = "stdio"
    host: str = "localhost"
    port: int = 8000
    auth_enabled: bool = False
    auth_type: str = "none"

    model_config = SettingsConfigDict(env_prefix="MCP_")


class WorkspaceSettings(BaseSettings):
    """Workspace configuration."""
    root: str = "~/.agent/workspace"
    temp_dir: str = "/tmp/agent"
    max_file_size_mb: int = 10
    allowed_extensions: list[str] = Field(default_factory=lambda: [
        ".py", ".txt", ".md", ".json", ".yaml", ".yml",
        ".toml", ".cfg", ".ini", ".sh", ".js", ".ts",
        ".html", ".css", ".sql", ".csv",
    ])

    model_config = SettingsConfigDict(env_prefix="WORKSPACE_")


class Settings(BaseSettings):
    """Main settings container."""
    agent: AgentSettings = Field(default_factory=AgentSettings)
    gateway: GatewaySettings = Field(default_factory=GatewaySettings)
    guardrails: GuardrailsSettings = Field(default_factory=GuardrailsSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    mcp: MCPSettings = Field(default_factory=MCPSettings)
    workspace: WorkspaceSettings = Field(default_factory=WorkspaceSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def load_settings_from_yaml(path: str | Path) -> Settings:
    """Load settings from YAML file."""
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f)
    return Settings(**data)


def reload_settings(path: Optional[str | Path] = None) -> Settings:
    """Reload settings from file or environment."""
    global _settings
    if path:
        _settings = load_settings_from_yaml(path)
    else:
        _settings = Settings()
    return _settings