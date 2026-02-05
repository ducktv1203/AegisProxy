"""Filter pipeline orchestration."""

from dataclasses import dataclass, field
from typing import Any

from aegis.api.schemas import ChatMessage
from aegis.filters.base import BaseFilter, FilterAction, FilterContext, Finding
from aegis.telemetry.logger import get_logger

logger = get_logger()


@dataclass
class PipelineResult:
    """Result of the complete filter pipeline."""

    blocked: bool = False
    block_reason: str | None = None
    blocking_filter: str | None = None
    processed_messages: list[ChatMessage] = field(default_factory=list)
    all_findings: list[Finding] = field(default_factory=list)


class FilterPipeline:
    """
    Orchestrates the execution of multiple security filters.

    Filters are run in priority order. If any filter returns BLOCK,
    processing stops immediately. REDACT actions accumulate through
    the pipeline.
    """

    def __init__(self, filters: list[BaseFilter] | None = None):
        self._filters: list[BaseFilter] = []
        if filters:
            for f in filters:
                self.register(f)

    def register(self, filter_instance: BaseFilter) -> None:
        """Register a filter and maintain priority order."""
        self._filters.append(filter_instance)
        self._filters.sort(key=lambda f: f.priority)

    async def process(
        self,
        messages: list[ChatMessage],
        request_id: str,
        client_info: dict[str, str | None] | None = None,
    ) -> PipelineResult:
        """
        Process messages through all registered filters.

        Args:
            messages: List of chat messages to analyze
            request_id: Unique request identifier
            client_info: Client metadata for context

        Returns:
            PipelineResult with processed messages and findings
        """
        context = FilterContext(
            request_id=request_id,
            client_info=client_info or {},
        )

        result = PipelineResult()
        processed_messages: list[ChatMessage] = []

        for message in messages:
            if message.content is None:
                processed_messages.append(message)
                continue

            current_content = message.content

            # Run through each filter
            for filter_instance in self._filters:
                if not filter_instance.enabled:
                    continue

                try:
                    filter_result = await filter_instance.analyze(current_content, context)

                    # Collect findings
                    result.all_findings.extend(filter_result.findings)

                    # Handle filter action
                    if filter_result.action == FilterAction.BLOCK:
                        result.blocked = True
                        result.block_reason = filter_result.reason
                        result.blocking_filter = filter_instance.name

                        logger.warning(
                            "filter_blocked_request",
                            request_id=request_id,
                            filter=filter_instance.name,
                            reason=filter_result.reason,
                            finding_count=len(filter_result.findings),
                        )
                        return result

                    elif filter_result.action == FilterAction.REDACT:
                        if filter_result.modified_content:
                            current_content = filter_result.modified_content

                        logger.info(
                            "filter_redacted_content",
                            request_id=request_id,
                            filter=filter_instance.name,
                            finding_count=len(filter_result.findings),
                        )

                except Exception as e:
                    logger.error(
                        "filter_error",
                        request_id=request_id,
                        filter=filter_instance.name,
                        error=str(e),
                    )
                    # Continue with other filters on error
                    continue

            # Add processed message
            processed_messages.append(
                message.model_copy(update={"content": current_content})
            )

        result.processed_messages = processed_messages
        return result


# Singleton instance
_filter_pipeline: FilterPipeline | None = None


def get_filter_pipeline() -> FilterPipeline:
    """Get the singleton filter pipeline instance."""
    global _filter_pipeline
    if _filter_pipeline is None:
        _filter_pipeline = FilterPipeline()
        # Filters will be registered during app initialization
    return _filter_pipeline


def initialize_filters() -> FilterPipeline:
    """Initialize the filter pipeline with all configured filters."""
    from aegis.filters.injection.filter import InjectionFilter
    from aegis.filters.pii.filter import PIIFilter
    from aegis.filters.redaction.filter import RedactionFilter

    pipeline = get_filter_pipeline()

    # Register filters in priority order
    pipeline.register(PIIFilter())  # Priority 10
    pipeline.register(InjectionFilter())  # Priority 20
    pipeline.register(RedactionFilter())  # Priority 100

    logger.info(
        "filter_pipeline_initialized",
        filter_count=len(pipeline._filters),
        filters=[f.name for f in pipeline._filters],
    )

    return pipeline
