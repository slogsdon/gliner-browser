from __future__ import annotations

from difflib import SequenceMatcher
import re
from typing import Any


def render_elements(elements: list[dict[str, str]]) -> str:
    return "".join(
        f'@{element["id"]} {element["role"]} "{element["name"]}"\n'
        for element in elements
    )


def element_for_span(
    rendered: str,
    elements: list[dict[str, str]],
    span: dict[str, Any],
) -> dict[str, Any] | None:
    start = int(span.get("start", -1))
    end = int(span.get("end", -1))
    if start < 0 or end <= start or end > len(rendered):
        return None

    offset = 0
    for line, element in zip(rendered.splitlines(keepends=True), elements):
        line_end = offset + len(line)
        if start < line_end and end > offset:
            return {**element, "confidence": float(span.get("confidence", 0.0))}
        offset = line_end
    return None


def lexical_matches(
    query: str,
    elements: list[dict[str, str]],
    limit: int = 5,
) -> list[dict[str, Any]]:
    normalized_query = " ".join(re.findall(r"\w+", query.casefold()))
    query_tokens = set(normalized_query.split())
    ranked = []
    for element in elements:
        description = " ".join(
            re.findall(r"\w+", f'{element["role"]} {element["name"]}'.casefold())
        )
        description_tokens = set(description.split())
        union = query_tokens | description_tokens
        token_score = len(query_tokens & description_tokens) / len(union) if union else 0.0
        score = max(SequenceMatcher(None, normalized_query, description).ratio(), token_score)
        ranked.append({**element, "confidence": round(score, 4), "source": "lexical"})
    return sorted(ranked, key=lambda item: item["confidence"], reverse=True)[:limit]


class GlinerResolver:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model: Any = None

    def _load(self) -> Any:
        if self._model is None:
            from gliner2 import AutoExtractor

            self._model = AutoExtractor.from_pretrained(self.model_name)
        return self._model

    def find(
        self,
        query: str,
        elements: list[dict[str, str]],
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        if not elements:
            return []
        # ponytail: lexical prefilter caps model context; batch candidates if pages
        # with more than 50 similar controls prove common.
        lexical = lexical_matches(query, elements, min(limit * 10, 50))
        candidates = [dict(match) for match in lexical]
        rendered = render_elements(candidates)
        label = f"interactive website element matching this request: {query}"
        result = self._load().extract_entities(
            rendered,
            [label],
            threshold=0.15,
            include_confidence=True,
            include_spans=True,
        )
        spans = result.get("entities", {}).get(label, [])
        matches = [element_for_span(rendered, candidates, span) for span in spans]
        semantic = {match["id"]: match["confidence"] for match in matches if match}
        ranked = []
        for match in lexical:
            lexical_confidence = match["confidence"]
            semantic_confidence = semantic.get(match["id"], 0.0)
            ranked.append(
                {
                    **match,
                    "confidence": round(0.7 * lexical_confidence + 0.3 * semantic_confidence, 4),
                    "lexical_confidence": lexical_confidence,
                    "gliner_confidence": round(semantic_confidence, 4),
                    "source": "gliner+lexical",
                }
            )
        return sorted(ranked, key=lambda item: item["confidence"], reverse=True)[:limit]
