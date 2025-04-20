# bank_actions.py

from app.infra.logger import logger

# Contas simuladas em memória
accounts = {
    "rodrigo.barreiros": {
        "corrente": 1500.0,
        "savings": 3000.0,
        "transactions": []
    }
}

def execute_action(user_id, intent, entities):
    user_accounts = accounts.get(user_id)
    if not user_accounts:
        return f"Usuário '{user_id}' não encontrado."

    if intent == "get_balance":
        account_type = entities.get("account_type", "corrente")
        balance = user_accounts.get(account_type)
        if balance is not None:
            return f"O saldo da sua conta {account_type} é R$ {balance:.2f}."
        else:
            return f"Tipo de conta '{account_type}' não encontrado."

    elif intent == "transfer":
        amount = entities.get("amount")
        recipient = entities.get("recipient")
        from_account = entities.get("account_type", "corrente")

        if amount is None or recipient is None:
            return "Faltando valor ou destinatário para a transferência."

        if user_accounts[from_account] < amount:
            return "Saldo insuficiente."

        # Simula transferência
        user_accounts[from_account] -= amount
        user_accounts["transactions"].append({
            "type": "transferência",
            "to": recipient,
            "amount": amount,
            "from_account": from_account
        })

        return f"Transferido R$ {amount:.2f} para {recipient} da sua conta {from_account}."

    elif intent == "get_transactions":
        transactions = user_accounts.get("transactions", [])
        if not transactions:
            return "Você não tem transações recentes."
        return "Suas transações recentes:\n" + "\n".join(
            f"- {t['type']} para {t['to']} (R$ {t['amount']:.2f}) da conta {t['from_account']}"
            for t in transactions
        )

    elif intent == "get_help":
        return "Você pode me pedir para consultar saldos, transferir dinheiro ou mostrar transações recentes."

    else:
        return f"A intenção '{intent}' ainda não é suportada."
