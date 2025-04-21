from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from app.domain.intent_service import IntentService
from app.application.bank_application_service import BankApplicationService

class IntentHandler:
    def __init__(
        self,
        intent_service: IntentService,
        user_id: str
    ):
        self.intent_service = intent_service
        self.bank_service = BankApplicationService()
        self.user_id = user_id

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

    def handle_transfer_confirmation(self, entities: Dict[str, Any]) -> Tuple[bool, str, str]:
        """Handle transfer confirmation."""
        if not entities.get("amount") or not entities.get("recipient"):
            return False, "error", "Dados da transferência incompletos."

        transfer_successful = self.bank_service.transfer(
            self.user_id,
            entities["amount"],
            entities["recipient"],
            entities.get("account_type", "corrente")
        )

        if transfer_successful:
            return True, "success", f"Transferência de R${entities['amount']:.2f} para {entities['recipient']} realizada com sucesso!"
        else:
            return False, "error", "Não foi possível realizar a transferência. Verifique seu saldo e tente novamente." 