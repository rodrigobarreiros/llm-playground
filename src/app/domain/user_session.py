from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class UserSession:
    user_id: str
    user_name: str
    account_number: str
    history: List[str]
    previous_result: Dict[str, Any] = None

    def __post_init__(self):
        if self.previous_result is None:
            self.previous_result = {}

    def add_to_history(self, message: str):
        self.history.append(message)

    def clear_previous_result(self):
        self.previous_result = {} 