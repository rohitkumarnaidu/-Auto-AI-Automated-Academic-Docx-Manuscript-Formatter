"""
Reference Formatter Engine - Deterministic, rule-based formatting.
Uses templates from contract.yaml.
"""

from typing import List, Optional, Dict
from app.models import Reference, ReferenceType
from app.pipeline.contracts.loader import ContractLoader

class ReferenceFormatterEngine:
    """
    Formats Reference objects into strings based on publisher rules.
    Strictly rule-based, no LLM.
    """
    
    def __init__(self, contract_loader: ContractLoader):
        self.contract_loader = contract_loader

    def process(self, document: Document) -> Document:
        """Standard pipeline stage entry point."""
        publisher = document.template.template_name if document.template else "IEEE"
        document.references = self.format_all(document.references, publisher)
        return document

    def format_all(self, references: List[Reference], publisher: str) -> List[Reference]:
        """Format a list of references."""
        contract = self.contract_loader.load(publisher)
        rules = contract.get("references", {}).get("normalization", {})
        
        if not rules:
            return references
            
        for ref in references:
            ref.formatted_text = self.format_single(ref, rules)
            
        return references

    def format_single(self, ref: Reference, rules: Dict) -> str:
        """Apply formatting template to a single reference."""
        ref_type = ref.reference_type
        
        # Select template
        template = rules.get("journal_format") if ref_type == ReferenceType.JOURNAL_ARTICLE else \
                   rules.get("conference_format") if ref_type == ReferenceType.CONFERENCE_PAPER else \
                   rules.get("default_format", "{authors}, {title}, {year}.")

        # 1. Format Authors
        max_authors = rules.get("max_authors", 99)
        et_al = rules.get("et_al_suffix", "et al.")
        
        if len(ref.authors) > max_authors:
            authors_str = f"{ref.authors[0]} {et_al}"
        else:
            authors_str = ", ".join(ref.authors)
            
        # 2. Fill Template
        # Mapping of fields to safe values
        data = {
            "authors": authors_str,
            "title": ref.title or "[Missing Title]",
            "journal": ref.journal or ref.metadata.get("journal_full", ""),
            "conference": ref.conference or ref.metadata.get("conf_full", ""),
            "year": str(ref.year) if ref.year else "[n.d.]",
            "volume": ref.volume or "",
            "issue": ref.issue or "",
            "pages": ref.pages or "",
            "doi": f"doi: {ref.doi}" if ref.doi else ""
        }
        
        try:
            formatted = template.format(**data)
            # Cleanup double punctuation
            formatted = formatted.replace("..", ".").replace(",,", ",").strip()
            return formatted
        except Exception as e:
            # Fallback to raw if template fails
            return ref.raw_text
