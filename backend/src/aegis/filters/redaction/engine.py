"""Presidio Anonymizer wrapper for content redaction."""

from functools import lru_cache

from presidio_analyzer import RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import EngineResult, OperatorConfig

from aegis.config import RedactionMode, get_settings


@lru_cache
def get_anonymizer() -> AnonymizerEngine:
    """Get a cached Presidio anonymizer engine instance."""
    return AnonymizerEngine()


def get_operator_config(
    entity_type: str,
    mode: RedactionMode,
    counter: int = 1,
) -> OperatorConfig:
    """
    Get the operator configuration for a specific entity type and mode.

    Args:
        entity_type: The type of entity (EMAIL_ADDRESS, etc.)
        mode: The redaction mode to use
        counter: Counter for placeholder numbering

    Returns:
        OperatorConfig for the anonymizer
    """
    if mode == RedactionMode.PLACEHOLDER:
        # [EMAIL_1], [SSN_1], etc.
        short_type = entity_type.replace("_ADDRESS", "").replace("US_", "")
        return OperatorConfig("replace", {"new_value": f"[{short_type}_{counter}]"})

    elif mode == RedactionMode.TYPE_ONLY:
        # [EMAIL], [SSN], etc.
        short_type = entity_type.replace("_ADDRESS", "").replace("US_", "")
        return OperatorConfig("replace", {"new_value": f"[{short_type}]"})

    elif mode == RedactionMode.MASK:
        # Partial masking with asterisks
        return OperatorConfig(
            "mask",
            {"chars_to_mask": 8, "masking_char": "*", "from_end": False},
        )

    elif mode == RedactionMode.HASH:
        # Hash-based redaction
        return OperatorConfig("hash", {"hash_type": "sha256"})

    # Default fallback
    return OperatorConfig("replace", {"new_value": "[REDACTED]"})


def redact_text(
    text: str,
    analyzer_results: list[RecognizerResult],
    mode: RedactionMode | None = None,
) -> EngineResult:
    """
    Redact detected entities from text.

    Args:
        text: Original text with PII
        analyzer_results: Results from Presidio analyzer
        mode: Redaction mode (from settings if not specified)

    Returns:
        EngineResult with redacted text and item details
    """
    settings = get_settings()
    redaction_mode = mode or settings.redaction_mode
    anonymizer = get_anonymizer()

    # Build operator configs for each entity type
    # Track counters per entity type for PLACEHOLDER mode
    type_counters: dict[str, int] = {}
    operators: dict[str, OperatorConfig] = {}

    for result in analyzer_results:
        entity_type = result.entity_type

        if entity_type not in type_counters:
            type_counters[entity_type] = 0

        type_counters[entity_type] += 1

        # For non-placeholder modes, we can reuse the same config
        if redaction_mode != RedactionMode.PLACEHOLDER:
            if entity_type not in operators:
                operators[entity_type] = get_operator_config(
                    entity_type, redaction_mode
                )
        else:
            # For placeholder mode, each instance gets a unique number
            operators[entity_type] = get_operator_config(
                entity_type, redaction_mode, type_counters[entity_type]
            )

    # Run anonymization
    result = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators=operators,
    )

    return result
