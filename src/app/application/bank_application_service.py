# bank_actions.py

from app.infra.logger_adapter import logger
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

@dataclass
class Transaction:
    type: str
    to: str
    amount: float
    from_account: str

@dataclass
class Account:
    balance: float
    transactions: List[Transaction]

class BankApplicationService:
    def __init__(self):
        # Simulated in-memory accounts
        self._accounts: Dict[str, Dict[str, Account]] = {
            "rodrigo.barreiros": {
                "corrente": Account(balance=1500.0, transactions=[]),
                "savings": Account(balance=3000.0, transactions=[])
            }
        }

    def get_balance(self, user_id: str, account_type: str) -> Tuple[Optional[float], str]:
        """Get the balance for a specific account type and return both the balance and response message."""
        user_accounts = self._accounts.get(user_id)
        if not user_accounts:
            return None, "Usuário não encontrado."
        
        account = user_accounts.get(account_type)
        if not account:
            return None, f"Tipo de conta '{account_type}' não encontrado."
        
        return account.balance, f"O saldo da sua conta {account_type} é R$ {account.balance:.2f}."

    def transfer(self, user_id: str, from_account: str, to_recipient: str, amount: float) -> Tuple[bool, str]:
        """Transfer money from one account to a recipient and return both success status and response message."""
        user_accounts = self._accounts.get(user_id)
        if not user_accounts:
            return False, "Usuário não encontrado."

        account = user_accounts.get(from_account)
        if not account:
            return False, f"Tipo de conta '{from_account}' não encontrado."
            
        if account.balance < amount:
            return False, "Saldo insuficiente para realizar a transferência."

        # Perform transfer
        account.balance -= amount
        account.transactions.append(
            Transaction(
                type="transferência",
                to=to_recipient,
                amount=amount,
                from_account=from_account
            )
        )
        return True, f"Transferido R$ {amount:.2f} para {to_recipient} da sua conta {from_account}."

    def get_transactions(self, user_id: str, account_type: str) -> Tuple[List[Transaction], str]:
        """Get transaction history for a specific account and return both transactions and response message."""
        user_accounts = self._accounts.get(user_id)
        if not user_accounts:
            return [], "Usuário não encontrado."

        account = user_accounts.get(account_type)
        if not account:
            return [], f"Tipo de conta '{account_type}' não encontrado."

        if not account.transactions:
            return [], "Você não tem transações recentes."

        transactions_text = "Suas transações recentes:\n" + "\n".join(
            f"- {t.type} para {t.to} (R$ {t.amount:.2f}) da conta {t.from_account}"
            for t in account.transactions
        )
        return account.transactions, transactions_text

    def get_help(self) -> str:
        """Get help message about available operations."""
        return "Você pode me pedir para consultar saldos, transferir dinheiro ou mostrar transações recentes."
