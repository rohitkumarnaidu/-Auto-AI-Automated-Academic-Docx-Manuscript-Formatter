from typing import Dict, Any
from app.models import Block, BlockType
from app.pipeline.contracts.loader import ContractLoader

class StyleMapper:
    """
    Maps semantic block labels to Word-compatible style names.
    Driven by contract.yaml.
    """
    def __init__(self, contract_loader: ContractLoader):
        self.contract_loader = contract_loader

    def get_style_name(self, block: Block, publisher: str) -> str:
        """
        Determine the Word style name for a block based on its type.
        """
        contract = self.contract_loader.load(publisher)
        style_map = contract.get("styles", {})
        
        # Determine the key for lookup
        bt = block.block_type
        if bt.startswith("heading_"):
            # Map level specific headings
            return style_map.get(bt.upper(), "Normal")
        
        # Map other types
        return style_map.get(bt.upper(), "Normal")
