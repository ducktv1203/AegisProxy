"""Configuration management for AegisProxy using Pydantic Settings."""

from enum import Enum
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    """Logging level options."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LogFormat(str, Enum):
    """Log output format options."""

    JSON = "json"
    CONSOLE = "console"


class RedactionMode(str, Enum):
    """PII redaction strategy options."""

    PLACEHOLDER = "placeholder"  # [EMAIL_1], [SSN_1]
    TYPE_ONLY = "type_only"  # [EMAIL], [SSN]
    MASK = "mask"  # j***@e***.com
    HASH = "hash"  # [REDACTED:a1b2c3]


class InjectionAction(str, Enum):
    """Action to take when prompt injection is detected."""

    BLOCK = "block"
    WARN = "warn"


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    GEMINI = "gemini"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="AEGIS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8080, description="Server port")
    debug: bool = Field(default=False, description="Enable debug mode")

    # LLM Provider Configuration
    default_provider: LLMProvider = Field(
        default=LLMProvider.OPENAI, description="Default LLM provider"
    )
    openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="OPENAI_API_KEY",
        description="OpenAI API key",
    )
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias="OPENAI_BASE_URL",
        description="OpenAI API base URL",
    )
    gemini_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="GEMINI_API_KEY",
        description="Google Gemini API key",
    )

    # Security Settings
    injection_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Injection detection threshold",
    )
    injection_action: InjectionAction = Field(
        default=InjectionAction.BLOCK,
        description="Action when injection detected",
    )
    pii_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="PII detection confidence threshold",
    )
    redaction_mode: RedactionMode = Field(
        default=RedactionMode.PLACEHOLDER,
        description="PII redaction strategy",
    )

    # Logging & Telemetry
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    log_format: LogFormat = Field(
        default=LogFormat.JSON, description="Log format")
    metrics_enabled: bool = Field(
        default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(
        default=9090, description="Prometheus metrics port")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
