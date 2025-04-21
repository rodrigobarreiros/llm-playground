import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from app.application.conversation_manager import ConversationManager
from app.domain.user_session import UserSession
from app.domain.default_entity_manager import DefaultEntityManager
from app.application.intent_handler import IntentHandler

@pytest.fixture
def mock_user_session():
    session = Mock(spec=UserSession)
    session.user_id = "test_user"
    session.user_name = "Test User"
    session.history = []
    session.previous_result = {}
    session.add_to_history = Mock()
    session.clear_previous_result = Mock()
    return session

@pytest.fixture
def mock_default_entity_manager():
    manager = Mock(spec=DefaultEntityManager)
    manager.apply_defaults = Mock(return_value={})
    return manager

@pytest.fixture
def mock_transaction_handler():
    handler = Mock(spec=IntentHandler)
    handler.handle_transaction = Mock()
    return handler

@pytest.fixture
def conversation_manager(mock_user_session, mock_default_entity_manager, mock_transaction_handler):
    return ConversationManager(
        user_session=mock_user_session,
        default_entity_manager=mock_default_entity_manager,
        transaction_handler=mock_transaction_handler,
        assistant_name="Test Assistant"
    )

def test_exit_conversation(conversation_manager):
    """Test that the conversation ends when user types exit command."""
    result = conversation_manager.process_message("exit")
    assert result is False
    conversation_manager.user_session.add_to_history.assert_called_once()

def test_error_handling(conversation_manager):
    """Test handling of error responses from intent processing."""
    with patch('app.application.conversation_manager.process_message') as mock_process:
        mock_process.return_value = {"error": "Test error"}
        result = conversation_manager.process_message("test message")
        assert result is True
        mock_process.assert_called_once()

def test_missing_entities_handling(conversation_manager):
    """Test handling of missing entities in the response."""
    with patch('app.application.conversation_manager.process_message') as mock_process:
        mock_process.return_value = {
            "intent": "transfer",
            "entities": {},
            "missing_entities": ["amount"],
            "next_question": "How much?"
        }
        result = conversation_manager.process_message("transfer money")
        assert result is True
        conversation_manager.user_session.previous_result = mock_process.return_value

def test_previous_missing_entities_handling(conversation_manager):
    """Test handling of missing entities from previous result."""
    conversation_manager.user_session.previous_result = {
        "intent": "transfer",
        "entities": {"account_type": "corrente"},
        "missing_entities": ["amount"]
    }
    
    with patch('app.application.conversation_manager.process_message') as mock_process:
        mock_process.return_value = {
            "entities": {"amount": 100.0}
        }
        result = conversation_manager.process_message("100")
        assert result is True
        conversation_manager.transaction_handler.handle_transaction.assert_called_once()

def test_successful_transaction_handling(conversation_manager):
    """Test successful processing of a complete transaction."""
    conversation_manager.default_entity_manager.apply_defaults.return_value = {
        "account_type": "corrente"
    }
    
    with patch('app.application.conversation_manager.process_message') as mock_process:
        mock_process.return_value = {
            "intent": "get_balance",
            "entities": {}
        }
        result = conversation_manager.process_message("show my balance")
        assert result is True
        conversation_manager.transaction_handler.handle_transaction.assert_called_once_with(
            "get_balance", {"account_type": "corrente"}
        )

def test_default_entities_application(conversation_manager):
    """Test that default entities are properly applied."""
    conversation_manager.default_entity_manager.apply_defaults.return_value = {
        "account_type": "corrente",
        "amount": 100.0
    }
    
    with patch('app.application.conversation_manager.process_message') as mock_process:
        mock_process.return_value = {
            "intent": "transfer",
            "entities": {"amount": 100.0}
        }
        result = conversation_manager.process_message("transfer 100")
        assert result is True
        conversation_manager.default_entity_manager.apply_defaults.assert_called_once()
        conversation_manager.transaction_handler.handle_transaction.assert_called_once()

def test_history_management(conversation_manager):
    """Test that conversation history is properly managed."""
    with patch('app.application.conversation_manager.process_message') as mock_process:
        mock_process.return_value = {
            "intent": "get_balance",
            "entities": {"account_type": "corrente"}
        }
        conversation_manager.process_message("show my balance")
        conversation_manager.user_session.add_to_history.assert_called_with(
            "Test User: show my balance"
        ) 