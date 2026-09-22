import re

REFUSAL_RESPONSE = (
    "I can't follow requests that try to change my instructions or reveal the system prompt."
)

_PATTERNS = [
    re.compile(
        r"ignore\s+(?:all\s+|any\s+)?(?:previous|prior|above)\s+instructions",
        re.IGNORECASE,
    ),
    re.compile(
        r"disregard\s+(?:all\s+|any\s+)?(?:previous|prior|your)\s+instructions",
        re.IGNORECASE,
    ),
    re.compile(
        r"reveal\s+(?:your\s+|the\s+)?(?:system\s+)?prompt",
        re.IGNORECASE,
    ),
    re.compile(r"you\s+are\s+now\b", re.IGNORECASE),
    re.compile(
        r"override\s+(?:your\s+)?(?:system\s+)?instructions",
        re.IGNORECASE,
    ),
]


def is_prompt_injection(message: str) -> bool:
    return any(pattern.search(message) for pattern in _PATTERNS)
