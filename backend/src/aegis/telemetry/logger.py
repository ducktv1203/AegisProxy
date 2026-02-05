"""Structured logging using structlog."""

import sys
from functools import lru_cache

import structlog

from aegis.config import LogFormat, get_settings


def configure_logging() -> None:
    """Configure structlog with appropriate processors."""
    settings = get_settings()

    # Common processors for all formats
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.log_format == LogFormat.JSON:
        # JSON output for production
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console output for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            # Default to INFO if invalid level
            20  # logging.INFO
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


@lru_cache
def get_logger() -> structlog.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger("aegis")


# Convenience function to log security events
def log_security_event(
    event_type: str,
    request_id: str,
    **kwargs,
) -> None:
    """
    Log a security event with structured data.

    This is the primary interface for logging security-related events.
    Sensitive data should NEVER be passed to this function.
    """
    logger = get_logger()
    logger.info(
        "security_event",
        event_type=event_type,
        request_id=request_id,
        **kwargs,
    )
