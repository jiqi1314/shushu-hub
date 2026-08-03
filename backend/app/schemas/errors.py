"""Unified error response schemas with i18n-friendly error codes."""

from enum import Enum

from pydantic import BaseModel


class ErrorCode(str, Enum):
    """Stable, machine-readable error identifiers.

    Frontend uses these codes to look up localized messages in its i18n catalog.
    The English ``message`` below is only a fallback for non-i18n clients.
    """

    INVALID_DATETIME = "INVALID_DATETIME"
    INVALID_TIMEZONE = "INVALID_TIMEZONE"
    INVALID_MANUAL_LINES = "INVALID_MANUAL_LINES"
    UNSUPPORTED_SYSTEM = "UNSUPPORTED_SYSTEM"
    MISSING_LOCATION = "MISSING_LOCATION"
    MISSING_DAY_GANZHI = "MISSING_DAY_GANZHI"
    SYSTEM_COMPUTATION_FAILED = "SYSTEM_COMPUTATION_FAILED"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


_ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.INVALID_DATETIME: "Invalid datetime format. Use ISO 8601.",
    ErrorCode.INVALID_TIMEZONE: "Invalid timezone. Use an IANA name like 'Asia/Hong_Kong'.",
    ErrorCode.INVALID_MANUAL_LINES: (
        "Manual lines must be exactly 6 characters, each being '6', '7', '8', or '9'."
    ),
    ErrorCode.UNSUPPORTED_SYSTEM: "Unsupported divination system.",
    ErrorCode.MISSING_LOCATION: "Latitude and longitude are required for this system.",
    ErrorCode.MISSING_DAY_GANZHI: "Day ganzhi could not be derived from the provided datetime.",
    ErrorCode.SYSTEM_COMPUTATION_FAILED: "Divination computation failed.",
    ErrorCode.RATE_LIMIT_EXCEEDED: "Rate limit exceeded. Try again later.",
    ErrorCode.INTERNAL_ERROR: "Internal server error.",
}


def fallback_message(code: ErrorCode) -> str:
    return _ERROR_MESSAGES[code]


class ErrorResponse(BaseModel):
    """Standard error envelope.

    The frontend uses ``error_code`` as a stable key into its i18n catalog.
    ``message`` is the English fallback; locales can be translated client-side.
    """

    error_code: ErrorCode
    message: str
    details: dict | None = None
