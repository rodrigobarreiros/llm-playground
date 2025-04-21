from typing import Dict, Any
from app.application.bank_application_service import BankApplicationService
from app.ui.console import print_assistant, print_user

class IntentHandler:
    READ_ONLY_INTENTS = {"get_balance", "view_transactions", "get_help", "get_transactions"}

    def __init__(self, user_id: str, user_name: str, assistant_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.assistant_name = assistant_name
        self.bank_service = BankApplicationService()

    def handle_transaction(self, intent: str, entities: Dict[str, Any]) -> None:
        """Route the intent to the appropriate bank operation."""
        if intent == "get_balance":
            self._handle_get_balance(entities)
        elif intent == "transfer":
            self._handle_transfer(entities)
        elif intent == "get_transactions":
            self._handle_get_transactions(entities)
        elif intent == "get_help":
            self._handle_get_help()

    def _handle_get_balance(self, entities: Dict[str, Any]) -> None:
        """Route balance inquiry to bank service."""
        account_type = entities.get("account_type", "corrente")
        _, message = self.bank_service.get_balance(self.user_id, account_type)
        print_assistant(self.assistant_name, message)

    def _handle_transfer(self, entities: Dict[str, Any]) -> None:
        """Route transfer operation to bank service."""
        amount = entities.get("amount")
        recipient = entities.get("recipient")
        from_account = entities.get("account_type", "corrente")

        if amount is None or recipient is None:
            print_assistant(self.assistant_name, "Faltando valor ou destinatário para a transferência.")
            return

        self._handle_transfer_confirmation(entities)

    def _handle_get_transactions(self, entities: Dict[str, Any]) -> None:
        """Route transaction history request to bank service."""
        account_type = entities.get("account_type", "corrente")
        _, message = self.bank_service.get_transactions(self.user_id, account_type)
        print_assistant(self.assistant_name, message)

    def _handle_get_help(self) -> None:
        """Route help request to bank service."""
        message = self.bank_service.get_help()
        print_assistant(self.assistant_name, message)

    def _handle_transfer_confirmation(self, entities: Dict[str, Any]) -> None:
        """Handle the confirmation flow for transfer transactions."""
        summary = (
            f"Transferência de R$ {entities.get('amount'):.2f} para "
            f"{entities.get('recipient')} da sua conta {entities.get('account_type')}."
        )
        print_assistant(self.assistant_name, summary + "\nVocê confirma essa operação? (sim/não)")
        
        confirmation = print_user(self.user_name).strip().lower()
        if confirmation in {"sim", "s", "yes", "y"}:
            success, message = self.bank_service.transfer(
                self.user_id,
                entities.get("account_type", "corrente"),
                entities.get("recipient"),
                entities.get("amount")
            )
            print_assistant(self.assistant_name, message)
        else:
            print_assistant(self.assistant_name, "Operação cancelada. Me avise se precisar de mais alguma coisa.") 