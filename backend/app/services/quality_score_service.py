from __future__ import annotations

from typing import Any, Dict, Iterable, List, Set


_TEMPLATE_REQUIREMENTS = {
    "ieee": [
        {"abstract"},
        {"introduction"},
        {"methods", "methodology"},
        {"results"},
        {"conclusion"},
        {"references"},
    ],
    "apa": [
        {"abstract"},
        {"introduction"},
        {"discussion"},
        {"conclusion"},
        {"references"},
    ],
    "acm": [
        {"abstract"},
        {"introduction"},
        {"system design", "methods", "methodology"},
        {"references"},
    ],
    "nature": [
        {"abstract"},
        {"introduction"},
        {"analysis", "results"},
        {"conclusion"},
        {"references"},
    ],
    "resume": [
        {"summary", "professional summary"},
        {"experience", "work experience"},
        {"education"},
        {"skills"},
    ],
}


def _normalize(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _flatten_aliases(alias_groups: Iterable[Set[str]]) -> List[str]:
    flattened: List[str] = []
    for alias_group in alias_groups:
        flattened.extend(sorted(alias_group))
    return flattened


def _collect_present_sections(structured_data: Dict[str, Any]) -> Set[str]:
    present: Set[str] = set()
    metadata = structured_data.get("metadata") or {}
    if _normalize(metadata.get("abstract")):
        present.add("abstract")
    if structured_data.get("references"):
        present.add("references")

    for heading in structured_data.get("headings") or []:
        normalized = _normalize(heading.get("text"))
        if normalized:
            present.add(normalized)

    return present


def _section_has_content(
    aliases: Set[str],
    structured_data: Dict[str, Any],
) -> bool:
    normalized_aliases = {_normalize(alias) for alias in aliases}
    metadata = structured_data.get("metadata") or {}
    if "abstract" in normalized_aliases and _normalize(metadata.get("abstract")):
        return True
    if "references" in normalized_aliases and structured_data.get("references"):
        return True

    for block in structured_data.get("blocks") or []:
        block_type = _normalize(block.get("block_type"))
        if block_type in {"heading_1", "heading_2", "heading_3", "heading_4", "abstract_heading", "references_heading"}:
            continue

        section_name = _normalize(block.get("section_name"))
        text = _normalize(block.get("text"))
        if not text:
            continue

        if section_name and any(alias in section_name for alias in normalized_aliases):
            return True

    return False


def compute_quality_score(
    structured_data: dict,
    template_name: str,
    validation_results: dict,
) -> dict:
    """Compute structural quality metrics for a formatted document."""
    normalized_template = _normalize(template_name) or "default"
    requirements = _TEMPLATE_REQUIREMENTS.get(
        normalized_template,
        [{"abstract"}, {"references"}],
    )

    present_sections = _collect_present_sections(structured_data)
    compliant_sections = 0
    content_complete_sections = 0

    for alias_group in requirements:
        normalized_aliases = {_normalize(alias) for alias in alias_group}
        if present_sections.intersection(normalized_aliases):
            compliant_sections += 1
        if _section_has_content(alias_group, structured_data):
            content_complete_sections += 1

    total_required = max(1, len(requirements))
    template_compliance_pct = round((compliant_sections / total_required) * 100, 2)
    content_completeness_pct = round((content_complete_sections / total_required) * 100, 2)

    references = structured_data.get("references") or []
    citation_count = len([reference for reference in references if reference])
    citation_target = max(1, int(validation_results.get("citation_target") or 5))
    citation_score_pct = round(min(citation_count / citation_target, 1.0) * 100, 2)

    overall_score = round(
        (template_compliance_pct * 0.4)
        + (content_completeness_pct * 0.4)
        + (citation_score_pct * 0.2),
        2,
    )

    return {
        "template_compliance_pct": template_compliance_pct,
        "content_completeness_pct": content_completeness_pct,
        "citation_count": citation_count,
        "overall_score": overall_score,
        "required_sections": _flatten_aliases(requirements),
    }
