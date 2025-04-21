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

@pytest.fixture
def mock_get_user_state():
    with patch('app.domain.intent_service.get_user_state') as mock:
        yield mock

def test_process_message_successful_transfer(intent_service, mock_query_llm, mock_update_user_state):
    # Arrange
    user_id = "123"
    history = ["Olá", "Quero transferir dinheiro"]
    user_input = "Quero transferir 100 reais para Maria"
    
    mock_response = """
    {
        "intent": "transfer",
        "entities": {
            "amount": 100,
            "recipient": "Maria"
        },
        "missing_entities": [],
        "next_question": ""
    }
    """
    mock_query_llm.return_value = mock_response

    # Act
    result = intent_service.process_message(user_id, history, user_input)

    # Assert
    assert result["intent"] == "transfer"
    assert result["entities"]["amount"] == 100
    assert result["entities"]["recipient"] == "Maria"
    assert result["missing_entities"] == []
    assert result["next_question"] == ""
    mock_update_user_state.assert_called_once()

def test_process_message_get_balance(intent_service, mock_query_llm, mock_update_user_state):
    # Arrange
    user_id = "123"
    history = ["Olá"]
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

    # Act
    result = intent_service.process_message(user_id, history, user_input)

    # Assert
    assert result["intent"] == "get_balance"
    assert result["entities"] == {}
    assert result["missing_entities"] == []
    assert result["next_question"] == ""
    mock_update_user_state.assert_called_once()

def test_process_message_missing_entities(intent_service, mock_query_llm, mock_update_user_state):
    # Arrange
    user_id = "123"
    history = ["Quero transferir dinheiro"]
    user_input = "Quero transferir para Maria"
    
    mock_response = """
    {
        "intent": "transfer",
        "entities": {
            "recipient": "Maria"
        },
        "missing_entities": ["amount"],
        "next_question": "Quanto você quer transferir?"
    }
    """
    mock_query_llm.return_value = mock_response

    # Act
    result = intent_service.process_message(user_id, history, user_input)

    # Assert
    assert result["intent"] == "transfer"
    assert result["entities"]["recipient"] == "Maria"
    assert "amount" in result["missing_entities"]
    assert result["next_question"] == "Quanto você quer transferir?"
    mock_update_user_state.assert_called_once()

def test_process_message_unknown_intent(intent_service, mock_query_llm, mock_update_user_state):
    # Arrange
    user_id = "123"
    history = ["Olá"]
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

    # Act
    result = intent_service.process_message(user_id, history, user_input)

    # Assert
    assert result["intent"] == "unknown"
    assert result["entities"] == {}
    assert result["missing_entities"] == []
    assert result["next_question"] == ""
    mock_update_user_state.assert_called_once()

def test_process_message_invalid_json_response(intent_service, mock_query_llm, mock_update_user_state):
    # Arrange
    user_id = "123"
    history = ["Olá"]
    user_input = "Quero transferir dinheiro"
    
    mock_response = "Invalid JSON response"
    mock_query_llm.return_value = mock_response

    # Act
    result = intent_service.process_message(user_id, history, user_input)

    # Assert
    assert "error" in result
    assert result["error"] == "No JSON block found in response."
    mock_update_user_state.assert_not_called()

def test_process_message_malformed_json(intent_service, mock_query_llm, mock_update_user_state):
    # Arrange
    user_id = "123"
    history = ["Olá"]
    user_input = "Quero transferir dinheiro"
    
    mock_response = """
    {
        intent: "transfer",
        entities: {
            amount: 100,
            recipient: "Maria"
        },
        missing_entities: [],
        next_question: ""
    }
    """
    mock_query_llm.return_value = mock_response

    # Act
    result = intent_service.process_message(user_id, history, user_input)

    # Assert
    assert result["intent"] == "transfer"
    assert result["entities"]["amount"] == 100
    assert result["entities"]["recipient"] == "Maria"
    assert result["missing_entities"] == []
    assert result["next_question"] == ""
    mock_update_user_state.assert_called_once()

def test_process_message_empty_response(intent_service, mock_query_llm, mock_update_user_state):
    # Arrange
    user_id = "123"
    history = ["Olá"]
    user_input = "Quero transferir dinheiro"
    
    mock_response = ""
    mock_query_llm.return_value = mock_response

    # Act
    result = intent_service.process_message(user_id, history, user_input)

    # Assert
    assert "error" in result
    assert result["error"] == "No JSON block found in response."
    mock_update_user_state.assert_not_called()

def test_process_message_invalid_intent(intent_service, mock_query_llm, mock_update_user_state):
    # Arrange
    user_id = "123"
    history = ["Olá"]
    user_input = "Quero transferir dinheiro"
    
    mock_response = """
    {
        "intent": "invalid_intent",
        "entities": {},
        "missing_entities": [],
        "next_question": ""
    }
    """
    mock_query_llm.return_value = mock_response

    # Act
    result = intent_service.process_message(user_id, history, user_input)

    # Assert
    assert result["intent"] == "unknown"
    assert result["entities"] == {}
    assert result["missing_entities"] == []
    assert result["next_question"] == ""
    mock_update_user_state.assert_called_once() 