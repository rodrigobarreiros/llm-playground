import pytest
from unittest.mock import patch, MagicMock
from app.domain.intent_service import IntentService

@pytest.fixture
def intent_service():
    return IntentService()

@pytest.fixture
def mock_query_llm():
    with patch('app.domain.intent_service.query_llm') as mock:
        yield mock

@pytest.fixture
def mock_update_user_state():
    with patch('app.domain.intent_service.update_user_state') as mock:
        yield mock

class TestIntentEngine:
    def test_basic_intent_extraction(self, intent_service, mock_query_llm, mock_update_user_state):
        user_id = "test_user_1"
        history = []
        user_input = "Quero transferir 500 para João"

        mock_response = """
        {
            "intent": "transfer",
            "entities": {
                "amount": 500,
                "recipient": "João"
            },
            "missing_entities": [],
            "next_question": ""
        }
        """
        mock_query_llm.return_value = mock_response

        result = intent_service.process_message(user_id, history, user_input)

        assert "error" not in result, f"Erro no processamento: {result['error']}"
        assert result["intent"] == "transfer"
        assert result["entities"]["amount"] == 500
        assert result["entities"]["recipient"] == "João"
        assert result["missing_entities"] == []
        assert result["next_question"] == ""

    def test_get_balance(self, intent_service, mock_query_llm, mock_update_user_state):
        user_id = "test_user_2"
        history = []
        user_input = "Qual é o meu saldo?"

        mock_response = """
        {
            "intent": "get_balance",
            "entities": {},
            "missing_entities": [],
            "next_question": ""
        }
        """
        mock_query_llm.return_value = mock_response

        result = intent_service.process_message(user_id, history, user_input)

        assert "error" not in result, f"Erro no processamento: {result['error']}"
        assert result["intent"] == "get_balance"
        assert result["entities"] == {}
        assert result["missing_entities"] == []
        assert result["next_question"] == ""

    def test_get_transactions(self, intent_service, mock_query_llm, mock_update_user_state):
        user_id = "test_user_3"
        history = []
        user_input = "Quero ver meu extrato"

        mock_response = """
        {
            "intent": "get_transactions",
            "entities": {},
            "missing_entities": [],
            "next_question": ""
        }
        """
        mock_query_llm.return_value = mock_response

        result = intent_service.process_message(user_id, history, user_input)

        assert "error" not in result, f"Erro no processamento: {result['error']}"
        assert result["intent"] == "get_transactions"
        assert result["entities"] == {}
        assert result["missing_entities"] == []
        assert result["next_question"] == ""

    def test_get_help(self, intent_service, mock_query_llm, mock_update_user_state):
        user_id = "test_user_4"
        history = []
        user_input = "O que você pode fazer?"

        mock_response = """
        {
            "intent": "get_help",
            "entities": {},
            "missing_entities": [],
            "next_question": ""
        }
        """
        mock_query_llm.return_value = mock_response

        result = intent_service.process_message(user_id, history, user_input)

        assert "error" not in result, f"Erro no processamento: {result['error']}"
        assert result["intent"] == "get_help"
        assert result["entities"] == {}
        assert result["missing_entities"] == []
        assert result["next_question"] == ""

    def test_unknown_intent(self, intent_service, mock_query_llm, mock_update_user_state):
        user_id = "test_user_5"
        history = []
        user_input = "Alguma coisa aleatória"

        mock_response = """
        {
            "intent": "unknown",
            "entities": {},
            "missing_entities": [],
            "next_question": ""
        }
        """
        mock_query_llm.return_value = mock_response

        result = intent_service.process_message(user_id, history, user_input)

        assert "error" not in result, f"Erro no processamento: {result['error']}"
        assert result["intent"] == "unknown"
        assert result["entities"] == {}
        assert result["missing_entities"] == []
        assert result["next_question"] == ""
