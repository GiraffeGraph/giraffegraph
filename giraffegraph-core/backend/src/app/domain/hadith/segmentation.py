from dataclasses import dataclass

from app.domain.extraction.segmentation import SegmentDraft
from app.domain.hadith.segmenter import segment_isnad


@dataclass(frozen=True, slots=True)
class IsnadSegmentation:
    name: str = "isnad"
    one_call_per_segment: bool = True

    def split(self, raw_content: str) -> list[SegmentDraft]:
        segmented = segment_isnad(raw_content)
        drafts: list[SegmentDraft] = []
        for chain in segmented.chains:
            start = chain.mentions[0].sigha_start
            end = chain.mentions[-1].end
            # Past the matn boundary the transmission particles mostly belong to the narrative.
            if segmented.matn_start is not None and start >= segmented.matn_start:
                continue
            drafts.append(
                SegmentDraft(
                    text=raw_content[start:end],
                    metadata={
                        "chain_no": str(chain.chain_no),
                        "start_offset": str(start),
                        "end_offset": str(end),
                    },
                )
            )
        if drafts:
            return drafts
        return [SegmentDraft(text=raw_content.strip(), metadata={"fallback": "whole_text"})]
