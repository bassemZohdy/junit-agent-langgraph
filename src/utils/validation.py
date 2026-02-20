import os
import re
from pathlib import Path
from typing import Optional, List, Any, Union
from ..exceptions.handler import ValidationError, FileOperationError
from .security import SecurityUtils


def validate_not_none(value: Any, field_name: str) -> None:
    """Validate that a value is not None."""
    if value is None:
        raise ValidationError(f"Field '{field_name}' cannot be None", field_name)


def validate_not_empty(value: str, field_name: str) -> None:
    """Validate that a string is not empty."""
    validate_not_none(value, field_name)
    if not value.strip():
        raise ValidationError(f"Field '{field_name}' cannot be empty", field_name)


def validate_path(path: Union[str, Path], field_name: str = "path") -> Path:
    """Validate and return a Path object."""
    if isinstance(path, Path):
        path_str = str(path)
    else:
        path_str = path
    
    validate_not_none(path_str, field_name)
    validate_not_empty(path_str, field_name)
    
    path_obj = Path(path_str)
    return path_obj


def validate_file_exists(file_path: Union[str, Path]) -> Path:
    """Validate that a file exists and return its Path object."""
    if isinstance(file_path, Path):
        path_str = str(file_path)
    else:
        path_str = file_path
    
    path_obj = validate_path(path_str, "file_path")
    
    if not path_obj.exists():
        raise FileOperationError(f"File '{file_path}' does not exist", str(path_obj))
    
    if not path_obj.is_file():
        raise FileOperationError(f"Path '{file_path}' is not a file", str(path_obj))
    
    return path_obj


def validate_directory_exists(directory_path: Union[str, Path]) -> Path:
    """Validate that a directory exists and return its Path object."""
    if isinstance(directory_path, Path):
        dir_str = str(directory_path)
    else:
        dir_str = directory_path
    
    path_obj = validate_path(dir_str, "directory_path")
    
    if not path_obj.exists():
        raise FileOperationError(f"Directory '{directory_path}' does not exist", str(path_obj))
    
    if not path_obj.is_dir():
        raise FileOperationError(f"Path '{directory_path}' is not a directory", str(path_obj))
    
    return path_obj


def validate_file_extension(file_path: Union[str, Path], allowed_extensions: List[str]) -> None:
    """Validate that a file has one of the allowed extensions."""
    path_obj = Path(file_path)
    extension = path_obj.suffix.lower()
    
    if extension not in allowed_extensions:
        raise ValidationError(
            f"File '{file_path}' has invalid extension '{extension}'. "
            f"Allowed extensions: {', '.join(allowed_extensions)}",
            "file_path"
        )


def validate_java_file(file_path: Union[str, Path]) -> Path:
    """Validate that a path is a Java source file."""
    validate_file_extension(file_path, [".java"])
    return validate_file_exists(file_path)


def validate_pom_xml(file_path: Union[str, Path]) -> Path:
    """Validate that a path is a pom.xml file."""
    path_obj = Path(file_path)
    if path_obj.name != "pom.xml":
        raise ValidationError(f"File must be named 'pom.xml', got '{path_obj.name}'", "file_path")
    return validate_file_exists(file_path)


def validate_project_directory(project_path: Union[str, Path]) -> Path:
    """Validate that a path is a valid project directory (either has pom.xml or is a valid directory)."""
    path_obj = validate_directory_exists(project_path)
    
    pom_xml = path_obj / "pom.xml"
    if not pom_xml.exists():
        raise FileOperationError(
            f"Project directory '{project_path}' must contain a pom.xml file",
            str(path_obj)
        )
    
    return path_obj


def sanitize_path(path: str, allow_traversal: bool = False, allow_absolute: bool = False) -> str:
    """
    Sanitize a file path to prevent path traversal attacks.
    
    Args:
        path: The path to sanitize
        allow_traversal: Whether to allow parent directory references (..)
        allow_absolute: Whether to allow absolute paths
    
    Returns:
        Sanitized path
    
    Raises:
        ValidationError: If path traversal detected and not allowed
    """
    return SecurityUtils.sanitize_path(path, allow_absolute=allow_absolute)


def validate_in_allowed_values(value: Any, field_name: str, allowed_values: List[Any]) -> None:
    """Validate that a value is one of the allowed values."""
    validate_not_none(value, field_name)
    
    if value not in allowed_values:
        raise ValidationError(
            f"Field '{field_name}' must be one of: {', '.join(map(str, allowed_values))}, "
            f"got '{value}'",
            field_name
        )


def validate_range(value: Union[int, float], field_name: str, min_val: Optional[Union[int, float]] = None, max_val: Optional[Union[int, float]] = None) -> None:
    """Validate that a numeric value is within the specified range."""
    validate_not_none(value, field_name)
    
    if min_val is not None and value < min_val:
        raise ValidationError(
            f"Field '{field_name}' must be >= {min_val}, got {value}",
            field_name
        )
    
    if max_val is not None and value > max_val:
        raise ValidationError(
            f"Field '{field_name}' must be <= {max_val}, got {value}",
            field_name
        )


def validate_class_name(class_name: str) -> None:
    """Validate that a string is a valid Java class name."""
    validate_not_empty(class_name, "class_name")
    
    pattern = r'^[A-Z][a-zA-Z0-9_]*$'
    if not re.match(pattern, class_name):
        raise ValidationError(
            f"Invalid Java class name '{class_name}'. Class names must start with uppercase letter "
            f"and contain only alphanumeric characters and underscores.",
            "class_name"
        )


def validate_package_name(package_name: str) -> None:
    """Validate that a string is a valid Java package name."""
    validate_not_empty(package_name, "package_name")
    
    pattern = r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$'
    if not re.match(pattern, package_name):
        raise ValidationError(
            f"Invalid Java package name '{package_name}'. Package names must be lowercase and "
            f"follow reverse domain notation (e.g., com.example.package)",
            "package_name"
        )


def validate_method_name(method_name: str) -> None:
    """Validate that a string is a valid Java method name."""
    validate_not_empty(method_name, "method_name")
    
    pattern = r'^[a-z][a-zA-Z0-9_]*$'
    if not re.match(pattern, method_name):
        raise ValidationError(
            f"Invalid Java method name '{method_name}'. Method names must start with lowercase letter "
            f"and contain only alphanumeric characters and underscores.",
            "method_name"
        )


def validate_field_name(field_name: str) -> None:
    """Validate that a string is a valid Java field name."""
    validate_not_empty(field_name, "field_name")
    
    pattern = r'^[a-z][a-zA-Z0-9_]*$'
    if not re.match(pattern, field_name):
        raise ValidationError(
            f"Invalid Java field name '{field_name}'. Field names must start with lowercase letter "
            f"and contain only alphanumeric characters and underscores.",
            "field_name"
        )


def validate_maven_goal(goal: str) -> None:
    """Validate that a string is a valid Maven goal."""
    validate_not_empty(goal, "goal")
    
    valid_goals = [
        "compile", "test", "package", "install", "deploy",
        "clean", "validate", "verify", "site",
        "dependency:tree", "dependency:list", "dependency:analyze",
        "help:effective-pom", "help:describe"
    ]
    
    goal_parts = goal.split(":")
    if len(goal_parts) > 1:
        prefix = goal_parts[0]
        if prefix not in ["dependency", "help", "exec", "surefire", "failsafe"]:
            raise ValidationError(
                f"Invalid Maven goal prefix '{prefix}'. Valid prefixes: dependency, help, exec, surefire, failsafe",
                "goal"
            )
    else:
        if goal not in ["compile", "test", "package", "install", "deploy", "clean", "validate", "verify", "site"]:
            raise ValidationError(
                f"Invalid Maven goal '{goal}'. Valid goals: {', '.join(valid_goals)}",
                "goal"
            )


def validate_maven_scope(scope: str) -> None:
    """Validate that a string is a valid Maven scope."""
    validate_not_empty(scope, "scope")
    
    valid_scopes = ["compile", "test", "provided", "runtime", "system", "import"]
    validate_in_allowed_values(scope, "scope", valid_scopes)


def validate_list_not_empty(items: List[Any], field_name: str) -> None:
    """Validate that a list is not empty."""
    validate_not_none(items, field_name)
    
    if not items:
        raise ValidationError(f"List '{field_name}' cannot be empty", field_name)


def validate_list_max_length(items: List[Any], field_name: str, max_length: int) -> None:
    """Validate that a list does not exceed maximum length."""
    validate_not_none(items, field_name)
    
    if len(items) > max_length:
        raise ValidationError(
            f"List '{field_name}' exceeds maximum length of {max_length}, got {len(items)}",
            field_name
        )


def validate_content_not_empty(content: str) -> None:
    """Validate that content string is not just whitespace."""
    validate_not_none(content, "content")
    
    if not content or not content.strip():
        raise ValidationError("Content cannot be empty or whitespace only", "content")


def validate_positive_integer(value: int, field_name: str) -> None:
    """Validate that a value is a positive integer."""
    validate_not_none(value, field_name)
    
    if not isinstance(value, int) or value <= 0:
        raise ValidationError(
            f"Field '{field_name}' must be a positive integer, got {value}",
            field_name
        )


def validate_non_negative_integer(value: int, field_name: str) -> None:
    """Validate that a value is a non-negative integer."""
    validate_not_none(value, field_name)
    
    if not isinstance(value, int) or value < 0:
        raise ValidationError(
            f"Field '{field_name}' must be a non-negative integer, got {value}",
            field_name
        )


def validate_annotation_name(annotation_name: str) -> None:
    """Validate that a string is a valid Java annotation name."""
    validate_not_empty(annotation_name, "annotation_name")
    
    pattern = r'^@[A-Z][a-zA-Z0-9_]*$'
    if not re.match(pattern, annotation_name):
        raise ValidationError(
            f"Invalid Java annotation name '{annotation_name}'. Annotation names must start with @ "
            f"followed by uppercase letter and contain only alphanumeric characters and underscores.",
            "annotation_name"
        )


def validate_import_statement(import_statement: str) -> None:
    """Validate that a string is a valid Java import statement."""
    validate_not_empty(import_statement, "import_statement")
    
    pattern = r'^(import\s+static\s+|import\s+)[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z0-9_]+)*\.(?:\*|[A-Z][a-zA-Z0-9_]*)\s*;$'
    if not re.match(pattern, import_statement):
        raise ValidationError(
            f"Invalid Java import statement '{import_statement}'. Must follow pattern: "
            f"'import package.Class;' or 'import static package.Class.method;'",
            "import_statement"
        )


def validate_modifier(modifier: str) -> None:
    """Validate that a string is a valid Java modifier."""
    validate_not_empty(modifier, "modifier")
    
    valid_modifiers = [
        "public", "private", "protected",
        "static", "final", "abstract", "synchronized",
        "volatile", "transient", "native", "strictfp"
    ]
    validate_in_allowed_values(modifier, "modifier", valid_modifiers)
