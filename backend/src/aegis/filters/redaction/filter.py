"""Redaction filter implementation."""

from aegis.filters.base import BaseFilter, FilterAction, FilterContext, FilterResult
from aegis.filters.redaction.engine import redact_text
from aegis.telemetry.logger import get_logger

logger = get_logger()


class RedactionFilter(BaseFilter):
    """
    Filter that redacts sensitive information based on previous PII findings.

    This filter typically runs last in the pipeline (or after PII detection)
    to sanitize the content before it is sent to the LLM.
    """

    def __init__(self, name: str = "redaction_filter"):
        """Initialize the redaction filter."""
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def analyze(self, content: str, context: FilterContext) -> FilterResult:
        """
        Redact PII from the content using findings in the context.

        Args:
            content: The text content to analyze/redact.
            context: The filter context containing findings from previous filters.

        Returns:
            FilterResult: The result containing the redacted content.
        """
        # If no findings to redact, pass through
        if not context.metadata.get("pii_findings") and not context.findings:
            return FilterResult(action=FilterAction.PASS)

        # Collect recognizer results from findings
        # We assume previous filters (like PIIFilter) have populated findings
        # compatible with Presidio's RecognizerResult (or we convert them)
        # For simplicity in this integration, we rely on the PIIFilter to have
        # possibly stored raw Presidio results or we reconstruct them.

        # In this implementation, we will use the 'findings' in the context
        # to drive redaction.

        # Check if we have findings to act upon from metadata
        findings = context.metadata.get("pii_findings", [])
        if not findings:
            return FilterResult(action=FilterAction.PASS)

        try:
            # Perform redaction
            # We need to map our 'Finding' objects back to what the engine expects
            # or update the engine to accept our findings.
            # For now, let's assume valid Presidio-compatible results are needed,
            # but since we are using a custom engine wrapper, let's look at `redact_text`.

            # Actually, the PII filter likely added findings.
            # Let's perform the redaction using the engine.
            # We need to convert context.findings to the format expected by redact_text

            # Import here to avoid circular dependency
            from presidio_analyzer import RecognizerResult

            analyzer_results = []
            for finding in findings:
                if finding.filter_name == "pii_detector":  # Only redact PII findings
                    analyzer_results.append(RecognizerResult(
                        entity_type=finding.entity_type,
                        start=finding.start,
                        end=finding.end,
                        score=finding.confidence
                    ))

            if not analyzer_results:
                return FilterResult(action=FilterAction.PASS)

            redaction_result = redact_text(content, analyzer_results)

            logger.info(
                "content_redacted",
                original_length=len(content),
                redacted_length=len(redaction_result.text),
                items_redacted=len(redaction_result.items),
            )

            return FilterResult(
                action=FilterAction.REDACT,
                modified_content=redaction_result.text,
                reason=f"Redacted {len(redaction_result.items)} items",
            )

        except Exception as e:
            logger.error("redaction_error", error=str(e))
            # In case of error, deciding whether to BLOCK or PASS is critical.
            # To be safe (fail-closed), we should probably BLOCK if redaction fails.
            return FilterResult(
                action=FilterAction.BLOCK,
                reason="Redaction failed due to internal error",
            )
