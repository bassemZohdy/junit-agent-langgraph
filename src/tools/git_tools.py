import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from langchain_core.tools import tool
from ..exceptions.handler import FileOperationError, ValidationError, create_error_response
from ..utils.validation import validate_file_exists, validate_directory_exists, validate_not_empty


@tool
def git_status(project_path: str) -> str:
    """Get git status of the project."""
    try:
        validate_directory_exists(project_path)
        
        result = subprocess.run(
            ["git", "status"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return f"Git status error: {result.stderr}"
        
        return result.stdout if result.stdout else "No changes"
    except Exception as e:
        response = create_error_response(e)
        return f"Error getting git status: {response['errors'][0]}"


@tool
def git_log(project_path: str, limit: int = 10) -> str:
    """Get git commit history."""
    try:
        validate_directory_exists(project_path)
        
        result = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%h - %an - %ar - %s"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return f"Git log error: {result.stderr}"
        
        return result.stdout if result.stdout else "No commits"
    except Exception as e:
        response = create_error_response(e)
        return f"Error getting git log: {response['errors'][0]}"


@tool
def git_diff(project_path: str, file_path: Optional[str] = None) -> str:
    """Show git diff for project or specific file."""
    try:
        validate_directory_exists(project_path)
        
        command = ["git", "diff"]
        if file_path:
            command.append(file_path)
        
        result = subprocess.run(
            command,
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return f"Git diff error: {result.stderr}"
        
        return result.stdout if result.stdout else "No differences"
    except Exception as e:
        response = create_error_response(e)
        return f"Error getting git diff: {response['errors'][0]}"


@tool
def git_file_history(project_path: str, file_path: str, limit: int = 5) -> str:
    """Show modification history for a specific file."""
    try:
        validate_directory_exists(project_path)
        validate_file_exists(file_path)
        
        relative_path = str(Path(file_path).relative_to(project_path))
        
        result = subprocess.run(
            ["git", "log", f"-{limit}", "--pretty=format:%h - %an - %ar - %s", "--", relative_path],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return f"Git file history error: {result.stderr}"
        
        return result.stdout if result.stdout else "No history for this file"
    except Exception as e:
        response = create_error_response(e)
        return f"Error getting file history: {response['errors'][0]}"


@tool
def git_branch(project_path: str) -> str:
    """Get current git branch."""
    try:
        validate_directory_exists(project_path)
        
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return f"Git branch error: {result.stderr}"
        
        return result.stdout.strip() if result.stdout else "Unknown branch"
    except Exception as e:
        response = create_error_response(e)
        return f"Error getting git branch: {response['errors'][0]}"


@tool
def git_add(project_path: str, file_path: str) -> str:
    """Add file to git staging area."""
    try:
        validate_directory_exists(project_path)
        validate_file_exists(file_path)
        
        relative_path = str(Path(file_path).relative_to(project_path))
        
        result = subprocess.run(
            ["git", "add", relative_path],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return f"Git add error: {result.stderr}"
        
        return f"Added {file_path} to staging area"
    except Exception as e:
        response = create_error_response(e)
        return f"Error adding file to git: {response['errors'][0]}"


@tool
def git_commit(project_path: str, message: str) -> str:
    """Create git commit with message."""
    try:
        validate_directory_exists(project_path)
        validate_not_empty(message, "message")
        
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return f"Git commit error: {result.stderr}"
        
        return f"Commit created successfully"
    except Exception as e:
        response = create_error_response(e)
        return f"Error creating commit: {response['errors'][0]}"


@tool
def generate_commit_message(project_path: str) -> str:
    """Generate a git commit message based on staged changes."""
    try:
        validate_directory_exists(project_path)
        
        result = subprocess.run(
            ["git", "diff", "--staged", "--name-status"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return f"Error getting staged changes: {result.stderr}"
        
        if not result.stdout:
            return "No staged changes"
        
        lines = result.stdout.strip().split('\n')
        changes = []
        
        for line in lines:
            if not line:
                continue
            parts = line.split('\t')
            if len(parts) >= 2:
                status, file = parts[0], parts[1]
                changes.append(f"{status}: {file}")
        
        if not changes:
            return "No staged changes"
        
        num_changes = len(changes)
        
        message_parts = [
            f"Update: {num_changes} file{'s' if num_changes > 1 else ''}"
            "",
            "Changes:"
        ]
        message_parts.extend([f"- {change}" for change in changes])
        
        return "\n".join(message_parts)
    except Exception as e:
        response = create_error_response(e)
        return f"Error generating commit message: {response['errors'][0]}"


@tool
def git_is_repository(project_path: str) -> bool:
    """Check if directory is a git repository."""
    try:
        path = Path(project_path)
        if not path.exists():
            return False
        
        git_dir = path / ".git"
        return git_dir.exists() and git_dir.is_dir()
    except Exception:
        return False


git_tools = [
    git_status,
    git_log,
    git_diff,
    git_file_history,
    git_branch,
    git_add,
    git_commit,
    generate_commit_message,
    git_is_repository
]
