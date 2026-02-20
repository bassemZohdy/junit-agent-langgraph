import copy
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from .state_manager import StateManager, get_state_manager


@dataclass
class DiffChange:
    """Represents a single change in state."""
    change_type: str  # "added", "removed", "modified"
    component: str  # e.g., "java_classes", "fields", "methods"
    identifier: str  # e.g., class name, field name
    old_value: Optional[Any]
    new_value: Optional[Any]
    details: Optional[str] = None


@dataclass
class DiffReport:
    """Comprehensive diff report between two states."""
    timestamp: str
    state1_hash: str
    state2_hash: str
    changes: List[DiffChange]
    summary: Dict[str, int]


def calculate_state_hash(state: Dict[str, Any]) -> str:
    """Calculate a hash of the state for comparison."""
    import hashlib
    import json
    
    state_copy = copy.deepcopy(state)
    
    state_copy.pop('messages', None)
    state_copy.pop('last_action', None)
    state_copy.pop('summary_report', None)
    state_copy.pop('retry_count', None)
    
    state_str = json.dumps(state_copy, sort_keys=True, default=str)
    return hashlib.sha256(state_str.encode()).hexdigest()


def diff_states(state1: Dict[str, Any], state2: Dict[str, Any]) -> DiffReport:
    """Compare two ProjectState objects and generate diff report."""
    timestamp = datetime.now().isoformat()
    hash1 = calculate_state_hash(state1)
    hash2 = calculate_state_hash(state2)
    
    changes: List[DiffChange] = []
    summary = {
        "added": 0,
        "removed": 0,
        "modified": 0
        "classes_changed": 0,
        "fields_changed": 0,
        "methods_changed": 0
    }
    
    classes1 = {c['name']: c for c in state1.get('java_classes', [])}
    classes2 = {c['name']: c for c in state2.get('java_classes', [])}
    
    class_names1 = set(classes1.keys())
    class_names2 = set(classes2.keys())
    
    for class_name in class_names1 - class_names2:
        class_data = classes1[class_name]
        changes.append(DiffChange(
            change_type="removed",
            component="java_classes",
            identifier=class_name,
            old_value=class_data,
            new_value=None,
            details=f"Class {class_name} removed"
        ))
        summary["removed"] += 1
        summary["classes_changed"] += 1
    
    for class_name in class_names2 - class_names1:
        class_data = classes2[class_name]
        changes.append(DiffChange(
            change_type="added",
            component="java_classes",
            identifier=class_name,
            old_value=None,
            new_value=class_data,
            details=f"Class {class_name} added"
        ))
        summary["added"] += 1
        summary["classes_changed"] += 1
    
    for class_name in class_names1 & class_names2:
        class1 = classes1[class_name]
        class2 = classes2[class_name]
        
        if class1 != class2:
            fields1 = {f['name']: f for f in class1.get('fields', [])}
            fields2 = {f['name']: f for f in class2.get('fields', [])}
            
            field_names1 = set(fields1.keys())
            field_names2 = set(fields2.keys())
            
            for field_name in field_names1 - field_names2:
                changes.append(DiffChange(
                    change_type="removed",
                    component="fields",
                    identifier=f"{class_name}.{field_name}",
                    old_value=fields1[field_name],
                    new_value=None,
                    details=f"Field {field_name} removed from class {class_name}"
                ))
                summary["removed"] += 1
                summary["fields_changed"] += 1
            
            for field_name in field_names2 - field_names1:
                changes.append(DiffChange(
                    change_type="added",
                    component="fields",
                    identifier=f"{class_name}.{field_name}",
                    old_value=None,
                    new_value=fields2[field_name],
                    details=f"Field {field_name} added to class {class_name}"
                ))
                summary["added"] += 1
                summary["fields_changed"] += 1
            
            for field_name in field_names1 & field_names2:
                field1 = fields1[field_name]
                field2 = fields2[field_name]
                
                if field1 != field2:
                    changes.append(DiffChange(
                        change_type="modified",
                        component="fields",
                        identifier=f"{class_name}.{field_name}",
                        old_value=field1,
                        new_value=field2,
                        details=f"Field {field_name} modified in class {class_name}"
                    ))
                    summary["modified"] += 1
                    summary["fields_changed"] += 1
            
            methods1 = {m['name']: m for m in class1.get('methods', [])}
            methods2 = {m['name']: m for m in class2.get('methods', [])}
            
            method_names1 = set(methods1.keys())
            method_names2 = set(methods2.keys())
            
            for method_name in method_names1 - method_names2:
                changes.append(DiffChange(
                    change_type="removed",
                    component="methods",
                    identifier=f"{class_name}.{method_name}",
                    old_value=methods1[method_name],
                    new_value=None,
                    details=f"Method {method_name} removed from class {class_name}"
                ))
                summary["removed"] += 1
                summary["methods_changed"] += 1
            
            for method_name in method_names2 - method_names1:
                changes.append(DiffChange(
                    change_type="added",
                    component="methods",
                    identifier=f"{class_name}.{method_name}",
                    old_value=None,
                    new_value=methods2[method_name],
                    details=f"Method {method_name} added to class {class_name}"
                ))
                summary["added"] += 1
                summary["methods_changed"] += 1
            
            for method_name in method_names1 & method_names2:
                method1 = methods1[method_name]
                method2 = methods2[method_name]
                
                if method1 != method2:
                    changes.append(DiffChange(
                        change_type="modified",
                        component="methods",
                        identifier=f"{class_name}.{method_name}",
                        old_value=method1,
                        new_value=method2,
                        details=f"Method {method_name} modified in class {class_name}"
                    ))
                    summary["modified"] += 1
                    summary["methods_changed"] += 1
    
    build_status1 = state1.get('build_status', {})
    build_status2 = state2.get('build_status', {})
    
    if build_status1.get('build_status') != build_status2.get('build_status'):
        changes.append(DiffChange(
            change_type="modified",
            component="build_status",
            identifier="build_status.build_status",
            old_value=build_status1,
            new_value=build_status2,
            details=f"Build status changed from {build_status1.get('build_status')} to {build_status2.get('build_status')}"
        ))
        summary["modified"] += 1
    
    return DiffReport(
        timestamp=timestamp,
        state1_hash=hash1,
        state2_hash=hash2,
        changes=changes,
        summary=summary
    )


def format_diff_report(report: DiffReport) -> str:
    """Format diff report as readable text."""
    lines = [
        "=" * 80,
        f"STATE DIFF REPORT",
        f"Timestamp: {report.timestamp}",
        f"State 1 Hash: {report.state1_hash}",
        f"State 2 Hash: {report.state2_hash}",
        "=" * 80,
        f"",
        f"SUMMARY:",
        f"  Changes: {len(report.changes)}",
        f"  Added: {report.summary['added']}",
        f"  Removed: {report.summary['removed']}",
        f"  Modified: {report.summary['modified']}",
        f"  Classes Changed: {report.summary['classes_changed']}",
        f"  Fields Changed: {report.summary['fields_changed']}",
        f"  Methods Changed: {report.summary['methods_changed']}",
        f"",
        "=" * 80,
        f"CHANGES:",
        f""
    ]
    
    for i, change in enumerate(report.changes, 1):
        lines.append(f"{i}. [{change.change_type.upper()}] {change.component}: {change.identifier}")
        if change.details:
            lines.append(f"   {change.details}")
        if change.old_value is not None:
            lines.append(f"   Old: {change.old_value}")
        if change.new_value is not None:
            lines.append(f"   New: {change.new_value}")
        lines.append("")
    
    lines.append("=" * 80)
    
    return "\n".join(lines)


def export_diff_report(report: DiffReport, file_path: str) -> None:
    """Export diff report to a file."""
    try:
        content = format_diff_report(report)
        Path(file_path).write_text(content, encoding="utf-8")
    except Exception as e:
        from .exceptions.handler import FileOperationError
        raise FileOperationError(f"Failed to export diff report: {str(e)}", file_path)
