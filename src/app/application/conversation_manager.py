from typing import Dict, Any
from app.domain.intent_service import process_message
from app.domain.user_session import UserSession
from app.domain.default_entity_manager import DefaultEntityManager
from app.application.intent_handler import IntentHandler
from app.ui.console import print_assistant, print_user, print_info, print_warning, print_error

class ConversationManager:
    def __init__(
        self,
        user_session: UserSession,
        default_entity_manager: DefaultEntityManager,
        transaction_handler: IntentHandler,
        assistant_name: str
    ):
        self.user_session = user_session
        self.default_entity_manager = default_entity_manager
        self.transaction_handler = transaction_handler
        self.assistant_name = assistant_name

    def process_message(self, message: str) -> bool:
        """Process a user message and return whether to continue the conversation."""
        self.user_session.add_to_history(f"{self.user_session.user_name}: {message}")
        
        if message.lower() in {"exit", "quit", "sair"}:
            print_assistant(self.assistant_name, f"Até logo, {self.user_session.user_name}!")
            return False

        result = process_message(self.user_session.user_id, self.user_session.history, message)

        if self._handle_previous_missing_entities(result):
            return True

        if "error" in result:
            print_error(f"Não consegui entender. ({result['error']})\n")
            return True

        print_info(f"Intent → {result['intent']} | Entities → {result.get('entities', {})}")

        # Apply default entities before handling missing entities
        result["entities"] = self.default_entity_manager.apply_defaults(result.get("entities", {}))

        if self._handle_missing_entities(result):
            return True

        self.user_session.clear_previous_result()
        self.transaction_handler.handle_transaction(result["intent"], result["entities"])
        return True

    def _handle_previous_missing_entities(self, result: Dict[str, Any]) -> bool:
        """Handle missing entities from previous result."""
        if self.user_session.previous_result.get("missing_entities"):
            result["intent"] = self.user_session.previous_result["intent"]
            result["entities"] = {
                **self.user_session.previous_result.get("entities", {}),
                **result.get("entities", {})
            }
            return False
        return False

    def _handle_missing_entities(self, result: Dict[str, Any]) -> bool:
        """Handle missing entities in the current result."""
        if result.get("missing_entities"):
            result["missing_entities"] = [
                m for m in result["missing_entities"]
                if m not in result["entities"]
            ]

            if result["missing_entities"]:
                print_warning(f"Missing → {result['missing_entities']}")
                if result.get("next_question"):
                    print_assistant(self.assistant_name, result['next_question'])
                    self.user_session.add_to_history(f"{self.assistant_name}: {result['next_question']}")
                self.user_session.previous_result = result
                return True
        return False 