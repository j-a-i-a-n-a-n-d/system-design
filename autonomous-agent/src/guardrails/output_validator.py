"""Output validation guardrail."""

from typing import Any
from pydantic import BaseModel
import re


class ValidationResult(BaseModel):
    """Output validation result."""
    allowed: bool
    reason: str = ""
    risk_level: str = "low"
    sanitized: str = ""


class OutputValidator:
    """Validates LLM output for safety."""
    
    # PII patterns
    PII_PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "phone": r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    }
    
    # Secret patterns
    SECRET_PATTERNS = {
        "api_key": r"(?i)(api[_-]?key|apikey)\s*[:=]\s*[\"']?[a-zA-Z0-9_-]{20,}[\"']?",
        "password": r"(?i)(password|passwd|pwd)\s*[:=]\s*[\"']?[^\s\"']{8,}[\"']?",
        "token": r"(?i)(token|access_token|bearer)\s*[:=]\s*[\"']?[a-zA-Z0-9_-]{20,}[\"']?",
        "private_key": r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----",
        "aws_key": r"(?i)aws[_-]?(access[_-]?key|secret[_-]?key)\s*[:=]\s*[A-Z0-9]{20,}",
        "github_token": r"gh[ps]_[a-zA-Z0-9]{36,}",
    }
    
    # Code safety patterns
    CODE_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"sudo\s+",
        r"chmod\s+777",
        r">\s*/dev/",
        r"curl.*\|\s*sh",
        r"wget.*\|\s*sh",
    ]
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.pii_detection = self.config.get("pii_detection", True)
        self.secrets_detection = self.config.get("secrets_detection", True)
        self.code_safety = self.config.get("code_safety", True)
        self.max_output_length = self.config.get("max_output_length", 100000)
        
        # Compile patterns
        self._pii_regex = {k: re.compile(v) for k, v in self.PII_PATTERNS.items()}
        self._secret_regex = {k: re.compile(v) for k, v in self.SECRET_PATTERNS.items()}
        self._code_regex = [re.compile(p) for p in self.CODE_PATTERNS]
    
    def validate(self, text: str) -> ValidationResult:
        """Validate output text."""
        if not self.enabled:
            return ValidationResult(allowed=True, reason="Validation disabled")
        
        # Check length
        if len(text) > self.max_output_length:
            return ValidationResult(
                allowed=False,
                reason=f"Output too long: {len(text)} > {self.max_output_length}",
                risk_level="medium",
            )
        
        # PII detection
        if self.pii_detection:
            for pii_type, pattern in self._pii_regex.items():
                if pattern.search(text):
                    return ValidationResult(
                        allowed=False,
                        reason=f"PII detected: {pii_type}",
                        risk_level="high",
                    )
        
        # Secrets detection
        if self.secrets_detection:
            for secret_type, pattern in self._secret_regex.items():
                if pattern.search(text):
                    return ValidationResult(
                        allowed=False,
                        reason=f"Secret detected: {secret_type}",
                        risk_level="critical",
                    )
        
        # Code safety
        if self.code_safety:
            for pattern in self._code_regex:
                if pattern.search(text):
                    return ValidationResult(
                        allowed=False,
                        reason=f"Dangerous code pattern detected",
                        risk_level="high",
                    )
        
        return ValidationResult(
            allowed=True,
            reason="Output validation passed",
            risk_level="low",
            sanitized=text,
        )
    
    def sanitize(self, text: str) -> str:
        """Sanitize output text."""
        sanitized = text
        
        # Redact PII
        if self.pii_detection:
            for pii_type, pattern in self._pii_regex.items():
                sanitized = pattern.sub(f"[REDACTED_{pii_type.upper()}]", sanitized)
        
        # Redact secrets
        if self.secrets_detection:
            for secret_type, pattern in self._secret_regex.items():
                sanitized = pattern.sub(f"[REDACTED_{secret_type.upper()}]", sanitized)
        
        return sanitized