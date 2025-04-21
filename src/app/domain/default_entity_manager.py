from typing import Dict, Any

class DefaultEntityManager:
    def __init__(self, account_number: str):
        self.default_entities = {
            "account_number": account_number,
            "account_type": "corrente"
        }

    def apply_defaults(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Apply default entities to the given entities dictionary."""
        for key, value in self.default_entities.items():
            entities.setdefault(key, value)
        return entities 