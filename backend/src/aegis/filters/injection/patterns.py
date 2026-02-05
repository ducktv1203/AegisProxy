"""Prompt injection detection patterns based on OWASP LLM01:2025."""

import re
from dataclasses import dataclass
from enum import Enum


class PatternCategory(str, Enum):
    """Categories of injection patterns."""

    JAILBREAK = "jailbreak"
    ROLE_OVERRIDE = "role_override"
    SYSTEM_EXTRACTION = "system_extraction"
    DELIMITER_INJECTION = "delimiter_injection"
    ENCODING_EVASION = "encoding_evasion"


@dataclass
class InjectionPattern:
    """A pattern for detecting prompt injection attempts."""

    name: str
    pattern: re.Pattern
    category: PatternCategory
    severity: float  # 0.0 - 1.0
    description: str


# Compiled patterns for prompt injection detection
INJECTION_PATTERNS: list[InjectionPattern] = [
    # === JAILBREAK PATTERNS ===
    InjectionPattern(
        name="ignore_instructions",
        pattern=re.compile(
            r"(?i)ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?|guidelines?)",
            re.IGNORECASE,
        ),
        category=PatternCategory.JAILBREAK,
        severity=0.95,
        description="Attempts to override system instructions",
    ),
    InjectionPattern(
        name="dan_mode",
        pattern=re.compile(
            r"(?i)\b(DAN|do\s+anything\s+now)\b",
            re.IGNORECASE,
        ),
        category=PatternCategory.JAILBREAK,
        severity=0.9,
        description="DAN (Do Anything Now) jailbreak attempt",
    ),
    InjectionPattern(
        name="developer_mode",
        pattern=re.compile(
            r"(?i)(developer|dev|debug|maintenance)\s+mode\s*(enabled?|on|activated?)",
            re.IGNORECASE,
        ),
        category=PatternCategory.JAILBREAK,
        severity=0.85,
        description="Fake developer mode activation",
    ),
    InjectionPattern(
        name="jailbreak_keywords",
        pattern=re.compile(
            r"(?i)\b(jailbreak|bypass\s+filters?|unlock|unrestricted\s+mode|no\s+limits?)\b",
            re.IGNORECASE,
        ),
        category=PatternCategory.JAILBREAK,
        severity=0.85,
        description="Common jailbreak terminology",
    ),
    InjectionPattern(
        name="forget_instructions",
        pattern=re.compile(
            r"(?i)(forget|disregard|discard)\s+(everything|all|your)\s+(you|instructions?|training)",
            re.IGNORECASE,
        ),
        category=PatternCategory.JAILBREAK,
        severity=0.9,
        description="Attempts to reset AI behavior",
    ),

    # === ROLE OVERRIDE PATTERNS ===
    InjectionPattern(
        name="you_are_now",
        pattern=re.compile(
            r"(?i)(you\s+are\s+now|from\s+now\s+on\s+you\s+are|act\s+as\s+if\s+you\s+are)\s+(?!helpful|an?\s+assistant)",
            re.IGNORECASE,
        ),
        category=PatternCategory.ROLE_OVERRIDE,
        severity=0.7,
        description="Role reassignment attempt",
    ),
    InjectionPattern(
        name="pretend_to_be",
        pattern=re.compile(
            r"(?i)(pretend|imagine|roleplay|act)\s+(to\s+be|as|like|you\s+are)\s+(?!helpful)",
            re.IGNORECASE,
        ),
        category=PatternCategory.ROLE_OVERRIDE,
        severity=0.65,
        description="Roleplay-based manipulation",
    ),
    InjectionPattern(
        name="new_persona",
        pattern=re.compile(
            r"(?i)(your\s+new\s+(name|identity|persona|role)\s+is|adopt\s+the\s+persona)",
            re.IGNORECASE,
        ),
        category=PatternCategory.ROLE_OVERRIDE,
        severity=0.8,
        description="Persona injection attempt",
    ),

    # === SYSTEM PROMPT EXTRACTION ===
    InjectionPattern(
        name="repeat_instructions",
        pattern=re.compile(
            r"(?i)(repeat|show|display|reveal|print|output)\s+(your\s+)?(system\s+)?(prompt|instructions?|rules?|guidelines?)",
            re.IGNORECASE,
        ),
        category=PatternCategory.SYSTEM_EXTRACTION,
        severity=0.9,
        description="System prompt extraction attempt",
    ),
    InjectionPattern(
        name="what_are_instructions",
        pattern=re.compile(
            r"(?i)what\s+(are|is)\s+(your\s+)?(initial|original|system|secret)?\s*(instructions?|prompt|rules?|guidelines?)",
            re.IGNORECASE,
        ),
        category=PatternCategory.SYSTEM_EXTRACTION,
        severity=0.85,
        description="System prompt interrogation",
    ),
    InjectionPattern(
        name="verbatim_output",
        pattern=re.compile(
            r"(?i)(print|output|echo|show)\s+(verbatim|exactly|word\s+for\s+word)",
            re.IGNORECASE,
        ),
        category=PatternCategory.SYSTEM_EXTRACTION,
        severity=0.75,
        description="Verbatim output request",
    ),

    # === DELIMITER INJECTION ===
    InjectionPattern(
        name="markdown_delimiter",
        pattern=re.compile(
            r'(?:^|\n)(?:"""|\'\'\').*?(?:ignore|instruction|system|prompt)',
            re.IGNORECASE | re.DOTALL,
        ),
        category=PatternCategory.DELIMITER_INJECTION,
        severity=0.8,
        description="Markdown/code block delimiter injection",
    ),
    InjectionPattern(
        name="xml_injection",
        pattern=re.compile(
            r"<\/?(?:system|instruction|prompt|ignore|override)[^>]*>",
            re.IGNORECASE,
        ),
        category=PatternCategory.DELIMITER_INJECTION,
        severity=0.75,
        description="XML tag injection",
    ),
    InjectionPattern(
        name="separator_injection",
        pattern=re.compile(
            r"(?:^|\n)(?:#{3,}|={3,}|-{3,})\s*(system|instruction|new\s+prompt|override)",
            re.IGNORECASE,
        ),
        category=PatternCategory.DELIMITER_INJECTION,
        severity=0.7,
        description="Separator-based section injection",
    ),

    # === ENCODING EVASION ===
    InjectionPattern(
        name="base64_instruction",
        pattern=re.compile(
            r"(?i)(decode|interpret|execute)\s+(this\s+)?base64",
            re.IGNORECASE,
        ),
        category=PatternCategory.ENCODING_EVASION,
        severity=0.8,
        description="Base64 encoded instruction attempt",
    ),
    InjectionPattern(
        name="unicode_obfuscation",
        pattern=re.compile(
            r"[\u200b\u200c\u200d\ufeff]",  # Zero-width characters
        ),
        category=PatternCategory.ENCODING_EVASION,
        severity=0.6,
        description="Unicode obfuscation detected",
    ),
    InjectionPattern(
        name="leetspeak",
        pattern=re.compile(
            r"1gn0r3|1nstruct10n|syst3m|pr0mpt|byp4ss",
            re.IGNORECASE,
        ),
        category=PatternCategory.ENCODING_EVASION,
        severity=0.5,
        description="Leetspeak obfuscation",
    ),
]


def get_patterns_by_category(category: PatternCategory) -> list[InjectionPattern]:
    """Get all patterns for a specific category."""
    return [p for p in INJECTION_PATTERNS if p.category == category]
