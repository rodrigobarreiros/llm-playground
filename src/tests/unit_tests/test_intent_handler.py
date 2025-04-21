import pytest
from unittest.mock import Mock, patch
from app.application.intent_handler import IntentHandler
from app.domain.intent_service import IntentService

@pytest.fixture
def mock_intent_service():
    return Mock(spec=IntentService)

@pytest.fixture
def mock_bank_service():
    return Mock()

@pytest.fixture
def intent_handler(mock_intent_service):
    return IntentHandler(mock_intent_service, "test_user")

def test_handle_transaction_get_balance(intent_handler):
    """Test handling get_balance intent."""
    with patch.object(intent_handler.bank_service, 'get_balance', return_value=(True, "Saldo: R$ 1000,00")):
        intent, message = intent_handler.handle_transaction("get_balance", {"account_type": "corrente"})
        assert intent == "get_balance"
        assert "Saldo" in message

def test_handle_transaction_transfer_success(intent_handler):
    """Test handling transfer intent with complete information."""
    with patch.object(intent_handler.bank_service, 'transfer', return_value=True):
        intent, message = intent_handler.handle_transaction("transfer", {
            "amount": 100,
            "recipient": "Maria",
            "account_type": "corrente"
        })
        assert intent == "transfer_confirmation"
        assert "Transferência" in message
        assert "confirma" in message

def test_handle_transaction_transfer_missing_info(intent_handler):
    """Test handling transfer intent with missing information."""
    intent, message = intent_handler.handle_transaction("transfer", {"amount": 100})
    assert intent == "transfer"
    assert "Faltando" in message

def test_handle_transaction_get_transactions(intent_handler):
    """Test handling get_transactions intent."""
    with patch.object(intent_handler.bank_service, 'get_transactions', return_value=(True, "Últimas transações...")):
        intent, message = intent_handler.handle_transaction("get_transactions", {"account_type": "corrente"})
        assert intent == "get_transactions"
        assert "transações" in message

def test_handle_transaction_get_help(intent_handler):
    """Test handling get_help intent."""
    with patch.object(intent_handler.bank_service, 'get_help', return_value="Ajuda disponível..."):
        intent, message = intent_handler.handle_transaction("get_help", {})
        assert intent == "get_help"
        assert "Ajuda" in message

def test_handle_transaction_unknown(intent_handler):
    """Test handling unknown intent."""
    intent, message = intent_handler.handle_transaction("unknown_intent", {})
    assert intent == "unknown"
    assert "não entendi" in message

def test_handle_transfer_confirmation_success(intent_handler):
    """Test successful transfer confirmation."""
    with patch.object(intent_handler.bank_service, 'transfer', return_value=True):
        success, status, message = intent_handler.handle_transfer_confirmation({
            "amount": 100,
            "recipient": "Maria",
            "account_type": "corrente"
        })
        assert success is True
        assert status == "success"
        assert "sucesso" in message

def test_handle_transfer_confirmation_failure(intent_handler):
    """Test failed transfer confirmation."""
    with patch.object(intent_handler.bank_service, 'transfer', return_value=False):
        success, status, message = intent_handler.handle_transfer_confirmation({
            "amount": 100,
            "recipient": "Maria",
            "account_type": "corrente"
        })
        assert success is False
        assert status == "error"
        assert "Não foi possível" in message

def test_handle_transfer_confirmation_missing_info(intent_handler):
    """Test transfer confirmation with missing information."""
    success, status, message = intent_handler.handle_transfer_confirmation({
        "amount": 100
    })
    assert success is False
    assert status == "error"
    assert "incompletos" in message

def test_handle_get_balance_default_account(intent_handler):
    """Test get balance with default account type."""
    with patch.object(intent_handler.bank_service, 'get_balance', return_value=(True, "Saldo: R$ 1000,00")):
        intent, message = intent_handler.handle_transaction("get_balance", {})
        assert intent == "get_balance"
        assert "Saldo" in message

def test_handle_get_transactions_default_account(intent_handler):
    """Test get transactions with default account type."""
    with patch.object(intent_handler.bank_service, 'get_transactions', return_value=(True, "Últimas transações...")):
        intent, message = intent_handler.handle_transaction("get_transactions", {})
        assert intent == "get_transactions"
        assert "transações" in message 