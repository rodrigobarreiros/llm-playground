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
    handler.handle_transaction = Mock(return_value=("get_balance", "Saldo: R$ 1000,00"))
    handler.handle_transfer_confirmation = Mock(return_value=("transfer", "Transferência realizada com sucesso"))
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
    should_continue, msg_type, message = conversation_manager.process_message("exit")
    assert should_continue is False
    assert msg_type is None
    assert message == "Até logo, Test User!"
    conversation_manager.user_session.add_to_history.assert_called_once()

def test_error_handling(conversation_manager):
    """Test handling of error responses from intent processing."""
    with patch('app.application.conversation_manager.process_message') as mock_process:
        mock_process.return_value = {"error": "Test error"}
        should_continue, msg_type, message = conversation_manager.process_message("test message")
        assert should_continue is True
        assert msg_type == "error"
        assert message == "Não consegui entender. (Test error)\n"
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
        should_continue, msg_type, message = conversation_manager.process_message("transfer money")
        assert should_continue is True
        assert msg_type == "warning"
        assert message == "Missing → ['amount']"
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
        conversation_manager.transaction_handler.handle_transaction.return_value = ("transfer", "Transferência realizada com sucesso")
        should_continue, msg_type, message = conversation_manager.process_message("100")
        assert should_continue is True
        assert msg_type is None
        assert message == "Transferência realizada com sucesso"
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
        conversation_manager.transaction_handler.handle_transaction.return_value = ("get_balance", "Saldo: R$ 1000,00")
        should_continue, msg_type, message = conversation_manager.process_message("show my balance")
        assert should_continue is True
        assert msg_type is None
        assert message == "Saldo: R$ 1000,00"
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
        conversation_manager.transaction_handler.handle_transaction.return_value = ("transfer", "Transferência realizada com sucesso")
        should_continue, msg_type, message = conversation_manager.process_message("transfer 100")
        assert should_continue is True
        assert msg_type is None
        assert message == "Transferência realizada com sucesso"
        conversation_manager.default_entity_manager.apply_defaults.assert_called_once()
        conversation_manager.transaction_handler.handle_transaction.assert_called_once()

def test_history_management(conversation_manager):
    """Test that conversation history is properly managed."""
    with patch('app.application.conversation_manager.process_message') as mock_process:
        mock_process.return_value = {
            "intent": "get_balance",
            "entities": {"account_type": "corrente"}
        }
        conversation_manager.transaction_handler.handle_transaction.return_value = ("get_balance", "Saldo: R$ 1000,00")
        should_continue, msg_type, message = conversation_manager.process_message("show my balance")
        assert should_continue is True
        assert msg_type is None
        assert message == "Saldo: R$ 1000,00"
        conversation_manager.user_session.add_to_history.assert_called_with(
            "Test User: show my balance"
        )

def test_transfer_confirmation_flow(conversation_manager):
    """Test the complete transfer confirmation flow."""
    # First message initiates the transfer
    with patch('app.application.conversation_manager.process_message') as mock_process:
        # Mock the initial transfer request
        mock_process.return_value = {
            "intent": "transfer",
            "entities": {
                "amount": 100.0,
                "recipient": "Maria",
                "account_type": "corrente"
            }
        }
        # Mock the default entity manager to return the same entities
        conversation_manager.default_entity_manager.apply_defaults.return_value = {
            "amount": 100.0,
            "recipient": "Maria",
            "account_type": "corrente"
        }
        conversation_manager.transaction_handler.handle_transaction.return_value = (
            "transfer_confirmation",
            "Transferência de R$ 100.00 para Maria da sua conta corrente.\nVocê confirma essa operação? (sim/não)"
        )
        
        # Initial transfer request
        should_continue, msg_type, message = conversation_manager.process_message("transferir 100 para Maria")
        assert should_continue is True
        assert msg_type == "transfer_confirmation"
        assert "Você confirma essa operação?" in message
        assert conversation_manager.user_session.previous_result == {
            "intent": "transfer",
            "entities": {
                "amount": 100.0,
                "recipient": "Maria",
                "account_type": "corrente"
            }
        }

        # User confirms the transfer
        conversation_manager.transaction_handler.handle_transfer_confirmation.return_value = (
            "transfer",
            "Transferência realizada com sucesso"
        )
        should_continue, msg_type, message = conversation_manager.process_message("sim")
        assert should_continue is True
        assert msg_type is None
        assert message == "Transferência realizada com sucesso"
        conversation_manager.transaction_handler.handle_transfer_confirmation.assert_called_once_with(
            {
                "amount": 100.0,
                "recipient": "Maria",
                "account_type": "corrente"
            },
            "sim"
        )
        assert conversation_manager.user_session.previous_result == {} 