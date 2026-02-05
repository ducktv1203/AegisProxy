"""Custom Presidio recognizers for API keys and secrets."""

from presidio_analyzer import Pattern, PatternRecognizer


class APIKeyRecognizer(PatternRecognizer):
    """
    Recognizer for common API key patterns.

    Detects OpenAI, GitHub, AWS, Stripe, and generic API key patterns.
    """

    PATTERNS = [
        # OpenAI API keys
        Pattern(
            "OpenAI API Key",
            r"sk-[a-zA-Z0-9]{48}",
            0.95,
        ),
        # OpenAI Project keys (newer format)
        Pattern(
            "OpenAI Project Key",
            r"sk-proj-[a-zA-Z0-9\-_]{80,}",
            0.95,
        ),
        # GitHub Personal Access Tokens
        Pattern(
            "GitHub PAT",
            r"ghp_[a-zA-Z0-9]{36}",
            0.95,
        ),
        # GitHub OAuth tokens
        Pattern(
            "GitHub OAuth",
            r"gho_[a-zA-Z0-9]{36}",
            0.95,
        ),
        # AWS Access Key ID
        Pattern(
            "AWS Access Key",
            r"AKIA[0-9A-Z]{16}",
            0.9,
        ),
        # Stripe API keys
        Pattern(
            "Stripe Key",
            r"sk_(live|test)_[a-zA-Z0-9]{24,}",
            0.95,
        ),
        Pattern(
            "Stripe Publishable",
            r"pk_(live|test)_[a-zA-Z0-9]{24,}",
            0.85,
        ),
        # Google API keys
        Pattern(
            "Google API Key",
            r"AIza[0-9A-Za-z\-_]{35}",
            0.9,
        ),
        # Slack tokens
        Pattern(
            "Slack Token",
            r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*",
            0.9,
        ),
        # Generic secret patterns (lower confidence)
        Pattern(
            "Generic API Key",
            r"(?i)(?:api[_-]?key|apikey|secret[_-]?key|access[_-]?token)['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9\-_]{20,})['\"]?",
            0.7,
        ),
    ]

    def __init__(self):
        super().__init__(
            supported_entity="API_KEY",
            patterns=self.PATTERNS,
            context=["api", "key", "token", "secret", "credential", "auth"],
        )


class AWSSecretRecognizer(PatternRecognizer):
    """
    Recognizer for AWS Secret Access Keys.

    AWS secrets are 40-character base64 strings, typically near
    AWS-related context words.
    """

    PATTERNS = [
        Pattern(
            "AWS Secret Key",
            r"(?i)(?:aws[_-]?secret[_-]?(?:access[_-]?)?key)['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
            0.9,
        ),
        # Standalone 40-char base64 near AWS context
        Pattern(
            "AWS Secret Standalone",
            r"[A-Za-z0-9/+=]{40}",
            0.5,  # Lower confidence without context
        ),
    ]

    def __init__(self):
        super().__init__(
            supported_entity="AWS_SECRET",
            patterns=self.PATTERNS,
            context=["aws", "amazon", "secret", "credentials", "iam"],
        )


class PrivateKeyRecognizer(PatternRecognizer):
    """Recognizer for private key blocks (PEM format)."""

    PATTERNS = [
        Pattern(
            "Private Key Block",
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----",
            0.99,
        ),
    ]

    def __init__(self):
        super().__init__(
            supported_entity="PRIVATE_KEY",
            patterns=self.PATTERNS,
            context=["key", "private", "pem", "ssh", "rsa"],
        )


# List of all custom recognizers to register
CUSTOM_RECOGNIZERS = [
    APIKeyRecognizer,
    AWSSecretRecognizer,
    PrivateKeyRecognizer,
]
