from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

console = Console()

def print_assistant(name, message):
    console.print(f"[bold cyan]{name}[/bold cyan] ➤ {message}")

def print_user(name):
    return Prompt.ask(f"[bold green]{name}[/bold green] ➤")

def print_info(message):
    console.print(f"[dim]{message}[/dim]")

def print_warning(message):
    console.print(f"[bold yellow][AVISO][/bold yellow] {message}")

def print_error(message):
    console.print(f"[bold red][ERRO][/bold red] {message}")
