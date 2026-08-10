"""Audit logging for guardrails."""

from typing import Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel
import time
import json
import uuid
from pathlib import Path


class AuditEvent(BaseModel):
    """Audit event."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    event_type: str  # tool_call, validation, error, security
    session_id: str
    user_id: str = "unknown"
    details: dict = field(default_factory=dict)
    success: bool = True
    error: str = ""


class AuditLogger:
    """Audit logger for security events."""
    
    def __init__(
        self,
        log_file: str = "~/.agent/audit.log",
        max_file_size_mb: int = 100,
        retention_days: int = 30,
    ):
        self.log_file = Path(log_file).expanduser()
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.max_file_size_mb = max_file_size_mb
        self.retention_days = retention_days
    
    def log(
        self,
        event_type: str,
        session_id: str,
        details: dict,
        success: bool = True,
        error: str = "",
        user_id: str = "unknown",
    ) -> AuditEvent:
        """Log an audit event."""
        event = AuditEvent(
            event_type=event_type,
            session_id=session_id,
            details=details,
            success=success,
            error=error,
            user_id=user_id,
        )
        
        # Write to file
        self._write_event(event)
        
        return event
    
    def _write_event(self, event: AuditEvent) -> None:
        """Write event to log file."""
        try:
            # Check rotation
            if self.log_file.exists():
                size_mb = self.log_file.stat().st_size / (1024 * 1024)
                if size_mb > self.max_file_size_mb:
                    self._rotate()
            
            # Append event
            with open(self.log_file, "a") as f:
                f.write(event.model_dump_json() + "\n")
        except Exception:
            # Fail silently - audit logging should never break the app
            pass
    
    def _rotate(self) -> None:
        """Rotate log file."""
        import shutil
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        rotated = self.log_file.with_name(f"{self.log_file.stem}_{timestamp}.log")
        shutil.move(str(self.log_file), str(rotated))
        
        # Clean old files
        self._cleanup_old()
    
    def _cleanup_old(self) -> None:
        """Remove old log files."""
        cutoff = time.time() - (self.retention_days * 86400)
        for log_file in self.log_file.parent.glob(f"{self.log_file.stem}_*.log"):
            try:
                mtime = log_file.stat().st_mtime
                if mtime < cutoff:
                    log_file.unlink()
            except Exception:
                pass
    
    def query(
        self,
        session_id: str = None,
        event_type: str = None,
        start_time: float = None,
        end_time: float = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query audit events."""
        events = []
        
        if not self.log_file.exists():
            return events
        
        with open(self.log_file, "r") as f:
            for line in f:
                if len(events) >= limit:
                    break
                try:
                    event = AuditEvent.model_validate_json(line)
                    
                    if session_id and event.session_id != session_id:
                        continue
                    if event_type and event.event_type != event_type:
                        continue
                    if start_time and event.timestamp < start_time:
                        continue
                    if end_time and event.timestamp > end_time:
                        continue
                    
                    events.append(event)
                except Exception:
                    continue
        
        return events
    
    def get_stats(self) -> dict:
        """Get audit log statistics."""
        if not self.log_file.exists():
            return {"events": 0, "file_size_mb": 0}
        
        count = 0
        event_types = {}
        
        with open(self.log_file, "r") as f:
            for line in f:
                count += 1
                try:
                    event = AuditEvent.model_validate_json(line)
                    event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
                except Exception:
                    pass
        
        size_mb = self.log_file.stat().st_size / (1024 * 1024)
        
        return {
            "events": count,
            "file_size_mb": round(size_mb, 2),
            "event_types": event_types,
        }