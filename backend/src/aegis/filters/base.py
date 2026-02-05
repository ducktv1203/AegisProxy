"""Base filter interface and common types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FilterAction(Enum):
    """Action to take after filter analysis."""

    PASS = "pass"  # Continue processing
    REDACT = "redact"  # Modify content and continue
    BLOCK = "block"  # Stop processing, reject request


class FindingType(Enum):
    """Type of security finding."""

    PII = "pii"
    INJECTION = "injection"
    CUSTOM = "custom"


@dataclass
class Finding:
    """A security finding detected by a filter."""

    type: FindingType
    entity_type: str  # e.g., "EMAIL_ADDRESS", "JAILBREAK_PATTERN"
    confidence: float  # 0.0 - 1.0
    start: int  # Character position start
    end: int  # Character position end
    filter_name: str
    metadata: dict[str, Any] = field(default_factory=dict)

    # Note: We intentionally do NOT store the actual matched content
    # to prevent sensitive data from appearing in logs


@dataclass
class FilterContext:
    """Context passed through the filter pipeline."""

    request_id: str
    client_info: dict[str, str | None] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FilterResult:
    """Result of a filter's analysis."""

    action: FilterAction
    modified_content: str | None = None
    findings: list[Finding] = field(default_factory=list)
    reason: str | None = None


class BaseFilter(ABC):
    """Abstract base class for security filters."""

    @abstractmethod
    async def analyze(self, content: str, context: FilterContext) -> FilterResult:
        """
        Analyze content and return filter decision.

        Args:
            content: The text content to analyze
            context: Request context information

        Returns:
            FilterResult with action, optional modified content, and findings
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique filter identifier."""
        pass

    @property
    def priority(self) -> int:
        """
        Execution order priority.

        Lower values run earlier. Default is 100.
        """
        return 100

    @property
    def enabled(self) -> bool:
        """Whether the filter is enabled."""
        return True
