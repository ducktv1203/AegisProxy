"""PII detection filter implementation."""

from aegis.filters.base import (
    BaseFilter,
    FilterAction,
    FilterContext,
    FilterResult,
    Finding,
    FindingType,
)
from aegis.filters.pii.analyzer import analyze_text
from aegis.telemetry.metrics import pii_detections_total


class PIIFilter(BaseFilter):
    """
    Filter that detects PII in content using Microsoft Presidio.

    This filter analyzes text for personally identifiable information
    and flags content for redaction. It does NOT perform the actual
    redaction - that's handled by the RedactionFilter.
    """

    @property
    def name(self) -> str:
        return "pii_detector"

    @property
    def priority(self) -> int:
        # Run early to detect PII before other filters
        return 10

    async def analyze(self, content: str, context: FilterContext) -> FilterResult:
        """
        Analyze content for PII entities.

        Returns REDACT action if PII is found, with findings attached.
        The actual redaction is performed by a later filter.
        """
        # Run Presidio analysis
        results = analyze_text(content)

        if not results:
            return FilterResult(action=FilterAction.PASS)

        # Convert to findings
        findings: list[Finding] = []
        for result in results:
            findings.append(
                Finding(
                    type=FindingType.PII,
                    entity_type=result.entity_type,
                    confidence=result.score,
                    start=result.start,
                    end=result.end,
                    filter_name=self.name,
                    metadata={
                        "recognition_metadata": result.recognition_metadata,
                    },
                )
            )

            # Update metrics
            pii_detections_total.labels(entity_type=result.entity_type).inc()

        # Store findings in context for redaction filter
        if "pii_findings" not in context.metadata:
            context.metadata["pii_findings"] = []
        context.metadata["pii_findings"].extend(findings)

        return FilterResult(
            action=FilterAction.REDACT,
            findings=findings,
            reason=f"Detected {len(findings)} PII entities",
        )
