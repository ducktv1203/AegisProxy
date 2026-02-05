"""Security event definitions for telemetry."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal


@dataclass
class SecurityEvent:
    """
    A security event for logging and telemetry.

    IMPORTANT: This class intentionally does NOT include any fields
    for storing sensitive content. Only metadata is logged.
    """

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    request_id: str = ""
    event_type: Literal[
        "PII_DETECTED",
        "INJECTION_BLOCKED",
        "INJECTION_WARNED",
        "REQUEST_ALLOWED",
        "REQUEST_BLOCKED",
    ] = "REQUEST_ALLOWED"

    # What was found (NO actual content)
    entity_type: str | None = None
    entity_count: int = 0
    confidence_score: float = 0.0

    # What action was taken
    action: Literal["REDACTED", "BLOCKED", "WARNED", "ALLOWED"] = "ALLOWED"

    # Context (safe metadata only)
    client_ip: str | None = None
    user_agent: str | None = None
    model_requested: str | None = None

    # Position info (for debugging, NO content)
    char_start: int | None = None
    char_end: int | None = None

    def to_log_dict(self) -> dict:
        """Convert to a dictionary safe for logging."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id,
            "event_type": self.event_type,
            "entity_type": self.entity_type,
            "entity_count": self.entity_count,
            "confidence_score": self.confidence_score,
            "action": self.action,
            "client_ip": self.client_ip,
            "user_agent": self.user_agent,
            "model_requested": self.model_requested,
        }
