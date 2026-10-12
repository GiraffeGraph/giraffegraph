from dataclasses import dataclass
from itertools import pairwise
from typing import Any

from app.application.ports.llm_provider import LLMUsage, StructuredGeneration
from app.domain.hadith.segmenter import segment_isnad
from app.domain.shared.resolution import normalize_text

RULE_CONFIDENCE = 0.95


@dataclass(slots=True)
class RuleBasedIsnadProvider:
    provider_name: str = "rule_based_isnad"

    def generate_structured(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> dict[str, Any]:
        del prompt, schema_name, model
        hadith_ref = payload["source_unit"]["external_ref"]
        nodes_by_name: dict[str, dict[str, Any]] = {}
        relations: list[dict[str, Any]] = []
        for segment in payload["segments"]:
            for chain in segment_isnad(segment["text"]).chains:
                refs: list[str] = []
                for mention in chain.mentions:
                    # A name written twice in one payload is one node with two evidence quotes.
                    node = nodes_by_name.setdefault(
                        normalize_text(mention.text),
                        {
                            "ref": f"narrator-{len(nodes_by_name) + 1}",
                            "node_type": "Narrator",
                            "properties": {"name": mention.text},
                            "confidence": RULE_CONFIDENCE,
                            "evidence_refs": [],
                        },
                    )
                    node["evidence_refs"].append(_evidence(segment, mention.start, mention.end))
                    refs.append(node["ref"])
                links = pairwise(zip(refs, chain.mentions, strict=True))
                for position, ((from_ref, narrator), (to_ref, source)) in enumerate(links, 1):
                    properties: dict[str, Any] = {
                        "chain_no": segment["segment_order"] + chain.chain_no - 1,
                        "position": position,
                        "sigha": source.sigha,
                    }
                    if hadith_ref is not None:
                        properties["hadith_ref"] = hadith_ref
                    relations.append(
                        {
                            "relation_type": "NARRATED_FROM",
                            "from_ref": from_ref,
                            "to_ref": to_ref,
                            "properties": properties,
                            "confidence": RULE_CONFIDENCE,
                            "evidence_refs": [_evidence(segment, narrator.start, source.end)],
                        }
                    )
        return {"nodes": list(nodes_by_name.values()), "relations": relations}

    def generate_structured_with_usage(
        self,
        *,
        prompt: str,
        schema_name: str,
        payload: dict[str, Any],
        model: str | None = None,
    ) -> StructuredGeneration:
        return StructuredGeneration(
            output=self.generate_structured(
                prompt=prompt,
                schema_name=schema_name,
                payload=payload,
                model=model,
            ),
            usage=LLMUsage(model=model),
        )


def _evidence(segment: dict[str, Any], start: int, end: int) -> dict[str, Any]:
    return {
        "segment_id": segment["segment_id"],
        "quote": segment["text"][start:end],
        "start_offset": start,
        "end_offset": end,
    }
