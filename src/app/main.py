import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.domain.user_session import UserSession
from app.domain.default_entity_manager import DefaultEntityManager
from app.application.intent_handler import IntentHandler
from app.application.conversation_manager import ConversationManager
from app.ui.console import ConsoleUI

def main():
    # Configuration
    assistant_name = "Magie"
    user_id = "rodrigo.barreiros"
    user_name = "Rodrigo"
    user_account_number = "000123"  # Default known account

    # Initialize components
    user_session = UserSession(
        user_id=user_id,
        user_name=user_name,
        account_number=user_account_number,
        history=[]
    )
    default_entity_manager = DefaultEntityManager(user_account_number)
    transaction_handler = IntentHandler(user_id, user_name, assistant_name)
    conversation_manager = ConversationManager(
        user_session=user_session,
        default_entity_manager=default_entity_manager,
        transaction_handler=transaction_handler,
        assistant_name=assistant_name
    )

    # Initialize UI and start conversation
    console_ui = ConsoleUI(assistant_name, user_name)
    console_ui.start_conversation(conversation_manager.process_message)

if __name__ == "__main__":
    main()
    