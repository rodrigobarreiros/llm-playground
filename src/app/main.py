import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.logger import logger
from app.state_store import get_user_state
from app.intent_engine import process_message
from app.bank_actions import execute_action
from app.ui_console import print_assistant, print_user, print_info, print_warning, print_error

assistant_name = "Magie"
user_id = "rodrigo.barreiros"
user_name = "Rodrigo"
user_account_number = "000123"  # Default known account
history = []

read_only_intents = {"get_balance", "view_transactions", "get_help", "get_transactions"}
previous_result = {}

print()
print_assistant(assistant_name, f"Olá {user_name}, como posso te ajudar hoje? (Digite 'sair' para encerrar)")

while True:
    try:
        msg = print_user(user_name).strip()
        if msg.lower() in {"exit", "quit", "sair"}:
            print_assistant(assistant_name, f"Até logo, {user_name}!")
            break

        history.append(f"{user_name}: {msg}")
        result = process_message(user_id, history, msg)

        # If previous intent had missing entities, keep the previous intent
        if previous_result.get("missing_entities"):
            result["intent"] = previous_result["intent"]
            result["entities"] = {**previous_result.get("entities", {}), **result.get("entities", {})}

        if "error" in result:
            print_error(f"Não consegui entender. ({result['error']})\n")
            continue

        print_info(f"Intent → {result['intent']} | Entities → {result.get('entities', {})}")

        # Set known default entities
        default_entities = {
            "account_number": user_account_number,
            "account_type": "corrente"
        }
        for key, value in default_entities.items():
            result["entities"].setdefault(key, value)

        if result.get("missing_entities"):
            result["missing_entities"] = [
                m for m in result["missing_entities"] if m not in result["entities"]
            ]

        if result.get("missing_entities"):
            print_warning(f"Missing → {result['missing_entities']}")
            if result.get("next_question"):
                print_assistant(assistant_name, result['next_question'])
                history.append(f"{assistant_name}: {result['next_question']}")
            previous_result = result
        else:
            previous_result = {}  # Clear intent memory since we are done
            if result["intent"] in read_only_intents:
                response = execute_action(user_id, result["intent"], result["entities"])
                print_assistant(assistant_name, response)
            else:
                summary = f"Transferência de R$ {result['entities'].get('amount'):.2f} para {result['entities'].get('recipient')} da sua conta {result['entities'].get('account_type')}."
                print_assistant(assistant_name, summary + "\nVocê confirma essa operação? (sim/não)")
                confirmation = print_user(user_name).strip().lower()
                if confirmation in {"sim", "s", "yes", "y"}:
                    response = execute_action(user_id, result["intent"], result["entities"])
                    print_assistant(assistant_name, response)
                else:
                    print_assistant(assistant_name, "Operation canceled. Let me know if you need anything else.")

    except KeyboardInterrupt:
        print_assistant(assistant_name, f"Até logo, {user_name}!")
        break
    