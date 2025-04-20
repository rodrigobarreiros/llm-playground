import json
import pytest
from app.intent_engine import process_message
from app.state_store import clear_user_state

with open("tests/resources/dialogs.json", encoding="utf-8") as f:
    dialogs = json.load(f)

@pytest.mark.parametrize("case_index, case", list(enumerate(dialogs)))
def test_intent_and_entities(case_index, case):
    user_id = f"test_case_{case_index}"
    history = []
    result = process_message(user_id, history, case["input"])

    assert "error" not in result, f"Erro no caso {case_index}: {result.get('error')}"

    assert result["intent"] == case["expected_intent"], f"Intent mismatch on case {case_index}"

    for key, value in case["expected_entities"].items():
        assert result["entities"].get(key) == value, f"Entity '{key}' mismatch on case {case_index}"

    clear_user_state(user_id)
