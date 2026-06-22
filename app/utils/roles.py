"""Role constants and normalization helpers."""

ORGANIZER = "organizer"
REVIEWER = "reviewer"
PARTICIPANT = "participant"

# Legacy alias kept for existing DB rows
LEGACY_ORGANIZER = "admin"

SELF_REGISTER_ROLES = {PARTICIPANT, REVIEWER, ORGANIZER}


def is_organizer(role: str) -> bool:
    return role in {ORGANIZER, LEGACY_ORGANIZER}


def normalize_role(role: str) -> str:
    """Expose organizer consistently in API responses."""
    if role == LEGACY_ORGANIZER:
        return ORGANIZER
    return role
