import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from langchain_core.tools import tool
from ..exceptions.handler import FileOperationError, ValidationError, create_error_response
from ..utils.validation import validate_not_empty, validate_path
from .state_manager import get_state_manager


@tool
def save_state_to_file(state: Dict[str, Any], file_path: str) -> str:
    """Save ProjectState to a JSON file."""
    try:
        validate_not_empty(file_path, "file_path")
        
        state_copy = {
            "saved_at": datetime.now().isoformat(),
            "version": "1.0",
            "state": state
        }
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state_copy, indent=2, default=str), encoding="utf-8")
        
        return f"Successfully saved state to '{file_path}'"
    except Exception as e:
        response = create_error_response(e)
        return f"Error saving state: {response['errors'][0]}"


@tool
def load_state_from_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load ProjectState from a JSON file."""
    try:
        validate_file_exists(file_path)
        
        path = Path(file_path)
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
        
        if "state" not in data:
            raise FileOperationError("Invalid state file format", file_path)
        
        if data.get("version") != "1.0":
            raise FileOperationError(f"Unsupported state version: {data.get('version')}", file_path)
        
        return data["state"]
    except Exception as e:
        return None


@tool
def save_current_state(project_path: str) -> str:
    """Save current state from StateManager to a file."""
    try:
        validate_directory_exists(project_path)
        
        state_manager = get_state_manager()
        state = state_manager.get_state()
        
        if not state:
            return "No state loaded to save"
        
        state_file = Path(project_path) / ".project_state.json"
        return save_state_to_file(state, str(state_file))
    except Exception as e:
        response = create_error_response(e)
        return f"Error saving current state: {response['errors'][0]}"


@tool
def load_saved_state(project_path: str) -> Optional[Dict[str, Any]]:
    """Load saved state for a project."""
    try:
        validate_directory_exists(project_path)
        
        state_file = Path(project_path) / ".project_state.json"
        return load_state_from_file(str(state_file))
    except Exception as e:
        return None


@tool
def compare_with_saved_state(project_path: str) -> str:
    """Compare current state with saved state and return diff."""
    try:
        validate_directory_exists(project_path)
        
        state_manager = get_state_manager()
        current_state = state_manager.get_state()
        saved_state = load_saved_state(project_path)
        
        if not current_state:
            return "No current state to compare"
        
        if not saved_state:
            return "No saved state found"
        
        from .state_diff import diff_states, format_diff_report
        report = diff_states(saved_state, current_state)
        
        return format_diff_report(report)
    except Exception as e:
        response = create_error_response(e)
        return f"Error comparing states: {response['errors'][0]}"


@tool
def detect_state_drift(project_path: str) -> str:
    """Detect drift between filesystem and saved state."""
    try:
        validate_directory_exists(project_path)
        
        state_manager = get_state_manager()
        current_state = state_manager.get_state()
        
        if not current_state:
            return "No state loaded to detect drift"
        
        saved_state = load_saved_state(project_path)
        
        if not saved_state:
            return "No saved state to compare"
        
        from .state_diff import diff_states
        report = diff_states(saved_state, current_state)
        
        if report.summary['modified'] > 0:
            return "State drift detected:\n" + format_diff_report(report)
        else:
            return "No state drift detected"
    except Exception as e:
        response = create_error_response(e)
        return f"Error detecting drift: {response['errors'][0]}"


@tool
def export_state_as_json(state: Dict[str, Any], file_path: str, pretty: bool = True) -> str:
    """Export state as JSON file with optional pretty formatting."""
    try:
        validate_not_empty(file_path, "file_path")
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if pretty:
            content = json.dumps(state, indent=2, default=str, ensure_ascii=False)
        else:
            content = json.dumps(state, separators=(',', ':'), default=str)
        
        path.write_text(content, encoding="utf-8")
        
        return f"Successfully exported state to '{file_path}'"
    except Exception as e:
        response = create_error_response(e)
        return f"Error exporting state: {response['errors'][0]}"


@tool
def import_state_from_json(file_path: str) -> Optional[Dict[str, Any]]:
    """Import state from JSON file (flexible, ignores version)."""
    try:
        validate_file_exists(file_path)
        
        path = Path(file_path)
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
        
        if "state" in data:
            return data["state"]
        else:
            return data
    except Exception as e:
        return None


@tool
def list_saved_states(project_path: str) -> str:
    """List all saved state files for a project."""
    try:
        validate_directory_exists(project_path)
        
        project_dir = Path(project_path)
        state_files = list(project_dir.glob("*.state.json"))
        
        if not state_files:
            return "No saved state files found"
        
        results = ["Saved state files:"]
        for i, state_file in enumerate(state_files, 1):
            try:
                data = json.loads(state_file.read_text(encoding="utf-8"))
                saved_at = data.get('saved_at', 'Unknown')
                version = data.get('version', 'Unknown')
                results.append(f"{i}. {state_file.name} (Saved: {saved_at}, Version: {version})")
            except:
                results.append(f"{i}. {state_file.name} (Unable to read)")
        
        return "\n".join(results)
    except Exception as e:
        response = create_error_response(e)
        return f"Error listing states: {response['errors'][0]}"


@tool
def create_state_backup(project_path: str, backup_suffix: Optional[str] = None) -> str:
    """Create a timestamped backup of current state."""
    try:
        validate_directory_exists(project_path)
        
        state_manager = get_state_manager()
        state = state_manager.get_state()
        
        if not state:
            return "No state to backup"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"_{backup_suffix}" if backup_suffix else ""
        backup_file = Path(project_path) / f".project_state_backup{suffix}.json"
        
        return save_state_to_file(state, str(backup_file))
    except Exception as e:
        response = create_error_response(e)
        return f"Error creating backup: {response['errors'][0]}"
