import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

from app.application.conversation_manager import ConversationManager
from app.domain.user_session import UserSession
from app.domain.default_entity_manager import DefaultEntityManager
from app.application.intent_handler import IntentHandler

@pytest.fixture
def mock_user_session():
    session = MagicMock()
    session.user_id = "test_user"
    session.user_name = "Test User"
    session.history = []
    session.previous_result = {}
    return session

@pytest.fixture
def mock_default_entity_manager():
    manager = MagicMock()
    manager.apply_defaults.return_value = {}
    return manager

@pytest.fixture
def mock_intent_handler():
    handler = MagicMock()
    handler.handle_transaction.return_value = ("get_balance", "Saldo: R$ 1000,00")
    handler.handle_transfer_confirmation.return_value = ("transfer", "Transferência realizada com sucesso")
    return handler

@pytest.fixture
def mock_intent_service():
    service = MagicMock()
    service.process_message.return_value = {
        "intent": "get_balance",
        "entities": {},
        "missing_entities": [],
        "next_question": ""
    }
    return service

@pytest.fixture
def conversation_manager(mock_user_session, mock_default_entity_manager, mock_intent_handler, mock_intent_service):
    return ConversationManager(
        user_session=mock_user_session,
        default_entity_manager=mock_default_entity_manager,
        intent_handler=mock_intent_handler,
        intent_service=mock_intent_service,
        assistant_name="Test Assistant"
    )

def test_exit_conversation(conversation_manager, mock_user_session):
    mock_user_session.user_name = "Test User"
    result = conversation_manager.process_message("sair")
    assert result == (False, None, "Até logo, Test User!")

def test_error_handling(conversation_manager, mock_user_session, mock_intent_service):
    mock_user_session.previous_result = {}
    mock_intent_service.process_message.return_value = {
        "intent": "unknown",
        "entities": {},
        "missing_entities": [],
        "next_question": "Pode me ajudar a entender melhor o que você deseja fazer?"
    }
    result = conversation_manager.process_message("invalid message")
    assert result[0] is True
    assert result[1] == "error"
    assert "não entendi" in result[2].lower()

def test_missing_entities_handling(conversation_manager, mock_user_session, mock_intent_service):
    mock_user_session.previous_result = {}
    mock_intent_service.process_message.return_value = {
        "intent": "transfer",
        "entities": {"recipient": "Maria"},
        "missing_entities": ["amount"],
        "next_question": "Qual é o valor que você deseja transferir?"
    }
    result = conversation_manager.process_message("Quero transferir para Maria")
    assert result[0] is True
    assert result[1] == "warning"
    assert "missing" in result[2].lower()

def test_previous_missing_entities_handling(conversation_manager, mock_user_session, mock_intent_service, mock_intent_handler):
    mock_user_session.previous_result = {
        "intent": "transfer",
        "entities": {"recipient": "Maria"},
        "missing_entities": ["amount"]
    }
    mock_intent_service.process_message.return_value = {
        "intent": "transfer",
        "entities": {"amount": 100},
        "missing_entities": [],
        "next_question": ""
    }
    mock_intent_handler.handle_transaction.return_value = ("transfer", "Transferência realizada com sucesso")
    result = conversation_manager.process_message("100 reais")
    assert result[0] is True
    assert result[1] is None
    assert "sucesso" in result[2].lower()

def test_successful_transaction_handling(conversation_manager, mock_user_session, mock_intent_service, mock_intent_handler):
    mock_user_session.previous_result = {}
    mock_intent_service.process_message.return_value = {
        "intent": "get_balance",
        "entities": {"account_type": "corrente"},
        "missing_entities": [],
        "next_question": ""
    }
    mock_intent_handler.handle_transaction.return_value = ("get_balance", "Seu saldo é R$ 1000,00")
    result = conversation_manager.process_message("Qual é o meu saldo?")
    assert result[0] is True
    assert result[1] is None
    assert "saldo" in result[2].lower()

def test_default_entities_application(conversation_manager, mock_user_session, mock_intent_service, mock_default_entity_manager):
    mock_user_session.previous_result = {}
    mock_intent_service.process_message.return_value = {
        "intent": "get_balance",
        "entities": {},
        "missing_entities": [],
        "next_question": ""
    }
    mock_default_entity_manager.apply_defaults.return_value = {"account_type": "corrente"}
    result = conversation_manager.process_message("Qual é o meu saldo?")
    mock_default_entity_manager.apply_defaults.assert_called_once()

def test_history_management(conversation_manager, mock_user_session, mock_intent_service):
    mock_user_session.previous_result = {}
    mock_intent_service.process_message.return_value = {
        "intent": "get_help",
        "entities": {},
        "missing_entities": [],
        "next_question": "Como posso ajudar?"
    }
    conversation_manager.process_message("Olá")
    mock_user_session.add_to_history.assert_called_with("Test User: Olá")

def test_transfer_confirmation_flow(conversation_manager, mock_user_session, mock_intent_handler):
    mock_user_session.previous_result = {
        "intent": "transfer",
        "entities": {
            "amount": 100,
            "recipient": "Maria",
            "account_type": "corrente"
        },
        "missing_entities": []
    }
    mock_intent_handler.handle_transfer_confirmation.return_value = (True, "success", "Transferência realizada com sucesso!")
    result = conversation_manager.process_message("sim")
    assert result[0] is True
    assert result[1] == "success"
    assert "sucesso" in result[2].lower() 