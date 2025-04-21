from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text
from typing import Callable

class ConsoleUI:
    def __init__(self, assistant_name: str, user_name: str):
        self.assistant_name = assistant_name
        self.user_name = user_name
        self.console = Console()

    def print_assistant(self, message: str) -> None:
        """Print a message from the assistant."""
        self.console.print(f"[bold cyan]{self.assistant_name}[/bold cyan] ➤ {message}")

    def get_user_input(self) -> str:
        """Get input from the user."""
        return Prompt.ask(f"[bold green]{self.user_name}[/bold green] ➤").strip()

    def print_info(self, message: str) -> None:
        """Print an informational message."""
        self.console.print(f"[dim]{message}[/dim]")

    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        self.console.print(f"[bold yellow][AVISO][/bold yellow] {message}")

    def print_error(self, message: str) -> None:
        """Print an error message."""
        self.console.print(f"[bold red][ERRO][/bold red] {message}")

    def start_conversation(self, process_message: Callable[[str], tuple[bool, str | None, str | None]]) -> None:
        """Start the conversation loop."""
        self.console.print()
        self.print_assistant(f"Olá {self.user_name}, como posso te ajudar hoje? (Digite 'sair' para encerrar)")

        try:
            while True:
                msg = self.get_user_input()
                should_continue, msg_type, message = process_message(msg)
                
                if message:
                    if msg_type == "error":
                        self.print_error(message)
                    elif msg_type == "warning":
                        self.print_warning(message)
                    elif msg_type == "transfer_confirmation":
                        self.print_assistant(message)
                    else:
                        self.print_assistant(message)
                
                if not should_continue:
                    break
        except KeyboardInterrupt:
            self.print_assistant(f"Até logo, {self.user_name}!")
