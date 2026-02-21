from pathlib import Path
from langchain_core.tools import tool
from ..exceptions.handler import FileOperationError, create_error_response
from ..utils.validation import (
    validate_file_exists,
    validate_directory_exists,
    validate_not_empty,
    validate_content_not_empty
)

def read_file_func(file_path: str) -> str:
    """Read contents of a file at the specified path."""
    try:
        path = validate_file_exists(file_path)
        return path.read_text(encoding="utf-8")
    except FileOperationError as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error reading file: {response['errors'][0]}"


def write_file_func(file_path: str, content: str) -> str:
    """Write content to a file at the specified path."""
    try:
        validate_not_empty(file_path, "file_path")
        validate_content_not_empty(content)

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Successfully wrote to '{file_path}'"
    except FileOperationError as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error writing file: {response['errors'][0]}"


def list_files_func(directory_path: str, pattern: str = "*") -> str:
    """List files in a directory matching the given pattern."""
    try:
        validate_not_empty(directory_path, "directory_path")
        validate_not_empty(pattern, "pattern")

        path = validate_directory_exists(directory_path)

        files = [str(f.relative_to(path)) for f in path.rglob(pattern) if f.is_file()]
        return "\n".join(files) if files else "No files found"
    except FileOperationError as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error listing files: {response['errors'][0]}"


def list_directories_func(directory_path: str) -> str:
    """List all directories in the specified path."""
    try:
        path = validate_directory_exists(directory_path)

        dirs = [str(d.relative_to(path)) for d in path.iterdir() if d.is_dir()]
        return "\n".join(dirs) if dirs else "No directories found"
    except FileOperationError as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error listing directories: {response['errors'][0]}"


def delete_file_func(file_path: str) -> str:
    """Delete a file at the specified path."""
    try:
        path = validate_file_exists(file_path)
        path.unlink()
        return f"Successfully deleted '{file_path}'"
    except FileOperationError as e:
        return str(e)
    except Exception as e:
        response = create_error_response(e)
        return f"Error deleting file: {response['errors'][0]}"

read_file = tool(read_file_func)
write_file = tool(write_file_func)
list_files = tool(list_files_func)
list_directories = tool(list_directories_func)
delete_file = tool(delete_file_func)

file_tools = [read_file, write_file, list_files, list_directories, delete_file]

__all__ = [
    'read_file', 'read_file_func',
    'write_file', 'write_file_func',
    'list_files', 'list_files_func',
    'list_directories', 'list_directories_func',
    'delete_file', 'delete_file_func'
]
