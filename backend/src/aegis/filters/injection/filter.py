"""Prompt injection detection filter."""

from dataclasses import dataclass

from aegis.config import InjectionAction, get_settings
from aegis.filters.base import (
    BaseFilter,
    FilterAction,
    FilterContext,
    FilterResult,
    Finding,
    FindingType,
)
from aegis.filters.injection.heuristics import analyze_heuristics
from aegis.filters.injection.patterns import INJECTION_PATTERNS, PatternCategory
from aegis.telemetry.metrics import injection_detections_total


@dataclass
class InjectionAnalysis:
    """Complete injection analysis result."""

    pattern_score: float = 0.0
    heuristic_score: float = 0.0
    matched_patterns: list[str] = None
    highest_severity_pattern: str | None = None

    def __post_init__(self):
        if self.matched_patterns is None:
            self.matched_patterns = []

    @property
    def combined_score(self) -> float:
        """Combined score from patterns and heuristics."""
        # Pattern matches are weighted more heavily
        return self.pattern_score * 0.7 + self.heuristic_score * 0.3


class InjectionFilter(BaseFilter):
    """
    Filter that detects prompt injection attempts.

    Uses a combination of pattern matching and heuristic analysis
    based on OWASP LLM01:2025 (Prompt Injection).
    """

    @property
    def name(self) -> str:
        return "injection_detector"

    @property
    def priority(self) -> int:
        # Run after PII detection
        return 20

    def _analyze_patterns(self, content: str) -> tuple[float, list[str], str | None]:
        """
        Check content against known injection patterns.

        Returns (score, matched_pattern_names, highest_severity_pattern).
        """
        matched = []
        highest_severity = 0.0
        highest_pattern = None

        for pattern in INJECTION_PATTERNS:
            if pattern.pattern.search(content):
                matched.append(pattern.name)

                if pattern.severity > highest_severity:
                    highest_severity = pattern.severity
                    highest_pattern = pattern.name

        # Score is the highest severity found
        return highest_severity, matched, highest_pattern

    async def analyze(self, content: str, context: FilterContext) -> FilterResult:
        """
        Analyze content for prompt injection attempts.

        Returns BLOCK if injection is detected above threshold,
        or PASS otherwise.
        """
        settings = get_settings()

        # Pattern-based detection
        pattern_score, matched_patterns, highest_pattern = self._analyze_patterns(
            content)

        # Heuristic analysis
        heuristics = analyze_heuristics(content)

        # Create analysis result
        analysis = InjectionAnalysis(
            pattern_score=pattern_score,
            heuristic_score=heuristics.combined,
            matched_patterns=matched_patterns,
            highest_severity_pattern=highest_pattern,
        )

        # Check against threshold
        if analysis.combined_score >= settings.injection_threshold:
            # Create finding
            finding = Finding(
                type=FindingType.INJECTION,
                entity_type=highest_pattern or "unknown_injection",
                confidence=analysis.combined_score,
                start=0,
                end=len(content),
                filter_name=self.name,
                metadata={
                    "pattern_score": analysis.pattern_score,
                    "heuristic_score": analysis.heuristic_score,
                    "matched_patterns": matched_patterns,
                },
            )

            # Update metrics
            for pattern_name in matched_patterns:
                injection_detections_total.labels(
                    pattern_type=pattern_name,
                    action=settings.injection_action.value,
                ).inc()

            # Determine action based on settings
            if settings.injection_action == InjectionAction.BLOCK:
                return FilterResult(
                    action=FilterAction.BLOCK,
                    findings=[finding],
                    reason=f"Prompt injection detected: {highest_pattern} (score: {analysis.combined_score:.2f})",
                )
            else:
                # Warn mode - pass but log the finding
                return FilterResult(
                    action=FilterAction.PASS,
                    findings=[finding],
                    reason=f"Injection warning: {highest_pattern} (score: {analysis.combined_score:.2f})",
                )

        return FilterResult(action=FilterAction.PASS)
