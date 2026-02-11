import os
import yaml
from typing import Dict, Any, Optional

class ContractLoader:
    """
    Loads and provides access to template contracts.
    """
    def __init__(self, contracts_dir: str = "app/pipeline/contracts"):
        self.contracts_dir = contracts_dir
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load(self, name: str) -> Dict[str, Any]:
        """
        Load a contract by name (e.g., 'ieee').
        """
        name = name.lower()
        if name in self._cache:
            return self._cache[name]

        contract_path = os.path.join(self.contracts_dir, name, "contract.yaml")
        if not os.path.exists(contract_path):
            raise FileNotFoundError(f"Contract not found for publisher: {name}")

        try:
            with open(contract_path, 'r') as f:
                contract = yaml.safe_load(f)
                self._cache[name] = contract
                return contract
        except Exception as e:
            raise RuntimeError(f"Failed to load contract {name}: {e}")

    def get_canonical_name(self, publisher: str, section_name: str) -> str:
        """
        Get canonical section name for a given publisher.
        """
        contract = self.load(publisher)
        canonical_map = contract.get("sections", {}).get("canonical_names", {})
        return canonical_map.get(section_name.lower(), section_name.lower())

    def is_required(self, publisher: str, section_name: str) -> bool:
        """
        Check if a section is required by the contract.
        """
        contract = self.load(publisher)
        required = contract.get("sections", {}).get("required", [])
        return section_name.lower() in [s.lower() for s in required]
