import json
import pytest
from app.domain.intent_engine import process_message
from app.infrastructure.persistence.state_store import clear_user_state

// ... existing code ... 