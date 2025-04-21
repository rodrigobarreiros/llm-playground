import json
import pytest
from app.domain.intent_service import process_message
from app.domain.state_repository import clear_user_state

# Load scenarios from external JSON file
with open("tests/resources/multi_turn_scenarios.json", encoding="utf-8") as f:
    scenarios = json.load(f)

@pytest.mark.parametrize("scenario", scenarios)
def test_conversational_flow(scenario):
    user_id = f"scenario_{scenario['name'].replace(' ', '_')}"
    history = []

    for i, step in enumerate(scenario["steps"]):
        result = process_message(user_id, history, step["input"])

        assert "error" not in result, f"Unexpected error at step {i}: {result.get('error')}"

        if "expect_intent" in step:
            assert result["intent"] == step["expect_intent"], (
                f"Wrong intent at step {i} in scenario '{scenario['name']}':\n"
                f"Expected: {step['expect_intent']}\nGot: {result['intent']}"
            )

        if "expect_entities" in step:
            for key, value in step["expect_entities"].items():
                actual_value = result.get("entities", {}).get(key)
                assert actual_value == value, (
                    f"Wrong entity '{key}' at step {i} in scenario '{scenario['name']}':\n"
                    f"Expected: {value}\nGot: {actual_value} | {result.get('entities', {})}"
                )

        history.append(f"User: {step['input']}")

    clear_user_state(user_id)
