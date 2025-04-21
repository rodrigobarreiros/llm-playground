import json
import pytest
from app.domain.intent_service import process_message
from app.domain.state_repository import clear_user_state

# Load test cases from external JSON file
with open("tests/resources/dialogs.json", encoding="utf-8") as f:
    test_cases = json.load(f)

@pytest.mark.parametrize("case", test_cases)
def test_intent_and_entities(case):
    result = process_message("test_user", [], case["input"])

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

    clear_user_state("test_user")
