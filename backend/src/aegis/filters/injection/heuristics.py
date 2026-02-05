"""Heuristic scoring for prompt injection detection."""

import re
from dataclasses import dataclass


@dataclass
class HeuristicScore:
    """Scores from heuristic analysis."""

    instruction_density: float = 0.0  # How "instructional" the text is
    delimiter_score: float = 0.0  # Presence of suspicious delimiters
    urgency_score: float = 0.0  # Urgency/manipulation language
    context_switch_score: float = 0.0  # Attempts to change context

    @property
    def combined(self) -> float:
        """Weighted combination of all heuristic scores."""
        return (
            self.instruction_density * 0.35
            + self.delimiter_score * 0.25
            + self.urgency_score * 0.2
            + self.context_switch_score * 0.2
        )


# Instructional keywords and phrases
INSTRUCTION_KEYWORDS = [
    "you must", "you should", "you will", "always", "never",
    "do not", "don't", "must not", "respond with", "reply with",
    "output", "generate", "create", "write", "say",
    "ignore", "forget", "disregard", "override", "bypass",
    "from now on", "going forward", "starting now",
]

# Urgent/manipulative language
URGENCY_PHRASES = [
    "important", "urgent", "critical", "immediately",
    "this is a test", "this is just", "trust me",
    "as an ai", "as a language model",
    "hypothetically", "in theory", "for research",
]

# Suspicious delimiters
DELIMITER_PATTERNS = [
    r'"""',  # Triple quotes
    r"'''",  # Triple single quotes
    r"```",  # Code blocks
    r"###",  # Markdown headers
    r"---",  # Horizontal rules
    r"===",  # Emphasis separators
    r"\[INST\]",  # Instruction tags
    r"\[/INST\]",
    r"<<SYS>>",  # System tags
    r"<</SYS>>",
]

# Context switch indicators
CONTEXT_SWITCHES = [
    r"new\s+conversation",
    r"start\s+over",
    r"reset\s+context",
    r"previous\s+conversation",
    r"ignore\s+(?:the\s+)?above",
    r"actual\s+(?:prompt|instruction)",
    r"real\s+(?:task|request)",
]


def calculate_instruction_density(text: str) -> float:
    """
    Calculate how "instructional" the text appears.

    Returns a score from 0.0 to 1.0.
    """
    text_lower = text.lower()
    word_count = len(text.split())

    if word_count == 0:
        return 0.0

    matches = sum(1 for kw in INSTRUCTION_KEYWORDS if kw in text_lower)

    # Normalize by text length
    density = min(matches / (word_count / 10), 1.0)
    return density


def calculate_delimiter_score(text: str) -> float:
    """
    Calculate the presence of suspicious delimiters.

    Returns a score from 0.0 to 1.0.
    """
    score = 0.0
    for pattern in DELIMITER_PATTERNS:
        if re.search(pattern, text):
            score += 0.15  # Each delimiter adds to the score

    return min(score, 1.0)


def calculate_urgency_score(text: str) -> float:
    """
    Calculate the presence of urgent/manipulative language.

    Returns a score from 0.0 to 1.0.
    """
    text_lower = text.lower()
    matches = sum(1 for phrase in URGENCY_PHRASES if phrase in text_lower)

    return min(matches * 0.15, 1.0)


def calculate_context_switch_score(text: str) -> float:
    """
    Calculate attempts to switch or reset context.

    Returns a score from 0.0 to 1.0.
    """
    score = 0.0
    text_lower = text.lower()

    for pattern in CONTEXT_SWITCHES:
        if re.search(pattern, text_lower):
            score += 0.25

    return min(score, 1.0)


def analyze_heuristics(text: str) -> HeuristicScore:
    """
    Perform complete heuristic analysis on text.

    Returns a HeuristicScore with all component scores.
    """
    return HeuristicScore(
        instruction_density=calculate_instruction_density(text),
        delimiter_score=calculate_delimiter_score(text),
        urgency_score=calculate_urgency_score(text),
        context_switch_score=calculate_context_switch_score(text),
    )
