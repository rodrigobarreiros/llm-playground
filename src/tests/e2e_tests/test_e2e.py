import json
import pytest
from app.domain.intent_service import IntentService
from app.domain.state_repository import get_user_state, clear_user_state

# Load scenarios from external JSON file
with open("tests/resources/multi_turn_scenarios.json", encoding="utf-8") as f:
    scenarios = json.load(f)

@pytest.fixture
def intent_service():
    return IntentService()

@pytest.mark.parametrize("scenario", scenarios)
def test_conversational_flow(intent_service, scenario):
    user_id = f"scenario_{scenario['name'].replace(' ', '_')}"
    history = []

    for i, step in enumerate(scenario["steps"]):
        # Process the message
        result = intent_service.process_message(user_id, history, step["input"])
        
        # Get the updated state
        state = get_user_state(user_id)
        
        assert "error" not in result, f"Unexpected error at step {i}: {result.get('error')}"

        if "expect_intent" in step:
            assert state["intent"] == step["expect_intent"], (
                f"Wrong intent at step {i} in scenario '{scenario['name']}':\n"
                f"Expected: {step['expect_intent']}\nGot: {state['intent']}"
            )

        if "expect_entities" in step:
            for key, value in step["expect_entities"].items():
                actual_value = state.get("entities", {}).get(key)
                assert actual_value == value, (
                    f"Wrong entity '{key}' at step {i} in scenario '{scenario['name']}':\n"
                    f"Expected: {value}\nGot: {actual_value}"
                )

        # Add the message to history
        history.append(f"User: {step['input']}")

    # Clean up
    clear_user_state(user_id)
    