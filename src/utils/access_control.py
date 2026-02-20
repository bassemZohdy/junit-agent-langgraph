import os
import stat
from pathlib import Path
from typing import Optional, List, Set, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import threading
import json

from ..exceptions.handler import FileOperationError, ValidationError


class AccessLevel(Enum):
    """Access levels for file operations."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"


@dataclass
class AccessControlEntry:
    """Represents an access control decision."""
    path: str
    operation: str
    allowed: bool
    reason: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    user: Optional[str] = None


@dataclass
class AuditLogEntry:
    """Represents an audit log entry."""
    timestamp: datetime
    operation: str
    path: str
    success: bool
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class AccessControlManager:
    """Manages access control for file operations."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._project_root: Optional[Path] = None
        self._allowed_paths: Set[Path] = set()
        self._restricted_paths: Set[Path] = set()
        self._read_only_mode: bool = False
        self._audit_log: List[AuditLogEntry] = []
        self._max_audit_entries = 1000
        
    def set_project_root(self, project_root: str) -> None:
        """Set the project root directory. All operations must be within this directory."""
        with self._lock:
            self._project_root = Path(project_root).resolve()
            self._allowed_paths.add(self._project_root)
    
    def get_project_root(self) -> Optional[Path]:
        """Get the current project root directory."""
        with self._lock:
            return self._project_root
    
    def add_allowed_path(self, path: str) -> None:
        """Add a path to the allowed paths list."""
        with self._lock:
            self._allowed_paths.add(Path(path).resolve())
    
    def add_restricted_path(self, path: str) -> None:
        """Add a path to the restricted paths list."""
        with self._lock:
            self._restricted_paths.add(Path(path).resolve())
    
    def set_read_only_mode(self, read_only: bool) -> None:
        """Set whether operations are read-only."""
        with self._lock:
            self._read_only_mode = read_only
    
    def is_read_only_mode(self) -> bool:
        """Check if read-only mode is enabled."""
        with self._lock:
            return self._read_only_mode
    
    def check_permission(self, path: str, operation: AccessLevel) -> AccessControlEntry:
        """
        Check if an operation on a path is allowed.
        
        Args:
            path: The path to check
            operation: The type of operation
        
        Returns:
            AccessControlEntry with the decision
        """
        with self._lock:
            path_obj = Path(path).resolve()
            
            try:
                operation_str = operation.value
                
                if not self._project_root:
                    return AccessControlEntry(
                        path=str(path_obj),
                        operation=operation_str,
                        allowed=False,
                        reason="No project root configured"
                    )
                
                if not path_obj.is_relative_to(self._project_root):
                    return AccessControlEntry(
                        path=str(path_obj),
                        operation=operation_str,
                        allowed=False,
                        reason=f"Path is outside project root: {self._project_root}"
                    )
                
                for restricted in self._restricted_paths:
                    if path_obj.is_relative_to(restricted) or path_obj == restricted:
                        return AccessControlEntry(
                            path=str(path_obj),
                            operation=operation_str,
                            allowed=False,
                            reason=f"Path is in restricted directory: {restricted}"
                        )
                
                if self._read_only_mode and operation in [AccessLevel.WRITE, AccessLevel.DELETE]:
                    return AccessControlEntry(
                        path=str(path_obj),
                        operation=operation_str,
                        allowed=False,
                        reason="Read-only mode is enabled"
                    )
                
                if path_obj.exists():
                    file_stat = path_obj.stat()
                    mode = file_stat.st_mode
                    
                    if operation == AccessLevel.READ:
                        if not os.access(path_obj, os.R_OK):
                            return AccessControlEntry(
                                path=str(path_obj),
                                operation=operation_str,
                                allowed=False,
                                reason="File is not readable"
                            )
                    elif operation == AccessLevel.WRITE:
                        if not os.access(path_obj, os.W_OK):
                            return AccessControlEntry(
                                path=str(path_obj),
                                operation=operation_str,
                                allowed=False,
                                reason="File is not writable"
                            )
                    elif operation == AccessLevel.DELETE:
                        if not os.access(path_obj, os.W_OK):
                            return AccessControlEntry(
                                path=str(path_obj),
                                operation=operation_str,
                                allowed=False,
                                reason="File is not writable (cannot delete)"
                            )
                    elif operation == AccessLevel.EXECUTE:
                        if not os.access(path_obj, os.X_OK):
                            return AccessControlEntry(
                                path=str(path_obj),
                                operation=operation_str,
                                allowed=False,
                                reason="File is not executable"
                            )
                
                return AccessControlEntry(
                    path=str(path_obj),
                    operation=operation_str,
                    allowed=True
                )
                
            except Exception as e:
                return AccessControlEntry(
                    path=str(path_obj),
                    operation=operation.value,
                    allowed=False,
                    reason=f"Error checking permission: {str(e)}"
                )
    
    def ensure_access(self, path: str, operation: AccessLevel) -> None:
        """
        Ensure access is allowed, raising an exception if not.
        
        Args:
            path: The path to check
            operation: The type of operation
        
        Raises:
            FileOperationError: If access is not allowed
        """
        entry = self.check_permission(path, operation)
        
        if not entry.allowed:
            raise FileOperationError(
                f"Access denied for {operation.value} on '{path}': {entry.reason}",
                path
            )
    
    def log_operation(
        self,
        operation: str,
        path: str,
        success: bool,
        error: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an operation for auditing."""
        with self._lock:
            entry = AuditLogEntry(
                timestamp=datetime.now(),
                operation=operation,
                path=path,
                success=success,
                error=error,
                details=details or {}
            )
            self._audit_log.append(entry)
            
            if len(self._audit_log) > self._max_audit_entries:
                self._audit_log.pop(0)
    
    def get_audit_log(
        self,
        limit: Optional[int] = None,
        operation: Optional[str] = None,
        path_filter: Optional[str] = None
    ) -> List[AuditLogEntry]:
        """Get audit log entries, optionally filtered."""
        with self._lock:
            entries = self._audit_log
            
            if operation:
                entries = [e for e in entries if e.operation == operation]
            
            if path_filter:
                entries = [e for e in entries if path_filter in e.path]
            
            if limit:
                entries = entries[-limit:]
            
            return entries.copy()
    
    def clear_audit_log(self) -> None:
        """Clear the audit log."""
        with self._lock:
            self._audit_log.clear()
    
    def export_audit_log(self, file_path: str) -> None:
        """Export audit log to a file."""
        with self._lock:
            entries = [
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "operation": entry.operation,
                    "path": entry.path,
                    "success": entry.success,
                    "error": entry.error,
                    "details": entry.details
                }
                for entry in self._audit_log
            ]
            
            Path(file_path).write_text(json.dumps(entries, indent=2), encoding="utf-8")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get access control statistics."""
        with self._lock:
            total_operations = len(self._audit_log)
            successful_operations = sum(1 for e in self._audit_log if e.success)
            failed_operations = total_operations - successful_operations
            
            operation_counts = {}
            for entry in self._audit_log:
                operation_counts[entry.operation] = operation_counts.get(entry.operation, 0) + 1
            
            return {
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "failed_operations": failed_operations,
                "success_rate": successful_operations / total_operations if total_operations > 0 else 0,
                "operation_counts": operation_counts,
                "read_only_mode": self._read_only_mode,
                "project_root": str(self._project_root) if self._project_root else None,
                "allowed_paths_count": len(self._allowed_paths),
                "restricted_paths_count": len(self._restricted_paths)
            }


_global_access_control: Optional[AccessControlManager] = None
_access_control_lock = threading.Lock()


def get_access_control_manager() -> AccessControlManager:
    """Get the global access control manager instance."""
    global _global_access_control
    
    with _access_control_lock:
        if _global_access_control is None:
            _global_access_control = AccessControlManager()
    
    return _global_access_control


def reset_access_control_manager() -> None:
    """Reset the global access control manager (mainly for testing)."""
    global _global_access_control
    
    with _access_control_lock:
        _global_access_control = None
