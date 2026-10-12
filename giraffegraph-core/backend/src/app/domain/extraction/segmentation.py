from dataclasses import dataclass, field
from re import split
from typing import Protocol


@dataclass(frozen=True, slots=True, kw_only=True)
class SegmentDraft:
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


class SegmentationStrategy(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def one_call_per_segment(self) -> bool: ...

    def split(self, raw_content: str) -> list[SegmentDraft]: ...


@dataclass(frozen=True, slots=True)
class ParagraphSegmentation:
    name: str = "paragraphs"
    one_call_per_segment: bool = False

    def split(self, raw_content: str) -> list[SegmentDraft]:
        paragraph_chunks = [
            item.strip() for item in split(r"\n\s*\n", raw_content) if item.strip()
        ]
        if len(paragraph_chunks) > 1:
            return [SegmentDraft(text=chunk) for chunk in paragraph_chunks]

        line_chunks = [line.strip() for line in raw_content.splitlines() if line.strip()]
        if line_chunks:
            return [SegmentDraft(text=chunk) for chunk in line_chunks]
        return [SegmentDraft(text=raw_content.strip())]
