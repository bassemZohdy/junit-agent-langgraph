import sys
import argparse
from pathlib import Path
from typing import List, Optional
from langchain_core.tools import tool
from ..exceptions.handler import FileOperationError, ValidationError, create_error_response
from ..utils.validation import validate_file_exists, validate_directory_exists


@tool
def interactive_select(items: List[str], prompt: str = "Select an option") -> Optional[str]:
    """Interactive selection from a list of options."""
    try:
        if not sys.stdin.isatty():
            return None
        
        print(f"\n{prompt}:")
        for i, item in enumerate(items, 1):
            print(f"  {i}. {item}")
        
        while True:
            try:
                choice = input("\n> ").strip()
                if choice.lower() == 'q':
                    return None
                choice_num = int(choice)
                if 1 <= choice_num <= len(items):
                    return items[choice_num - 1]
                print(f"Invalid choice. Please enter 1-{len(items)} or 'q' to quit.")
            except ValueError:
                print(f"Invalid input. Please enter a number or 'q' to quit.")
            except KeyboardInterrupt:
                print("\nSelection cancelled")
                return None
    except Exception as e:
        response = create_error_response(e)
        return f"Error in selection: {response['errors'][0]}"


@tool
def confirm_action(action_description: str, default: bool = False) -> bool:
    """Ask user to confirm an action."""
    try:
        if not sys.stdin.isatty():
            return default
        
        prompt = f"\n{action_description} (y/n/q): "
        while True:
            choice = input(prompt).strip().lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            elif choice == 'q':
                return False
            else:
                print("Please enter 'y', 'n', or 'q'")
    except KeyboardInterrupt:
        print("\nAction cancelled")
        return False
    except Exception as e:
        response = create_error_response(e)
        print(f"Error: {response['errors'][0]}")
        return False


@tool
def select_file_interactive(directory_path: str, file_pattern: str = "*.java") -> Optional[str]:
    """Interactive file selection from directory."""
    try:
        validate_directory_exists(directory_path)
        
        project_dir = Path(directory_path)
        files = list(project_dir.rglob(file_pattern))
        
        if not files:
            print(f"No files found matching '{file_pattern}' in '{directory_path}'")
            return None
        
        relative_files = [str(f.relative_to(project_dir)) for f in files]
        
        return interactive_select(relative_files, "Select a file")
    except Exception as e:
        response = create_error_response(e)
        print(f"Error selecting file: {response['errors'][0]}")
        return None


@tool
def get_cli_history(history_size: int = 50) -> List[str]:
    """Get command history (simulated)."""
    try:
        history_file = Path.home() / ".agent_cli_history"
        if history_file.exists():
            lines = history_file.read_text(encoding="utf-8").split('\n')
            return lines[-history_size:]
        return []
    except Exception:
        return []


@tool
def show_progress_bar(current: int, total: int, width: int = 50, prefix: str = "") -> None:
    """Display a simple progress bar."""
    if total <= 0:
        return None
    
    if not prefix:
        prefix = "Progress:"
    
    percent = current / total
    filled = int(width * percent)
    bar = '=' * filled + '-' * (width - filled)
    
    print(f"\r{prefix} [{bar}] {current}/{total} ({percent:.1%})", end='', flush=True)


@tool
def color_output(text: str, color: str = "white") -> str:
    """Color output for terminal (basic implementation)."""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    
    reset_code = '\033[0m'
    
    if color not in colors:
        color = 'white'
    
    return f"{colors[color]}{text}{reset_code}"


@tool
def print_success(message: str) -> None:
    """Print success message in green."""
    print(color_output(f"✓ {message}", 'green'))


@tool
def print_error(message: str) -> None:
    """Print error message in red."""
    print(color_output(f"✗ {message}", 'red'))


@tool
 print_warning(message: str) -> None:
    """Print warning message in yellow."""
    print(color_output(f"⚠ {message}", 'yellow'))


@tool
def print_info(message: str) -> None:
    """Print info message in blue."""
    print(color_output(f"ℹ {message}", 'blue'))


def print_header(message: str) -> None:
    """Print section header in cyan with underline."""
    print("\n" + color_output(message, 'cyan'))
    print(color_output("=" * len(message), 'cyan') + "\n")


def print_subheader(message: str) -> None:
    """Print subsection header in magenta."""
    print("\n" + color_output(message, 'magenta') + "\n")


def clear_screen() -> None:
    """Clear the terminal screen."""
    import os
    os.system('cls' if sys.platform == 'win32' else 'clear')


def add_to_history(command: str) -> None:
    """Add command to history file."""
    try:
        history_file = Path.home() / ".agent_cli_history"
        history_file.touch(exist_ok=True)
        
        with open(history_file, 'a', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines or lines[-1].strip() != command:
                f.write(command + '\n')
    except Exception:
        pass


def create_cli_parser():
    """Create main CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="LangGraph + Ollama Java Test Generation Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'project-path',
        help='Path to Java project directory'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Enable interactive mode'
    )
    
    parser.add_argument(
        '--read-only',
        action='store_true',
        help='Run in read-only mode'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run (no actual changes)'
    )
    
    return parser
