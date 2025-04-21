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

def test_multi_turn_transfer_conversation(intent_service, mock_query_llm, mock_update_user_state):
    # First message: User wants to transfer money
    mock_response_1 = """
    {
        "intent": "transfer",
        "entities": {
            "recipient": "Maria"
        },
        "missing_entities": ["amount"],
        "next_question": "Quanto você quer transferir?"
    }
    """
    mock_query_llm.return_value = mock_response_1

    result = intent_service.process_message("123", ["Olá"], "Quero transferir para Maria")
    assert result["intent"] == "transfer"
    assert result["entities"]["recipient"] == "Maria"
    assert "amount" in result["missing_entities"]
    assert result["next_question"] == "Quanto você quer transferir?"

    # Second message: User provides the amount
    mock_response_2 = """
    {
        "intent": "transfer",
        "entities": {
            "recipient": "Maria",
            "amount": 100
        },
        "missing_entities": [],
        "next_question": ""
    }
    """
    mock_query_llm.return_value = mock_response_2

    result = intent_service.process_message("123", ["Olá", "Quero transferir para Maria", "Quanto você quer transferir?"], "100 reais")
    assert result["intent"] == "transfer"
    assert result["entities"]["recipient"] == "Maria"
    assert result["entities"]["amount"] == 100
    assert result["missing_entities"] == []
    assert result["next_question"] == ""

def test_multi_turn_balance_conversation(intent_service, mock_query_llm, mock_update_user_state):
    # First message: User asks about balance
    mock_response_1 = """
    {
        "intent": "get_balance",
        "entities": {},
        "missing_entities": [],
        "next_question": ""
    }
    """
    mock_query_llm.return_value = mock_response_1

    result = intent_service.process_message("123", ["Olá"], "Qual é o meu saldo?")
    assert result["intent"] == "get_balance"
    assert result["entities"] == {}
    assert result["missing_entities"] == []
    assert result["next_question"] == ""

    # Second message: User asks about a specific account type
    mock_response_2 = """
    {
        "intent": "get_balance",
        "entities": {
            "account_type": "poupança"
        },
        "missing_entities": [],
        "next_question": ""
    }
    """
    mock_query_llm.return_value = mock_response_2

    result = intent_service.process_message("123", ["Olá", "Qual é o meu saldo?"], "E da poupança?")
    assert result["intent"] == "get_balance"
    assert result["entities"]["account_type"] == "poupança"
    assert result["missing_entities"] == []
    assert result["next_question"] == ""

def test_multi_turn_help_conversation(intent_service, mock_query_llm, mock_update_user_state):
    # First message: User asks for help
    mock_response_1 = """
    {
        "intent": "get_help",
        "entities": {},
        "missing_entities": [],
        "next_question": ""
    }
    """
    mock_query_llm.return_value = mock_response_1

    result = intent_service.process_message("123", ["Olá"], "O que você pode fazer?")
    assert result["intent"] == "get_help"
    assert result["entities"] == {}
    assert result["missing_entities"] == []
    assert result["next_question"] == ""

    # Second message: User asks about a specific operation
    mock_response_2 = """
    {
        "intent": "get_help",
        "entities": {
            "operation": "transfer"
        },
        "missing_entities": [],
        "next_question": ""
    }
    """
    mock_query_llm.return_value = mock_response_2

    result = intent_service.process_message("123", ["Olá", "O que você pode fazer?"], "Como faço uma transferência?")
    assert result["intent"] == "get_help"
    assert result["entities"]["operation"] == "transfer"
    assert result["missing_entities"] == []
    assert result["next_question"] == "" 
    