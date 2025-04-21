from typing import Dict, Any, Tuple, Optional
from app.domain.intent_service import process_message
from app.domain.user_session import UserSession
from app.domain.default_entity_manager import DefaultEntityManager
from app.application.intent_handler import IntentHandler

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
            intent_type, response = self.transaction_handler.handle_transfer_confirmation(
                self.user_session.previous_result.get("entities", {}),
                message
            )
            # Clear the previous result after handling confirmation
            self.user_session.previous_result = {}
            return True, None, response

        result = process_message(self.user_session.user_id, self.user_session.history, message)

        if self._handle_previous_missing_entities(result):
            return True, None, None

        if "error" in result:
            return True, "error", f"Não consegui entender. ({result['error']})\n"

        if result.get("intent") == "unknown":
            return True, "error", "Desculpe, não entendi. Você pode tentar novamente ou pedir ajuda?"

        info_message = f"Intent → {result['intent']} | Entities → {result.get('entities', {})}"

        # Apply default entities before handling missing entities
        result["entities"] = self.default_entity_manager.apply_defaults(result.get("entities", {}))

        if self._handle_missing_entities(result):
            return True, "warning", f"Missing → {result['missing_entities']}"

        self.user_session.clear_previous_result()
        
        # Handle the transaction and get the response
        intent_type, response = self.transaction_handler.handle_transaction(result["intent"], result["entities"])
        
        # If it's a transfer confirmation, store the transfer details and ask for confirmation
        if intent_type == "transfer_confirmation":
            self.user_session.previous_result = {
                "intent": "transfer",
                "entities": result["entities"]
            }
            return True, "transfer_confirmation", response
        
        return True, None, response

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

    def _detect_intent(self, message: str) -> tuple[str, Dict[str, Any]]:
        """Detect intent and extract entities from the message."""
        message = message.lower()
        entities = {}

        if "saldo" in message or "quanto" in message:
            intent = "get_balance"
            if "poupança" in message:
                entities["account_type"] = "poupança"
            else:
                entities["account_type"] = "corrente"
        elif "transferir" in message or "enviar" in message:
            intent = "transfer"
            # Extract amount and recipient (simplified)
            words = message.split()
            for i, word in enumerate(words):
                if word.replace(",", ".").replace("r$", "").replace("$", "").replace(".", "").isdigit():
                    entities["amount"] = float(word.replace(",", ".").replace("r$", "").replace("$", ""))
                if word.startswith("@") or word.startswith("para"):
                    entities["recipient"] = words[i + 1] if i + 1 < len(words) else None
            if "poupança" in message:
                entities["account_type"] = "poupança"
            else:
                entities["account_type"] = "corrente"
        elif "transações" in message or "histórico" in message:
            intent = "get_transactions"
            if "poupança" in message:
                entities["account_type"] = "poupança"
            else:
                entities["account_type"] = "corrente"
        elif "ajuda" in message or "help" in message:
            intent = "get_help"
        else:
            intent = "unknown"

        return intent, entities 