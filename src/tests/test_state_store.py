import unittest
from app.state_store import get_user_state, update_user_state, clear_user_state

class TestStateStore(unittest.TestCase):

    def test_state_initialization(self):
        user_id = "test_user"
        state = get_user_state(user_id)
        self.assertIn("intent", state)
        clear_user_state(user_id)

    def test_state_update(self):
        user_id = "test_user"
        update_user_state(user_id, {"intent": "make_transfer"})
        state = get_user_state(user_id)
        self.assertEqual(state["intent"], "make_transfer")
        clear_user_state(user_id)
