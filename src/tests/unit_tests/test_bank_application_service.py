import pytest
from app.application.bank_application_service import BankApplicationService, Transaction, Account

@pytest.fixture
def bank_service():
    return BankApplicationService()

def test_get_balance_success(bank_service):
    """Test successful balance retrieval."""
    balance, message = bank_service.get_balance("rodrigo.barreiros", "corrente")
    assert balance == 1500.0
    assert "R$ 1500.00" in message
    assert "corrente" in message

def test_get_balance_invalid_user(bank_service):
    """Test balance retrieval for invalid user."""
    balance, message = bank_service.get_balance("nonexistent_user", "corrente")
    assert balance is None
    assert "não encontrado" in message

def test_get_balance_invalid_account(bank_service):
    """Test balance retrieval for invalid account type."""
    balance, message = bank_service.get_balance("rodrigo.barreiros", "invalid_account")
    assert balance is None
    assert "não encontrado" in message
    assert "invalid_account" in message

def test_transfer_success(bank_service):
    """Test successful money transfer."""
    success, message = bank_service.transfer("rodrigo.barreiros", "corrente", "Maria", 500.0)
    assert success is True
    assert "500.00" in message
    assert "Maria" in message
    
    # Verify balance was updated
    new_balance, _ = bank_service.get_balance("rodrigo.barreiros", "corrente")
    assert new_balance == 1000.0
    
    # Verify transaction was recorded
    transactions, _ = bank_service.get_transactions("rodrigo.barreiros", "corrente")
    assert len(transactions) == 1
    assert transactions[0].amount == 500.0
    assert transactions[0].to == "Maria"
    assert transactions[0].type == "transferência"

def test_transfer_insufficient_funds(bank_service):
    """Test transfer with insufficient funds."""
    success, message = bank_service.transfer("rodrigo.barreiros", "corrente", "Maria", 2000.0)
    assert success is False
    assert "insuficiente" in message
    
    # Verify balance remained unchanged
    balance, _ = bank_service.get_balance("rodrigo.barreiros", "corrente")
    assert balance == 1500.0

def test_transfer_invalid_user(bank_service):
    """Test transfer from invalid user."""
    success, message = bank_service.transfer("nonexistent_user", "corrente", "Maria", 100.0)
    assert success is False
    assert "não encontrado" in message

def test_transfer_invalid_account(bank_service):
    """Test transfer from invalid account type."""
    success, message = bank_service.transfer("rodrigo.barreiros", "invalid_account", "Maria", 100.0)
    assert success is False
    assert "não encontrado" in message
    assert "invalid_account" in message

def test_get_transactions_empty(bank_service):
    """Test getting transactions for account with no history."""
    transactions, message = bank_service.get_transactions("rodrigo.barreiros", "corrente")
    assert len(transactions) == 0
    assert "não tem transações" in message

def test_get_transactions_with_history(bank_service):
    """Test getting transactions after making transfers."""
    # Make two transfers
    bank_service.transfer("rodrigo.barreiros", "corrente", "Maria", 100.0)
    bank_service.transfer("rodrigo.barreiros", "corrente", "João", 200.0)
    
    transactions, message = bank_service.get_transactions("rodrigo.barreiros", "corrente")
    assert len(transactions) == 2
    assert transactions[0].to == "Maria"
    assert transactions[0].amount == 100.0
    assert transactions[1].to == "João"
    assert transactions[1].amount == 200.0
    assert "transações recentes" in message
    assert "Maria" in message
    assert "João" in message

def test_get_transactions_invalid_user(bank_service):
    """Test getting transactions for invalid user."""
    transactions, message = bank_service.get_transactions("nonexistent_user", "corrente")
    assert len(transactions) == 0
    assert "não encontrado" in message

def test_get_transactions_invalid_account(bank_service):
    """Test getting transactions for invalid account type."""
    transactions, message = bank_service.get_transactions("rodrigo.barreiros", "invalid_account")
    assert len(transactions) == 0
    assert "não encontrado" in message
    assert "invalid_account" in message

def test_get_help(bank_service):
    """Test getting help message."""
    message = bank_service.get_help()
    assert "saldos" in message
    assert "transferir" in message
    assert "transações" in message 