"""Presidio analyzer wrapper for PII detection."""

from functools import lru_cache

from presidio_analyzer import AnalyzerEngine, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider

from aegis.config import get_settings
from aegis.filters.pii.recognizers import CUSTOM_RECOGNIZERS


@lru_cache
def get_analyzer() -> AnalyzerEngine:
    """
    Get a cached Presidio analyzer engine instance.

    Initializes the analyzer with SpaCy NLP engine and custom recognizers.
    """
    # Configure NLP engine (SpaCy)
    nlp_config = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
    }

    nlp_engine = NlpEngineProvider(
        nlp_configuration=nlp_config).create_engine()

    # Create analyzer with NLP engine
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine,
                              supported_languages=["en"])

    # Register custom recognizers
    for recognizer_class in CUSTOM_RECOGNIZERS:
        analyzer.registry.add_recognizer(recognizer_class())

    return analyzer


# Default entities to detect
DEFAULT_ENTITIES = [
    # Built-in Presidio entities
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "US_SSN",
    "CREDIT_CARD",
    "IP_ADDRESS",
    "IBAN_CODE",
    "US_PASSPORT",
    "US_DRIVER_LICENSE",
    # Custom entities
    "API_KEY",
    "AWS_SECRET",
    "PRIVATE_KEY",
]


def analyze_text(
    text: str,
    entities: list[str] | None = None,
    language: str = "en",
    score_threshold: float | None = None,
) -> list[RecognizerResult]:
    """
    Analyze text for PII entities.

    Args:
        text: The text to analyze
        entities: List of entity types to detect (default: all)
        language: Language code for analysis
        score_threshold: Minimum confidence score (from settings if not specified)

    Returns:
        List of RecognizerResult objects with detected entities
    """
    analyzer = get_analyzer()
    settings = get_settings()

    threshold = score_threshold if score_threshold is not None else settings.pii_threshold

    results = analyzer.analyze(
        text=text,
        entities=entities or DEFAULT_ENTITIES,
        language=language,
        score_threshold=threshold,
    )

    return results
