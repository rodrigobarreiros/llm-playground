from typing import Dict, Any, Tuple
from app.application.bank_application_service import BankApplicationService

class IntentHandler:
    READ_ONLY_INTENTS = {"get_balance", "view_transactions", "get_help", "get_transactions"}

    def __init__(self, user_id: str, user_name: str, assistant_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.assistant_name = assistant_name
        self.bank_service = BankApplicationService()

    def handle_transaction(self, intent: str, entities: Dict[str, Any]) -> Tuple[str, str]:
        """Route the intent to the appropriate bank operation and return the response message."""
        if intent == "get_balance":
            return self._handle_get_balance(entities)
        elif intent == "transfer":
            return self._handle_transfer(entities)
        elif intent == "get_transactions":
            return self._handle_get_transactions(entities)
        elif intent == "get_help":
            return self._handle_get_help()
        else:
            return "unknown", "Desculpe, não entendi. Você pode tentar novamente ou pedir ajuda?"

    def _handle_get_balance(self, entities: Dict[str, Any]) -> Tuple[str, str]:
        """Route balance inquiry to bank service."""
        account_type = entities.get("account_type", "corrente")
        _, message = self.bank_service.get_balance(self.user_id, account_type)
        return "get_balance", message

    def _handle_transfer(self, entities: Dict[str, Any]) -> Tuple[str, str]:
        """Route transfer operation to bank service."""
        amount = entities.get("amount")
        recipient = entities.get("recipient")
        from_account = entities.get("account_type", "corrente")

        if amount is None or recipient is None:
            return "transfer", "Faltando valor ou destinatário para a transferência."

        return self._handle_transfer_confirmation(entities)

    def _handle_get_transactions(self, entities: Dict[str, Any]) -> Tuple[str, str]:
        """Route transaction history request to bank service."""
        account_type = entities.get("account_type", "corrente")
        _, message = self.bank_service.get_transactions(self.user_id, account_type)
        return "get_transactions", message

    def _handle_get_help(self) -> Tuple[str, str]:
        """Route help request to bank service."""
        message = self.bank_service.get_help()
        return "get_help", message

    def _handle_transfer_confirmation(self, entities: Dict[str, Any]) -> Tuple[str, str]:
        """Handle the confirmation flow for transfer transactions."""
        summary = (
            f"Transferência de R$ {entities.get('amount'):.2f} para "
            f"{entities.get('recipient')} da sua conta {entities.get('account_type')}."
        )
        return "transfer_confirmation", summary + "\nVocê confirma essa operação? (sim/não)"

    def handle_transfer_confirmation(self, entities: Dict[str, Any], confirmation: str) -> Tuple[str, str]:
        """Handle the user's confirmation response for a transfer."""
        if confirmation.lower() in {"sim", "s", "yes", "y"}:
            success, message = self.bank_service.transfer(
                self.user_id,
                entities.get("account_type", "corrente"),
                entities.get("recipient"),
                entities.get("amount")
            )
            return "transfer", message
        else:
            return "transfer", "Operação cancelada. Me avise se precisar de mais alguma coisa." 