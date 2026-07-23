"""Input validation and prompt-injection guards."""

from __future__ import annotations

import re

from app.core.exceptions import ValidationError

# Patterns that indicate likely prompt injection attempts
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(your\s+)?instructions",
    r"you\s+are\s+now\s+a?n?\s+(?:different|new|evil|jailbroken)",
    r"pretend\s+you\s+(?:have\s+no|don't\s+have)",
    r"<\s*system\s*>",
    r"\[INST\]",
    r"###\s*instruction",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

MAX_MESSAGE_LENGTH = 32_000


def sanitize_user_input(message: str) -> str:
    """Remove null bytes and validate length. Raise ValidationError on injection."""
    message = message.replace("\x00", "")

    if len(message) > MAX_MESSAGE_LENGTH:
        raise ValidationError(
            f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters."
        )

    for pattern in _COMPILED:
        if pattern.search(message):
            raise ValidationError(
                "Message contains disallowed content. "
                "Do not attempt to override system instructions."
            )

    return message


def validate_filename(filename: str) -> str:
    """Strip path traversal and non-safe characters from a filename."""
    # Remove path components
    name = filename.replace("\\", "/").split("/")[-1]
    # Allow only safe characters
    safe = re.sub(r"[^\w.\-]", "_", name)
    if not safe or safe.startswith("."):
        raise ValidationError(f"Invalid filename: {filename!r}")
    return safe
