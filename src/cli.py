import readline
import os
from pathlib import Path
from typing import List, Callable, Optional
from functools import wraps
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.theme import Theme

custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "command": "bold blue",
    "prompt": "bold magenta",
})

console = Console(theme=custom_theme)


class TabCompleter:
    def __init__(self):
        self.commands = {
            'help': [],
            'exit': [],
            'quit': [],
            'analyze': ['project', 'class', 'dependencies'],
            'generate': ['test', 'code', 'documentation'],
            'build': [],
            'test': [],
            'list': ['classes', 'methods', 'fields', 'dependencies'],
            'add': ['import', 'method', 'field'],
            'remove': ['import', 'method', 'field'],
            'git': ['status', 'log', 'diff', 'add', 'commit'],
        }
        self.path_completion = True

    def complete(self, text: str, state: int) -> Optional[str]:
        if state == 0:
            parts = text.split()
            if len(parts) == 1:
                matches = [cmd for cmd in self.commands.keys() if cmd.startswith(text)]
                self.matches = matches
            elif len(parts) == 2 and parts[0] in self.commands:
                matches = [f"{parts[0]} {arg}" for arg in self.commands[parts[0]] 
                          if arg.startswith(parts[1])]
                self.matches = matches
            elif self.path_completion and (len(parts) == 2 and parts[0] in ['analyze', 'open']):
                directory = os.path.dirname(parts[1]) or '.'
                prefix = os.path.basename(parts[1])
                try:
                    files = os.listdir(directory)
                    matches = [f"{parts[0]} {os.path.join(directory, f)}" 
                              for f in files if f.startswith(prefix)]
                    self.matches = matches
                except:
                    self.matches = []
            else:
                self.matches = []
        
        if state < len(self.matches):
            return self.matches[state]
        return None


class EnhancedCLI:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.console = Console(theme=custom_theme)
        self.completer = TabCompleter()
        self.setup_readline()
        self.history_file = Path.home() / ".agent_history"
        self.load_history()

    def setup_readline(self):
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.completer.complete)
        readline.set_completer_delims(' \t\n')

    def load_history(self):
        if self.history_file.exists():
            readline.read_history_file(str(self.history_file))

    def save_history(self):
        readline.write_history_file(str(self.history_file))

    def print_header(self):
        self.console.print("\n[bold cyan]╔════════════════════════════════════════════════════════╗[/bold cyan]")
        self.console.print("[bold cyan]║     LangGraph + Ollama Java Test Generator           ║[/bold cyan]")
        self.console.print("[bold cyan]╚════════════════════════════════════════════════════════╝[/bold cyan]\n")
        self.console.print(f"[info]Project:[/info] [bold]{self.project_path.absolute()}[/bold]\n")
        self.print_help()

    def print_help(self):
        help_text = """
[bold cyan]Available Commands:[/bold cyan]
  [command]analyze <path>[/command]   - Analyze a project or file
  [command]generate test[/command]     - Generate tests for classes
  [command]build[/command]              - Run Maven build
  [command]test[/command]               - Run Maven tests
  [command]list classes[/command]      - List all Java classes
  [command]list methods[/command]       - List methods in a class
  [command]git status[/command]         - Show git status
  [command]git log[/command]            - Show git history
  [command]help[/command]               - Show this help message
  [command]exit[/command]               - Exit the application
        """
        self.console.print(help_text)

    def print_prompt(self) -> str:
        return self.console.input("[prompt]Agent>[/prompt] ")

    def print_info(self, message: str):
        self.console.print(f"[info]ℹ[/info] {message}")

    def print_success(self, message: str):
        self.console.print(f"[success]✓[/success] {message}")

    def print_warning(self, message: str):
        self.console.print(f"[warning]⚠[/warning] {message}")

    def print_error(self, message: str):
        self.console.print(f"[error]✗[/error] {message}")

    def print_assistant(self, message: str):
        self.console.print(f"[bold cyan]Assistant:[/bold cyan] {message}")

    def print_command(self, command: str):
        self.console.print(f"[command]>[/command] {command}")

    def with_progress(self, description: str):
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TimeRemainingColumn(),
                    console=self.console,
                ) as progress:
                    task = progress.add_task(description, total=None)
                    try:
                        result = func(*args, **kwargs)
                        progress.update(task, completed=True)
                        return result
                    except Exception as e:
                        progress.update(task, completed=True)
                        self.print_error(f"Operation failed: {str(e)}")
                        raise
            return wrapper
        return decorator

    def show_progress_bar(self, description: str, total: int = None):
        class ProgressBar:
            def __init__(self, cli, description, total):
                self.cli = cli
                self.progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    console=cli.console,
                )
                self.task = None
                self.description = description
                self.total = total

            def __enter__(self):
                self.progress.start()
                self.task = self.progress.add_task(self.description, total=self.total)
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.progress.stop()

            def update(self, advance: int = 1):
                if self.task is not None:
                    self.progress.update(self.task, advance=advance)

            def set_total(self, total: int):
                if self.task is not None:
                    self.progress.update(self.task, total=total)

        return ProgressBar(self, description, total)

    def get_multiline_input(self, prompt: str = "") -> str:
        lines = []
        while True:
            line = self.console.input(f"[prompt]{prompt}[/prompt] " if prompt else "[prompt]...[/prompt] ")
            if line == ".":
                break
            lines.append(line)
        return "\n".join(lines)

    def confirm(self, message: str) -> bool:
        response = self.console.input(f"[prompt]{message} [y/N]:[/prompt] ").lower()
        return response in ['y', 'yes']

    def select_option(self, options: List[str], prompt: str = "Select an option:") -> int:
        for i, option in enumerate(options, 1):
            self.console.print(f"  [cyan]{i}.[/cyan] {option}")
        while True:
            try:
                choice = self.console.input(f"[prompt]{prompt}[/prompt] ")
                index = int(choice) - 1
                if 0 <= index < len(options):
                    return index
                self.print_warning("Invalid selection, try again")
            except ValueError:
                self.print_warning("Please enter a number")

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_separator(self, char: str = "=", length: int = 50):
        self.console.print(char * length)

    def print_table(self, headers: List[str], rows: List[List[str]]):
        from rich.table import Table
        table = Table(title="")
        for header in headers:
            table.add_column(header, style="cyan")
        for row in rows:
            table.add_row(*row)
        self.console.print(table)

    def print_code(self, code: str, language: str = "python"):
        from rich.syntax import Syntax
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.console.print(syntax)
