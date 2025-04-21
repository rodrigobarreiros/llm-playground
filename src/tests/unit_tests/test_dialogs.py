import json
import pytest
from unittest.mock import patch, MagicMock
from app.domain.intent_service import IntentService

# Load test cases from external JSON file
with open("tests/resources/dialogs.json", encoding="utf-8") as f:
    test_cases = json.load(f)

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

@pytest.mark.parametrize("case", test_cases)
def test_intent_and_entities(case, intent_service, mock_query_llm, mock_update_user_state):
    # Mock the LLM response based on the test case
    mock_response = {
        "intent": case["expected_intent"],
        "entities": case.get("expected_entities", {}),
        "missing_entities": [],
        "next_question": ""
    }
    mock_query_llm.return_value = json.dumps(mock_response)

    result = intent_service.process_message("test_user", [], case["input"])

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    assert result["intent"] == case["expected_intent"], (
        f"Intent mismatch:\nExpected: {case['expected_intent']}\nGot: {result['intent']}"
    )

    if "expected_entities" in case:
        for key, value in case["expected_entities"].items():
            actual_value = result.get("entities", {}).get(key)
            assert actual_value == value, (
                f"Entity mismatch for '{key}':\nExpected: {value}\nGot: {actual_value}"
            )

    mock_update_user_state.assert_called_once()
