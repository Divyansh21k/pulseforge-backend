from rapidfuzz import fuzz


def name_similarity(name_a: str, name_b: str) -> float:
    """Returns a 0.0-1.0 similarity score between two names."""
    a = (name_a or "").strip().lower()
    b = (name_b or "").strip().lower()
    if not a or not b:
        return 0.0
    return fuzz.token_sort_ratio(a, b) / 100
