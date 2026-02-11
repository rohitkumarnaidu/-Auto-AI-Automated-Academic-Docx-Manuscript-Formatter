from app.models import Reference, CitationStyle
from app.pipeline.contracts.loader import ContractLoader

class ReferenceFormatter:
    """
    Normalizes and formats references based on citation style rules.
    """
    def __init__(self, contract_loader: ContractLoader):
        self.contract_loader = contract_loader

    def format_reference(self, reference: Reference, publisher: str) -> str:
        """
        Produce a formatted string for a specific reference based on style.
        """
        contract = self.contract_loader.load(publisher)
        style_rule = contract.get("references", {}).get("style", "IEEE")
        
        # Simplified formatting for IEEE
        if style_rule == "IEEE":
            authors = reference.get_author_list(max_authors=3)
            title = f'"{reference.title}"' if reference.title else "Untitled"
            return f"[{reference.number}] {authors}, {title}, {reference.journal or reference.conference or ''}, {reference.year or ''}."
            
        return reference.raw_text
