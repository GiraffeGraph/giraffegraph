from collections.abc import Iterator
from dataclasses import dataclass
from re import Pattern
from re import compile as compile_pattern

from app.domain.hadith.normalization import NormalizedText, normalize_arabic_with_offsets

# Every lexicon below is written in normalize_arabic form; patterns run on normalised text only.
SIGHA_FORMULAS = (
    "حدثنا",
    "حدثني",
    "حدثناه",
    "حدثنيه",
    "اخبرنا",
    "اخبرني",
    "انبانا",
    "انباني",
    "نبانا",
    "نباني",
    "حدثهم",
    "حدثه",
    "اخبرهم",
    "اخبره",
    "سمعت",
    "سمعنا",
    "قرات علي",
    "قرا علينا",
    "عرضت علي",
    "كتب الي",
    "فيما قرا",
    "ذكر لنا",
    "ثنا",
    "انا",
    "عن",
    "ان",
)
# و/ف attached to ان or انا reads as the particles وأنّ / فإنّ / وأنا, which belong to the matn.
UNPREFIXED_SIGHA_FORMULAS = ("انا", "ان")
SIGHA_PATTERN = compile_pattern(
    r"(?:^|\s)(?:[وف](?!(?:"
    + "|".join(UNPREFIXED_SIGHA_FORMULAS)
    + r")(?:\s|$)))?("
    + "|".join(sorted(SIGHA_FORMULAS, key=len, reverse=True))
    + r")(?=\s|$)"
)
MATN_CUE_PATTERN = compile_pattern(
    r"رسول الله|النبي|صلي الله عليه وسلم|انه قال|انها قالت|سالت|بلغه|نهي|امر\s*ب"
)
TAHWIL_PATTERN = compile_pattern(r"(?:^|\s)ح(?=\s|$)")
CO_NARRATOR_PATTERN = compile_pattern(r"(?:^|\s)و(?=\s)")
HONORIFIC_PATTERN = compile_pattern(
    r"رضي الله عنهما|رضي الله عنها|رضي الله عنهم|رضي الله عنه|"
    r"عليه السلام|عليها السلام|رحمه الله|ام المومنين|المومنين"
)
TOKEN_PATTERN = compile_pattern(r"\S+")
LEADING_CONNECTIVES = frozenset({"و", "ف", "ثم", "قال", "قالت", "يقول", "انه", "انها", "ان"})
STOP_TOKENS = frozenset(
    {
        "الله",
        "رسول",
        "النبي",
        "قال",
        "قالت",
        "قالوا",
        "يقول",
        "انه",
        "انها",
        "ان",
        "عن",
        "في",
        "علي",
        "الي",
        "من",
        "مثله",
        "بهذا",
        "الاسناد",
        "نحوه",
        "جميعا",
        "كلاهما",
        "كلهم",
        "وهو",
        "يعني",
        "هو",
        "بن",
        "بنت",
    }
)
LEADING_CONNECTIVE_LIMIT = 3
MENTION_TOKEN_LIMIT = 9
MENTION_LIMIT = 40


@dataclass(frozen=True, slots=True, kw_only=True)
class NarratorMention:
    text: str
    start: int
    end: int
    position: int
    sigha: str
    sigha_start: int


@dataclass(frozen=True, slots=True, kw_only=True)
class IsnadChain:
    chain_no: int
    mentions: tuple[NarratorMention, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class SegmentedHadith:
    chains: tuple[IsnadChain, ...]
    matn_start: int | None


@dataclass(frozen=True, slots=True, kw_only=True)
class _Slice:
    text: str
    offset: int

    @property
    def end(self) -> int:
        return self.offset + len(self.text)

    def cut(self, start: int, end: int | None = None) -> "_Slice":
        return _Slice(text=self.text[start:end], offset=self.offset + start)


def segment_isnad(source: str) -> SegmentedHadith:
    normalized = normalize_arabic_with_offsets(source)
    chains: list[IsnadChain] = []
    matn_offset: int | None = None
    remaining = MENTION_LIMIT
    for chunk in _split(TAHWIL_PATTERN, _Slice(text=normalized.text, offset=0)):
        pieces = list(_iter_isnad_pieces(chunk))
        if matn_offset is None and pieces and pieces[0].end < chunk.end:
            matn_offset = pieces[0].end
        for piece in pieces:
            mentions = _chain_mentions(piece, normalized=normalized, source=source)[:remaining]
            if mentions:
                chains.append(IsnadChain(chain_no=len(chains) + 1, mentions=mentions))
                remaining -= len(mentions)
    return SegmentedHadith(
        chains=tuple(chains),
        matn_start=None if matn_offset is None else normalized.starts[matn_offset],
    )


def _iter_isnad_pieces(chunk: _Slice) -> Iterator[_Slice]:
    tail = chunk
    while (sigha := SIGHA_PATTERN.search(tail.text)) is not None:
        rest = tail.cut(sigha.start())
        cue = MATN_CUE_PATTERN.search(rest.text, sigha.end() - sigha.start())
        if cue is None:
            yield rest
            return
        yield rest.cut(0, cue.start())
        tail = rest.cut(cue.start())


def _chain_mentions(
    piece: _Slice,
    *,
    normalized: NormalizedText,
    source: str,
) -> tuple[NarratorMention, ...]:
    mentions: list[NarratorMention] = []
    previous_name = ""
    for sigha, name in _iter_names(piece):
        if name.text == previous_name:
            continue
        previous_name = name.text
        start, end = normalized.source_span(name.offset, name.end)
        mentions.append(
            NarratorMention(
                text=source[start:end],
                start=start,
                end=end,
                position=len(mentions) + 1,
                sigha=sigha.text,
                sigha_start=normalized.starts[sigha.offset],
            )
        )
    return tuple(mentions)


def _iter_names(piece: _Slice) -> Iterator[tuple[_Slice, _Slice]]:
    sighas = list(SIGHA_PATTERN.finditer(piece.text))
    candidate_ends = [*(sigha.start() for sigha in sighas[1:]), len(piece.text)]
    for sigha, candidate_end in zip(sighas, candidate_ends, strict=True):
        formula = piece.cut(*sigha.span(1))
        candidate = piece.cut(sigha.end(1), candidate_end)
        for part in _split(CO_NARRATOR_PATTERN, candidate):
            name = _find_name(part)
            if name is not None:
                yield formula, name


def _find_name(part: _Slice) -> _Slice | None:
    fragments = list(_split(HONORIFIC_PATTERN, part))
    tokens = [
        fragment.cut(*token.span())
        for fragment in fragments
        for token in TOKEN_PATTERN.finditer(fragment.text)
    ]
    for _ in range(LEADING_CONNECTIVE_LIMIT):
        if len(tokens) > 1 and tokens[0].text in LEADING_CONNECTIVES:
            del tokens[0]
    if all(token.text in STOP_TOKENS for token in tokens):
        return None
    # A mention is one contiguous source span, so it ends at the first honorific inside it.
    name_limit = next(fragment.end for fragment in fragments if fragment.end > tokens[0].offset)
    name_tokens = [token for token in tokens[:MENTION_TOKEN_LIMIT] if token.end <= name_limit]
    return part.cut(tokens[0].offset - part.offset, name_tokens[-1].end - part.offset)


def _split(pattern: Pattern[str], piece: _Slice) -> Iterator[_Slice]:
    start = 0
    for separator in pattern.finditer(piece.text):
        yield piece.cut(start, separator.start())
        start = separator.end()
    yield piece.cut(start)
