import pytest
from app.domain.intent_service import process_message
from app.domain.state_repository import clear_user_state

class TestIntentEngine:

    def test_basic_intent_extraction(self):
        user_id = "test_user_1"
        history = []
        user_input = "Quero transferir 500 para João"

        result = process_message(user_id, history, user_input)

        assert "error" not in result, f"Erro no processamento: {result['error']}"
        assert result["intent"] == "transfer"

        clear_user_state(user_id)

    def test_get_balance(self):
        user_id = "test_user_2"
        history = []
        user_input = "Qual é o meu saldo?"

        result = process_message(user_id, history, user_input)

        assert "error" not in result, f"Erro no processamento: {result['error']}"
        assert result["intent"] == "get_balance"

        clear_user_state(user_id)
