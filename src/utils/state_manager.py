import os
import threading
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import copy
import hashlib
import json

from ..exceptions.handler import ValidationError, create_error_response
from ..states.project import ProjectState, JavaClassState


def _make_serializable(state: Dict[str, Any]) -> Dict[str, Any]:
    """Convert non-serializable objects in state to serializable form.

    Specifically handles LangChain BaseMessage objects that contain model_dump() method.
    """
    state_copy = copy.deepcopy(state)
    if "messages" in state_copy:
        state_copy["messages"] = [
            msg.model_dump() if hasattr(msg, 'model_dump') else str(msg)
            for msg in state_copy.get("messages", [])
        ]
    return state_copy


@dataclass
class StateSnapshot:
    """A snapshot of state at a specific point in time."""
    timestamp: datetime
    state_data: Dict[str, Any]
    checksum: str
    operation: str
    
    def __post_init__(self):
        if not self.checksum:
            state_str = json.dumps(self.state_data, sort_keys=True)
            self.checksum = hashlib.sha256(state_str.encode()).hexdigest()


@dataclass
class StateTransaction:
    """Represents a state transaction for rollback."""
    operation: str
    before_snapshot: StateSnapshot
    after_snapshot: Optional[StateSnapshot] = None
    success: bool = False
    error: Optional[str] = None


class StateManager:
    """Manages state consistency with validation, rollback, and concurrency control."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._current_state: Optional[ProjectState] = None
        self._snapshots: List[StateSnapshot] = []
        self._transactions: List[StateTransaction] = []
        self._max_snapshots = 10
        
    def get_state(self) -> Optional[ProjectState]:
        """Get current state."""
        with self._lock:
            return copy.deepcopy(self._current_state) if self._current_state else None
    
    def set_state(self, state: ProjectState) -> None:
        """Set current state with validation."""
        with self._lock:
            self._validate_state(state)
            self._current_state = copy.deepcopy(state)
            self._create_snapshot("set_state")
    
    def validate_state(self, state: ProjectState) -> bool:
        """Validate state without locking (internal use)."""
        try:
            self._validate_state(state)
            return True
        except ValidationError:
            return False
    
    def _validate_state(self, state: ProjectState) -> None:
        """Validate state structure and content."""
        if not state:
            raise ValidationError("State cannot be None", "state")
        
        if not isinstance(state, dict):
            raise ValidationError("State must be a dictionary", "state")
        
        required_fields = [
            "project_path", "project_name", "java_classes", 
            "test_classes", "dependencies", "build_status"
        ]
        
        for field in required_fields:
            if field not in state:
                raise ValidationError(f"State missing required field: {field}", "state")
        
        if "java_classes" in state and state["java_classes"]:
            for idx, java_class in enumerate(state["java_classes"]):
                self._validate_java_class_state(java_class, f"java_classes[{idx}]")
    
    def _validate_java_class_state(self, java_class: JavaClassState, path: str) -> None:
        """Validate Java class state."""
        if not isinstance(java_class, dict):
            raise ValidationError(f"{path} must be a dictionary", path)
        
        required_fields = ["name", "file_path", "fields", "methods", "imports"]
        for field in required_fields:
            if field not in java_class:
                raise ValidationError(f"{path} missing required field: {field}", path)
        
        if not java_class.get("file_path"):
            raise ValidationError(f"{path} cannot have empty file_path", f"{path}.file_path")
        
        if java_class.get("fields") and not isinstance(java_class["fields"], list):
            raise ValidationError(f"{path}.fields must be a list", f"{path}.fields")
        
        if java_class.get("methods") and not isinstance(java_class["methods"], list):
            raise ValidationError(f"{path}.methods must be a list", f"{path}.methods")
        
        if java_class.get("imports") and not isinstance(java_class["imports"], list):
            raise ValidationError(f"{path}.imports must be a list", f"{path}.imports")
    
    def begin_transaction(self, operation: str) -> StateTransaction:
        """Begin a new transaction for state modifications."""
        with self._lock:
            snapshot = self._create_snapshot(operation)
            transaction = StateTransaction(
                operation=operation,
                before_snapshot=snapshot,
                after_snapshot=None,
                success=False
            )
            return transaction
    
    def commit_transaction(self, transaction: StateTransaction) -> None:
        """Commit a transaction, recording the after snapshot."""
        with self._lock:
            after_snapshot = self._create_snapshot(transaction.operation)
            transaction.after_snapshot = after_snapshot
            transaction.success = True
            self._transactions.append(transaction)
    
    def rollback_transaction(self, transaction: StateTransaction, error: Optional[str] = None) -> None:
        """Rollback a transaction to the before snapshot."""
        with self._lock:
            if transaction.before_snapshot:
                self._current_state = copy.deepcopy(transaction.before_snapshot.state_data)
                transaction.success = False
                transaction.error = error
                self._transactions.append(transaction)
                
                if len(self._snapshots) > 1:
                    self._snapshots.pop()
    
    def _create_snapshot(self, operation: str) -> StateSnapshot:
        """Create a snapshot of the current state."""
        if self._current_state:
            state_data = _make_serializable(self._current_state)
            state_str = json.dumps(state_data, sort_keys=True)
            checksum = hashlib.sha256(state_str.encode()).hexdigest()
            
            snapshot = StateSnapshot(
                timestamp=datetime.now(),
                state_data=state_data,
                checksum=checksum,
                operation=operation
            )
            
            self._snapshots.append(snapshot)
            
            if len(self._snapshots) > self._max_snapshots:
                self._snapshots.pop(0)
            
            return snapshot
        else:
            return StateSnapshot(
                timestamp=datetime.now(),
                state_data={},
                checksum="",
                operation=operation
            )
    
    def get_snapshot(self, index: int = -1) -> Optional[StateSnapshot]:
        """Get a snapshot by index (default: most recent)."""
        with self._lock:
            if not self._snapshots:
                return None
            try:
                return copy.deepcopy(self._snapshots[index])
            except IndexError:
                return None
    
    def get_snapshots_since(self, timestamp: datetime) -> List[StateSnapshot]:
        """Get all snapshots since a given timestamp."""
        with self._lock:
            return [s for s in self._snapshots if s.timestamp >= timestamp]
    
    def get_transaction_history(self, limit: int = 10) -> List[StateTransaction]:
        """Get recent transaction history."""
        with self._lock:
            return copy.deepcopy(self._transactions[-limit:])
    
    def execute_with_rollback(
        self, 
        operation: str, 
        func: Callable[[], Any],
        on_error: Optional[Callable[[Exception], None]] = None
    ) -> Any:
        """Execute a function with automatic rollback on error."""
        transaction = self.begin_transaction(operation)
        
        try:
            result = func()
            self.commit_transaction(transaction)
            return result
        except Exception as e:
            error_msg = str(e)
            self.rollback_transaction(transaction, error_msg)
            
            if on_error:
                on_error(e)
            
            raise e
    
    def sync_state_with_filesystem(self, project_path: str) -> ProjectState:
        """Sync state with filesystem by re-reading all files."""
        with self._lock:
            from ..tools.maven_tools import create_project_state
            
            transaction = self.begin_transaction("sync_with_filesystem")
            
            try:
                new_state = create_project_state(project_path)
                if isinstance(new_state, dict):
                    self.set_state(new_state)
                    self.commit_transaction(transaction)
                    return new_state
                else:
                    error_msg = "create_project_state did not return a dictionary"
                    self.rollback_transaction(transaction, error_msg)
                    raise ValidationError(error_msg, "state")
            except Exception as e:
                self.rollback_transaction(transaction, str(e))
                raise e
    
    def verify_state_consistency(self) -> Dict[str, Any]:
        """Verify that state matches the filesystem."""
        with self._lock:
            if not self._current_state:
                return {"consistent": False, "error": "No state loaded"}
            
            issues = []
            warnings = []
            
            project_path = self._current_state.get("project_path")
            if not project_path:
                return {"consistent": False, "error": "No project path in state"}
            
            project_dir = Path(project_path)
            if not project_dir.exists():
                issues.append(f"Project directory does not exist: {project_path}")
                return {"consistent": False, "issues": issues, "warnings": warnings}
            
            java_classes = self._current_state.get("java_classes", [])
            for java_class in java_classes:
                file_path = java_class.get("file_path")
                if file_path:
                    if not Path(file_path).exists():
                        issues.append(f"Java file in state not found on filesystem: {file_path}")
                    else:
                        current_mtime = Path(file_path).stat().st_mtime
                        expected_mtime = java_class.get("last_modified")
                        if expected_mtime and abs(current_mtime - expected_mtime) > 1:
                            warnings.append(f"File modified since state was cached: {file_path}")
            
            return {
                "consistent": len(issues) == 0,
                "issues": issues,
                "warnings": warnings
            }
    
    def invalidate_class_state(self, class_name: str) -> None:
        """Invalidate cached state for a specific class."""
        with self._lock:
            if not self._current_state:
                return
            
            java_classes = self._current_state.get("java_classes", [])
            for java_class in java_classes:
                if java_class.get("name") == class_name:
                    java_class["status"] = "stale"
                    break
    
    def clear_state(self) -> None:
        """Clear all state and snapshots."""
        with self._lock:
            self._current_state = None
            self._snapshots.clear()
            self._transactions.clear()
    
    def reset(self) -> None:
        """Reset state manager to initial state (alias for clear_state)."""
        self.clear_state()


_global_state_manager: Optional[StateManager] = None
_state_lock = threading.Lock()


def get_state_manager() -> StateManager:
    """Get the global state manager instance."""
    global _global_state_manager
    
    with _state_lock:
        if _global_state_manager is None:
            _global_state_manager = StateManager()
    
    return _global_state_manager


def reset_state_manager() -> None:
    """Reset the global state manager (mainly for testing)."""
    global _global_state_manager
    
    with _state_lock:
        if _global_state_manager:
            _global_state_manager.clear_state()
        _global_state_manager = None
