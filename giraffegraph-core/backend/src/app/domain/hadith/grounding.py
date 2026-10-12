from app.domain.hadith.normalization import normalize_arabic
from app.domain.shared.resolution import normalize_text


def quote_in_segment(quote: str, segment_text: str) -> bool:
    return _contains_normalized(segment_text, quote)


def value_in_quote(value: str, quote: str) -> bool:
    return _contains_normalized(quote, value)


def value_equals_reference(value: str, reference: str) -> bool:
    normalized_value = normalize_for_grounding(value)
    return normalized_value != "" and normalized_value == normalize_for_grounding(reference)


def normalize_for_grounding(value: str) -> str:
    # normalize_arabic keeps letter case, so case folding comes from the engine's normalize_text.
    return normalize_arabic(normalize_text(value))


def _contains_normalized(container: str, fragment: str) -> bool:
    normalized_fragment = normalize_for_grounding(fragment)
    if normalized_fragment == "":
        return False
    return normalized_fragment in normalize_for_grounding(container)
