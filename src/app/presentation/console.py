from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.theme import Theme

class ConsoleUI:
    def __init__(self):
        self.console = Console(theme=Theme({
            "info": "cyan",
            "warning": "yellow",
            "error": "red",
            "success": "green",
            "assistant": "blue",
            "user": "magenta"
        }))

    def print_message(self, message: str, message_type: str = "info"):
        """Print a message with appropriate styling."""
        if message_type == "error":
            self.console.print(Panel(message, title="Erro", border_style="red"))
        elif message_type == "success":
            self.console.print(Panel(message, title="Sucesso", border_style="green"))
        elif message_type == "warning":
            self.console.print(Panel(message, title="Aviso", border_style="yellow"))
        else:
            self.console.print(Panel(message, title="Informação", border_style="cyan"))

    def get_user_input(self, prompt: str = "> ") -> str:
        """Get input from the user."""
        return Prompt.ask(prompt)

    def clear_screen(self):
        """Clear the console screen."""
        self.console.clear() 