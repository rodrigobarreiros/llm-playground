import unittest
from app.intent_engine import process_message
from app.state_store import clear_user_state

class TestIntentEngine(unittest.TestCase):

    def test_basic_intent_extraction(self):
        user_id = "test_user_1"
        history = []
        user_input = "Quero transferir 500 para João"

        result = process_message(user_id, history, user_input)

        if "error" in result:
            self.fail(f"Erro no processamento: {result['error']}")

        self.assertEqual(result["intent"], "transfer")
        self.assertIn("amount", result["entities"])
        self.assertIn("recipient", result["entities"])

    def test_get_balance(self):
        user_id = "test_user_2"
        history = []
        user_input = "Qual é o meu saldo?"

        result = process_message(user_id, history, user_input)

        if "error" in result:
            self.fail(f"Erro no processamento: {result['error']}")

        self.assertEqual(result["intent"], "get_balance")
