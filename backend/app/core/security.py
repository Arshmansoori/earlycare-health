"""Zero-PII Privacy Protection & Security Sanitization Utilities."""
import uuid
from datetime import datetime, timezone


def generate_anonymous_screening_id() -> str:
    """Generates an anonymous, high-entropy screening identifier without PII."""
    year = datetime.now(timezone.utc).year
    unique_suffix = uuid.uuid4().hex[:8].upper()
    return f"EC-{year}-{unique_suffix}"


def sanitize_audit_log(payload: dict) -> dict:
    """Strips any potential accidentally submitted PII fields before logging."""
    pii_keys = {
        "name", "email", "student_id", "phone", "address",
        "ssn", "national_id", "ip_address", "user_id"
    }
    return {k: v for k, v in payload.items() if k.lower() not in pii_keys}
