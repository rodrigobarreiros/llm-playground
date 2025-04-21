from typing import Dict, Any, Tuple, Optional
from app.domain.intent_service import IntentService
from app.domain.user_session import UserSession
from app.domain.default_entity_manager import DefaultEntityManager
from app.application.intent_handler import IntentHandler

class ConversationManager:
    def __init__(
        self,
        user_session: UserSession,
        default_entity_manager: DefaultEntityManager,
        intent_handler: IntentHandler,
        assistant_name: str,
        intent_service: Optional[IntentService] = None
    ):
        self.user_session = user_session
        self.default_entity_manager = default_entity_manager
        self.intent_handler = intent_handler
        self.assistant_name = assistant_name
        self.intent_service = intent_service or IntentService()

    def process_message(self, message: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Process a user message and return:
        - bool: whether to continue the conversation
        - Optional[str]: message type (error, info, warning, or None)
        - Optional[str]: message content
        """
        self.user_session.add_to_history(f"{self.user_session.user_name}: {message}")
        
        if message.lower() in {"exit", "quit", "sair"}:
            return False, None, f"Até logo, {self.user_session.user_name}!"

        # Check if we're in a transfer confirmation flow
        if self.user_session.previous_result and self.user_session.previous_result.get("intent") == "transfer" and not self.user_session.previous_result.get("missing_entities"):
            # Handle the confirmation response
            success, msg_type, response = self.intent_handler.handle_transfer_confirmation(
                self.user_session.previous_result.get("entities", {})
            )
            # Clear the previous result after handling confirmation
            self.user_session.previous_result = {}
            return True, msg_type, response

        result = self.intent_service.process_message(
            self.user_session.user_id,
            self.user_session.history,
            message
        )

        if self._handle_previous_missing_entities(result):
            return True, None, None

        if "error" in result:
            return True, "error", f"Não consegui entender. ({result['error']})\n"

        if result.get("intent") == "unknown":
            return True, "error", "Desculpe, não entendi. Você pode tentar novamente ou pedir ajuda?"

        # Apply default entities before handling missing entities
        result["entities"] = self.default_entity_manager.apply_defaults(result.get("entities", {}))

        if self._handle_missing_entities(result):
            return True, "warning", f"Missing → {result['missing_entities']}"

        # Store the result before handling the transaction
        self.user_session.previous_result = result.copy()
        
        # Handle the transaction and get the response
        intent_type, response = self.intent_handler.handle_transaction(result["intent"], result["entities"])
        
        # If it's a transfer confirmation, store the transfer details and ask for confirmation
        if intent_type == "transfer_confirmation":
            return True, "transfer_confirmation", response
        
        # Return the response first, then clear the previous result
        response_tuple = (True, None, response)
        
        # Clear the previous result only if it's not a transfer confirmation
        if intent_type != "transfer_confirmation":
            self.user_session.clear_previous_result()
        
        return response_tuple

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
                if result.get("next_question"):
                    self.user_session.add_to_history(f"{self.assistant_name}: {result['next_question']}")
                self.user_session.previous_result = result
                return True
        return False 