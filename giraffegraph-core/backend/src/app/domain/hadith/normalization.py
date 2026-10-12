from collections.abc import Iterator
from dataclasses import dataclass
from re import compile as compile_pattern
from unicodedata import combining, normalize

HARAKAT_PATTERN = compile_pattern(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]")
PUNCTUATION_PATTERN = compile_pattern(r"[،.؛:!؟\"'()\[\]{}«»\-–—/\\*·]")
LETTER_FOLDS = str.maketrans(
    {"أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه", "ؤ": "و", "ئ": "ي"}
)


@dataclass(frozen=True, slots=True, kw_only=True)
class NormalizedText:
    text: str
    starts: tuple[int, ...]
    ends: tuple[int, ...]

    def source_span(self, start: int, end: int) -> tuple[int, int]:
        return self.starts[start], self.ends[end - 1]


def normalize_arabic(value: str) -> str:
    return normalize_arabic_with_offsets(value).text


def normalize_arabic_with_offsets(value: str) -> NormalizedText:
    characters: list[str] = []
    starts: list[int] = []
    ends: list[int] = []
    for cluster_start, cluster_end in _iter_cluster_spans(value):
        folded = _fold_cluster(value[cluster_start:cluster_end])
        if folded == "":
            if characters:
                ends[-1] = cluster_end
            continue
        for character in folded:
            if not character.isspace():
                characters.append(character)
                starts.append(cluster_start)
                ends.append(cluster_end)
            elif characters and characters[-1] == " ":
                ends[-1] = cluster_end
            elif characters:
                characters.append(" ")
                starts.append(cluster_start)
                ends.append(cluster_end)
    if characters and characters[-1] == " ":
        del characters[-1], starts[-1], ends[-1]
    return NormalizedText(text="".join(characters), starts=tuple(starts), ends=tuple(ends))


def _iter_cluster_spans(value: str) -> Iterator[tuple[int, int]]:
    cluster_start = 0
    for index in range(1, len(value)):
        if combining(value[index]) == 0:
            yield cluster_start, index
            cluster_start = index
    if value:
        yield cluster_start, len(value)


def _fold_cluster(cluster: str) -> str:
    folded = HARAKAT_PATTERN.sub("", normalize("NFKC", cluster))
    return PUNCTUATION_PATTERN.sub(" ", folded).translate(LETTER_FOLDS)
