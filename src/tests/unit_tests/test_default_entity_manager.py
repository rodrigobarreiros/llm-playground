import pytest
from app.domain.default_entity_manager import DefaultEntityManager

@pytest.fixture
def entity_manager():
    return DefaultEntityManager("12345")

def test_initialization(entity_manager):
    """Test that the manager is initialized with correct default values."""
    assert entity_manager.default_entities["account_number"] == "12345"
    assert entity_manager.default_entities["account_type"] == "corrente"

def test_apply_defaults_empty_entities(entity_manager):
    """Test applying defaults to empty entities dictionary."""
    entities = {}
    result = entity_manager.apply_defaults(entities)
    
    assert result["account_number"] == "12345"
    assert result["account_type"] == "corrente"
    assert len(result) == 2

def test_apply_defaults_partial_entities(entity_manager):
    """Test applying defaults when some entities are already present."""
    entities = {"account_type": "poupança"}
    result = entity_manager.apply_defaults(entities)
    
    assert result["account_number"] == "12345"
    assert result["account_type"] == "poupança"  # Should not override existing value
    assert len(result) == 2

def test_apply_defaults_all_entities_present(entity_manager):
    """Test applying defaults when all entities are already present."""
    entities = {
        "account_number": "67890",
        "account_type": "poupança"
    }
    result = entity_manager.apply_defaults(entities)
    
    assert result["account_number"] == "67890"  # Should not override
    assert result["account_type"] == "poupança"  # Should not override
    assert len(result) == 2

def test_apply_defaults_with_additional_entities(entity_manager):
    """Test applying defaults with additional entities not in defaults."""
    entities = {
        "amount": 100,
        "recipient": "Maria"
    }
    result = entity_manager.apply_defaults(entities)
    
    assert result["account_number"] == "12345"
    assert result["account_type"] == "corrente"
    assert result["amount"] == 100
    assert result["recipient"] == "Maria"
    assert len(result) == 4 