# state_store.py

# In-memory dictionary to track state per user
state = {}

def get_user_state(user_id):
    """
    Initializes and returns the user's state if it doesn't exist.
    """
    if user_id not in state:
        state[user_id] = {
            "intent": None,
            "entities": {},
            "missing": [],
            "next_question": None
        }
    return state[user_id]

def update_user_state(user_id, updates):
    """
    Updates the user's state with the provided values.
    """
    user_state = get_user_state(user_id)
    user_state.update(updates)

def clear_user_state(user_id):
    """
    Removes the user's state from memory.
    """
    if user_id in state:
        del state[user_id]
