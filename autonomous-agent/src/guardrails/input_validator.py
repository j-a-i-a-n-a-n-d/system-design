"""Input validation guardrail."""

from typing import Any
from pydantic import BaseModel
import re


class ValidationResult(BaseModel):
    """Input validation result."""
    allowed: bool
    reason: str = ""
    risk_level: str = "low"  # low, medium, high, critical
    sanitized: str = ""


class InputValidator:
    """Validates user input for safety."""
    
    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"forget\s+everything",
        r"system\s+prompt",
        r"you\s+are\s+now",
        r"pretend\s+to\s+be",
        r"act\s+as\s+if",
        r"roleplay",
        r"simulate",
        r"bypass",
        r"override",
        r"disable\s+safety",
        r"ignore\s+safety",
        r"no\s+rules",
        r"unrestricted",
        r"developer\s+mode",
        r"admin\s+mode",
        r"<\|.*?\|>",  # Special tokens
        r"\[INST\].*?\[/INST\]",  # Instruction tokens
    ]
    
    # Suspicious patterns
    SUSPICIOUS_PATTERNS = [
        r"password\s*[:=]",
        r"api\s*key\s*[:=]",
        r"secret\s*[:=]",
        r"token\s*[:=]",
        r"private\s*key",
        r"ssh\s*key",
        r"aws\s*access",
        r"aws\s*secret",
    ]
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.strict_mode = self.config.get("strict_mode", False)
        
        # Compile patterns
        self._injection_regex = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self._suspicious_regex = [re.compile(p, re.IGNORECASE) for p in self.SUSPICIOUS_PATTERNS]
    
    def validate(self, text: str) -> ValidationResult:
        """Validate input text."""
        if not self.enabled:
            return ValidationResult(allowed=True, reason="Validation disabled")
        
        # Check for injection attempts
        for pattern in self._injection_regex:
            if pattern.search(text):
                return ValidationResult(
                    allowed=False,
                    reason=f"Potential prompt injection detected: {pattern.pattern}",
                    risk_level="critical",
                )
        
        # Check for suspicious content
        for pattern in self._suspicious_regex:
            if pattern.search(text):
                return ValidationResult(
                    allowed=self.strict_mode is False,
                    reason=f"Suspicious content detected: {pattern.pattern}",
                    risk_level="high",
                )
        
        # Check length
        max_len = self.config.get("max_length", 100000)
        if len(text) > max_len:
            return ValidationResult(
                allowed=False,
                reason=f"Input too long: {len(text)} > {max_len}",
                risk_level="medium",
            )
        
        return ValidationResult(
            allowed=True,
            reason="Input validation passed",
            risk_level="low",
            sanitized=text,
        )
    
    def sanitize(self, text: str) -> str:
        """Sanitize input text."""
        # Remove potential injection attempts
        sanitized = text
        for pattern in self._injection_regex:
            sanitized = pattern.sub("[REDACTED]", sanitized)
        return sanitized