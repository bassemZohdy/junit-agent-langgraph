# API Documentation

## Table of Contents

- [Overview](#overview)
- [State Objects](#state-objects)
- [Tools Reference](#tools-reference)
  - [File Tools](#file-tools)
  - [Java Tools](#java-tools)
  - [Maven Tools](#maven-tools)
  - [Maven Dependency Analysis Tools](#maven-dependency-analysis-tools)
  - [Code Generation Tools](#code-generation-tools)
  - [Git Tools](#git-tools)
  - [Code Quality Tools](#code-quality-tools)
  - [Project Operations Tools](#project-operations-tools)
- [Utilities](#utilities)
- [Workflow](#workflow)

---

## Overview

This LangGraph + Ollama application provides a comprehensive toolkit for analyzing, testing, and managing Java projects. The API is organized around three main concepts:

1. **State Objects**: Immutable data structures representing project state
2. **Tools**: Functions that operate on files and projects
3. **Utilities**: Helper modules for validation, security, state management, and more

---

## State Objects

### ProjectState

Represents the entire project state throughout the workflow.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `messages` | `List[BaseMessage]` | Conversation message history (LangGraph annotation) |
| `project_path` | `str` | Absolute path to the project directory |
| `project_name` | `str` | Name of the project (derived from directory) |
| `packaging_type` | `str` | Maven packaging type (jar, war, etc.) |
| `version` | `str` | Project version |
| `description` | `Optional[str]` | Project description |
| `java_classes` | `List[JavaClassState]` | List of all Java classes in the project |
| `test_classes` | `List[TestClassState]` | List of all test classes |
| `current_class` | `Optional[JavaClassState]` | Currently processing class |
| `maven_group_id` | `str` | Maven groupId |
| `maven_artifact_id` | `str` | Maven artifactId |
| `dependencies` | `List[MavenDependencyState]` | Direct dependencies |
| `test_dependencies` | `List[MavenDependencyState]` | Test dependencies |
| `transitive_dependencies` | `List[MavenDependencyState]` | All transitive dependencies |
| `dependency_graph` | `dict` | Dependency relationships graph |
| `plugins` | `List[MavenPluginState]` | Maven plugins |
| `build_status` | `MavenBuildState` | Current build status |
| `last_action` | `str` | Last performed action |
| `summary_report` | `Optional[str]` | Final validation summary |
| `source_directory` | `str` | Main source directory path |
| `test_directory` | `str` | Test source directory path |
| `output_directory` | `str` | Build output directory |
| `has_spring` | `bool` | Whether Spring Boot is detected |
| `has_junit` | `bool` | Whether JUnit is detected |
| `has_mockito` | `bool` | Whether Mockito is detected |
| `retry_count` | `int` | Current retry count for test generation |
| `max_retries` | `int` | Maximum allowed retries |
| `test_results` | `dict` | Test execution results |
| `all_tests_passed` | `bool` | Overall test pass status |

### JavaClassState

Represents a single Java class with full metadata.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Class name |
| `file_path` | `str` | Path to the Java source file |
| `package` | `Optional[str]` | Package declaration |
| `content` | `Optional[str]` | File content |
| `type` | `str` | Class type (class, interface, enum, etc.) |
| `modifiers` | `List[str]` | Modifiers (public, private, static, etc.) |
| `extends` | `Optional[str]` | Superclass name |
| `implements` | `List[str]` | Implemented interfaces |
| `annotations` | `List[AnnotationState]` | Class annotations |
| `fields` | `List[FieldState]` | Class fields |
| `methods` | `List[MethodState]` | Class methods |
| `imports` | `List[ImportState]` | Import statements |
| `inner_classes` | `List[JavaClassState]` | Nested classes |
| `status` | `str` | Analysis/compilation status |
| `errors` | `List[str]` | Errors encountered |
| `line_number` | `Optional[int]` | Line number in source file |

### FieldState

Represents a class field.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Field name |
| `type` | `str` | Field type |
| `modifiers` | `List[str]` | Modifiers |
| `is_static` | `bool` | Whether static |
| `is_final` | `bool` | Whether final |
| `default_value` | `Optional[str]` | Default value |
| `annotations` | `List[AnnotationState]` | Field annotations |
| `line_number` | `Optional[int]` | Line number |

### MethodState

Represents a method.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Method name |
| `return_type` | `str` | Return type |
| `parameters` | `List[Dict[str, str]]` | Method parameters |
| `modifiers` | `List[str]` | Modifiers |
| `annotations` | `List[AnnotationState]` | Method annotations |
| `throws` | `List[str]` | Exceptions thrown |
| `body` | `Optional[str]` | Method body |
| `is_abstract` | `bool` | Whether abstract |
| `line_number` | `Optional[int]` | Line number |

### AnnotationState

Represents an annotation.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Annotation name |
| `elements` | `Dict[str, str]` | Annotation elements |
| `target` | `Optional[str]` | Annotation target |
| `line_number` | `Optional[int]` | Line number |

### ImportState

Represents an import statement.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Import name |
| `is_static` | `bool` | Whether static import |
| `is_wildcard` | `bool` | Whether wildcard import |
| `line_number` | `Optional[int]` | Line number |

### MavenDependencyState

Represents a Maven dependency.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `group_id` | `str` | Maven groupId |
| `artifact_id` | `str` | Maven artifactId |
| `version` | `str` | Dependency version |
| `type` | `str` | Dependency type (jar, war, etc.) |
| `scope` | `Optional[str]` | Dependency scope |
| `is_test` | `bool` | Whether test dependency |
| `dependencies` | `List[Dict]` | Transitive dependencies |

### MavenBuildState

Represents Maven build status.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `last_build_time` | `Optional[str]` | Last build timestamp |
| `build_status` | `str` | Build status (SUCCESS, FAILED, ERROR, RUNNING) |
| `build_duration` | `Optional[str]` | Build duration |
| `goals` | `List[str]` | Build goals executed |
| `output_directory` | `str` | Output directory |
| `test_results` | `Dict[str, str | bool]` | Test results |
| `compilation_errors` | `List[str]` | Compilation errors |

### TestClassState

Represents a test class.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Test class name |
| `file_path` | `str` | Path to test file |
| `package` | `Optional[str]` | Package declaration |
| `content` | `Optional[str]` | Test code content |
| `target_class` | `str` | Class being tested |
| `test_methods` | `List[MethodState]` | Test methods |
| `status` | `str` | Test status |
| `errors` | `List[str]` | Errors |
| `review_comments` | `List[str]` | Code review feedback |

---

## Tools Reference

### File Tools

#### `read_file(file_path: str) -> str`

Reads the contents of a file.

**Parameters:**
- `file_path` (str): Path to the file to read

**Returns:**
- `str`: File contents or error message

**Raises:**
- `FileOperationError`: If file doesn't exist or cannot be read

**Example:**
```python
content = read_file("/path/to/file.txt")
```

#### `write_file(file_path: str, content: str) -> str`

Writes content to a file, creating directories if needed.

**Parameters:**
- `file_path` (str): Path to the file to write
- `content` (str): Content to write

**Returns:**
- `str`: Success message or error message

**Raises:**
- `FileOperationError`: If file cannot be written

**Example:**
```python
result = write_file("/path/to/file.txt", "Hello, World!")
```

#### `list_files(directory: str, pattern: str = "*", recursive: bool = False) -> List[str]`

Lists files in a directory with optional pattern matching.

**Parameters:**
- `directory` (str): Directory to search
- `pattern` (str, optional): Glob pattern (default: "*")
- `recursive` (bool, optional): Search recursively (default: False)

**Returns:**
- `List[str]`: List of file paths

**Example:**
```python
java_files = list_files("/path/to/project", pattern="*.java", recursive=True)
```

#### `list_directories(directory: str, recursive: bool = False) -> List[str]`

Lists directories in a path.

**Parameters:**
- `directory` (str): Directory to search
- `recursive` (bool, optional): List recursively (default: False)

**Returns:**
- `List[str]`: List of directory paths

**Example:**
```python
dirs = list_directories("/path/to/project", recursive=True)
```

#### `delete_file(file_path: str) -> str`

Deletes a file.

**Parameters:**
- `file_path` (str): Path to the file to delete

**Returns:**
- `str`: Success message or error message

**Raises:**
- `FileOperationError`: If file cannot be deleted

**Example:**
```python
result = delete_file("/path/to/file.txt")
```

---

### Java Tools

#### `find_java_files(project_path: str) -> List[str]`

Finds all Java source files in a project.

**Parameters:**
- `project_path` (str): Path to the project directory

**Returns:**
- `List[str]`: List of Java file paths

**Example:**
```python
java_files = find_java_files("/path/to/project")
```

#### `create_java_class_state(file_path: str) -> JavaClassState`

Creates a complete JavaClassState from a Java file.

**Parameters:**
- `file_path` (str): Path to the Java file

**Returns:**
- `JavaClassState`: Complete class state with fields, methods, imports, annotations

**Example:**
```python
class_state = create_java_class_state("/path/to/User.java")
print(class_state["name"])  # User
```

#### `get_java_classes(project_path: str) -> List[Dict[str, Any]]`

Gets all classes declared in a Java project.

**Parameters:**
- `project_path` (str): Path to the project

**Returns:**
- `List[Dict[str, Any]]`: List of class information dictionaries

**Example:**
```python
classes = get_java_classes("/path/to/project")
for cls in classes:
    print(f"Class: {cls['name']}")
```

#### `get_java_methods(project_path: str, class_name: str = None) -> List[Dict[str, Any]]`

Gets all methods from a Java file or specific class.

**Parameters:**
- `project_path` (str): Path to the project or file
- `class_name` (str, optional): Specific class name

**Returns:**
- `List[Dict[str, Any]]`: List of method information

**Example:**
```python
methods = get_java_methods("/path/to/User.java")
for method in methods:
    print(f"Method: {method['name']}")
```

#### `add_import(file_path: str, import_statement: str, class_name: str) -> str`

Adds an import statement to a Java file.

**Parameters:**
- `file_path` (str): Path to the Java file
- `import_statement` (str): Import statement to add
- `class_name` (str): Name of the target class

**Returns:**
- `str`: Success message or error message

**Example:**
```python
result = add_import(
    "/path/to/User.java",
    "import java.util.List;",
    "User"
)
```

#### `add_field(file_path: str, class_name: str, field: Dict[str, Any]) -> str`

Adds a field to a specific class in a Java file.

**Parameters:**
- `file_path` (str): Path to the Java file
- `class_name` (str): Name of the target class
- `field` (Dict[str, Any]): Field definition

**Returns:**
- `str`: Success message or error message

**Example:**
```python
result = add_field(
    "/path/to/User.java",
    "User",
    {
        "name": "email",
        "type": "String",
        "modifiers": ["private"]
    }
)
```

---

### Maven Tools

#### `maven_build(project_path: str, goals: List[str] = ["package"]) -> Dict[str, Any]`

Runs Maven build with custom goals.

**Parameters:**
- `project_path` (str): Path to the Maven project
- `goals` (List[str], optional): Maven goals (default: ["package"])

**Returns:**
- `Dict[str, Any]`: Build result with status, output, and errors

**Example:**
```python
result = maven_build("/path/to/project", ["clean", "package"])
print(result["status"])  # SUCCESS or FAILED
```

#### `maven_test(project_path: str) -> Dict[str, Any]`

Runs Maven tests.

**Parameters:**
- `project_path` (str): Path to the Maven project

**Returns:**
- `Dict[str, Any]`: Test results

**Example:**
```python
result = maven_test("/path/to/project")
print(result["test_results"])
```

#### `maven_clean(project_path: str) -> Dict[str, Any]`

Cleans Maven build artifacts.

**Parameters:**
- `project_path` (str): Path to the Maven project

**Returns:**
- `Dict[str, Any]`: Clean result

**Example:**
```python
result = maven_clean("/path/to/project")
```

#### `maven_dependency_tree(project_path: str) -> str`

Shows Maven dependency tree.

**Parameters:**
- `project_path` (str): Path to the Maven project

**Returns:**
- `str`: Dependency tree output

**Example:**
```python
tree = maven_dependency_tree("/path/to/project")
print(tree)
```

#### `create_project_state(project_path: str) -> ProjectState`

Creates a complete ProjectState from a Maven project.

**Parameters:**
- `project_path` (str): Path to the Maven project

**Returns:**
- `ProjectState`: Complete project state

**Example:**
```python
state = create_project_state("/path/to/project")
print(state["maven_group_id"])
print(state["dependencies"])
```

---

### Maven Dependency Analysis Tools

#### `get_transitive_dependencies(project_path: str) -> List[MavenDependencyState]`

Gets all direct and indirect dependencies.

**Parameters:**
- `project_path` (str): Path to the Maven project

**Returns:**
- `List[MavenDependencyState]`: All dependencies including transitive

**Example:**
```python
deps = get_transitive_dependencies("/path/to/project")
for dep in deps:
    print(f"{dep['group_id']}:{dep['artifact_id']}:{dep['version']}")
```

#### `build_dependency_graph(project_path: str) -> Dict[str, Any]`

Builds a dependency graph with nodes and edges.

**Parameters:**
- `project_path` (str): Path to the Maven project

**Returns:**
- `Dict[str, Any]`: Graph with "nodes" and "edges"

**Example:**
```python
graph = build_dependency_graph("/path/to/project")
print(f"Nodes: {len(graph['nodes'])}")
print(f"Edges: {len(graph['edges'])}")
```

#### `detect_dependency_conflicts(project_path: str) -> List[Dict[str, Any]]`

Finds version conflicts in dependencies.

**Parameters:**
- `project_path` (str): Path to the Maven project

**Returns:**
- `List[Dict[str, Any]]`: List of conflict information

**Example:**
```python
conflicts = detect_dependency_conflicts("/path/to/project")
for conflict in conflicts:
    print(f"Conflict: {conflict['dependency']} - {conflict['versions']}")
```

#### `suggest_dependency_updates(project_path: str) -> List[Dict[str, Any]]`

Suggests version updates for dependencies.

**Parameters:**
- `project_path` (str): Path to the Maven project

**Returns:**
- `List[Dict[str, Any]]`: List of update suggestions

**Example:**
```python
updates = suggest_dependency_updates("/path/to/project")
for update in updates:
    print(f"Update {update['artifact']}: {update['current']} -> {update['latest']}")
```

---

### Code Generation Tools

#### `generate_getters_setters(file_path: str, class_name: str, fields: List[FieldState]) -> str`

Generates getter and setter methods for fields.

**Parameters:**
- `file_path` (str): Path to the Java file
- `class_name` (str): Name of the class
- `fields` (List[FieldState]): List of fields

**Returns:**
- `str`: Generated getter/setter code

**Example:**
```python
fields = [{"name": "name", "type": "String"}]
code = generate_getters_setters("/path/to/User.java", "User", fields)
```

#### `generate_constructor(file_path: str, class_name: str, fields: List[FieldState], include_all: bool = True) -> str`

Generates a constructor.

**Parameters:**
- `file_path` (str): Path to the Java file
- `class_name` (str): Name of the class
- `fields` (List[FieldState]): List of fields
- `include_all` (bool, optional): Include all fields or none (default: True)

**Returns:**
- `str`: Generated constructor code

**Example:**
```python
code = generate_constructor("/path/to/User.java", "User", fields, include_all=True)
```

#### `generate_tostring_equals_hashcode(file_path: str, class_name: str, fields: List[FieldState]) -> str`

Generates toString, equals, and hashCode methods.

**Parameters:**
- `file_path` (str): Path to the Java file
- `class_name` (str): Name of the class
- `fields` (List[FieldState]): List of fields

**Returns:**
- `str`: Generated methods code

**Example:**
```python
code = generate_tostring_equals_hashcode("/path/to/User.java", "User", fields)
```

#### `generate_builder_pattern(file_path: str, class_name: str, fields: List[FieldState]) -> str`

Generates a complete builder pattern.

**Parameters:**
- `file_path` (str): Path to the Java file
- `class_name` (str): Name of the class
- `fields` (List[FieldState]): List of fields

**Returns:**
- `str`: Generated builder class code

**Example:**
```python
code = generate_builder_pattern("/path/to/User.java", "User", fields)
```

---

### Git Tools

#### `git_status(project_path: str) -> str`

Gets git status of the project.

**Parameters:**
- `project_path` (str): Path to the project

**Returns:**
- `str`: Git status output

**Example:**
```python
status = git_status("/path/to/project")
print(status)
```

#### `git_log(project_path: str, max_count: int = 10) -> str`

Gets git commit history.

**Parameters:**
- `project_path` (str): Path to the project
- `max_count` (int, optional): Maximum commits (default: 10)

**Returns:**
- `str`: Git log output

**Example:**
```python
log = git_log("/path/to/project", max_count=5)
print(log)
```

#### `git_diff(project_path: str, file_path: str = None) -> str`

Shows git diff for project or specific file.

**Parameters:**
- `project_path` (str): Path to the project
- `file_path` (str, optional): Specific file path

**Returns:**
- `str`: Git diff output

**Example:**
```python
diff = git_diff("/path/to/project", "/path/to/User.java")
print(diff)
```

#### `git_is_repository(project_path: str) -> bool`

Checks if directory is a git repository.

**Parameters:**
- `project_path` (str): Path to check

**Returns:**
- `bool`: True if git repository

**Example:**
```python
is_repo = git_is_repository("/path/to/project")
```

#### `generate_commit_message(project_path: str) -> str`

Auto-generates commit message based on staged changes.

**Parameters:**
- `project_path` (str): Path to the project

**Returns:**
- `str`: Generated commit message

**Example:**
```python
message = generate_commit_message("/path/to/project")
print(message)
```

---

### Code Quality Tools

#### `detect_code_smells(project_path: str) -> List[Dict[str, Any]]`

Detects code smells (long methods, large classes, magic numbers, etc.).

**Parameters:**
- `project_path` (str): Path to the project

**Returns:**
- `List[Dict[str, Any]]`: List of code smell findings

**Example:**
```python
smells = detect_code_smells("/path/to/project")
for smell in smells:
    print(f"{smell['type']}: {smell['file']}:{smell['line']}")
```

#### `detect_security_issues(project_path: str) -> List[Dict[str, Any]]`

Identifies security vulnerabilities.

**Parameters:**
- `project_path` (str): Path to the project

**Returns:**
- `List[Dict[str, Any]]`: List of security issues

**Example:**
```python
issues = detect_security_issues("/path/to/project")
for issue in issues:
    print(f"{issue['severity']}: {issue['description']}")
```

#### `check_naming_conventions(project_path: str) -> List[Dict[str, Any]]`

Checks Java naming standards for classes, methods, fields.

**Parameters:**
- `project_path` (str): Path to the project

**Returns:**
- `List[Dict[str, Any]]`: List of naming convention violations

**Example:**
```python
violations = check_naming_conventions("/path/to/project")
for violation in violations:
    print(f"{violation['type']}: {violation['name']}")
```

---

### Project Operations Tools

#### `search_in_files(project_path: str, search_text: str, file_pattern: str = "*.java") -> List[Dict[str, Any]]`

Searches for text across all Java files.

**Parameters:**
- `project_path` (str): Path to the project
- `search_text` (str): Text to search for
- `file_pattern` (str, optional): File pattern (default: "*.java")

**Returns:**
- `List[Dict[str, Any]]`: List of search results

**Example:**
```python
results = search_in_files("/path/to/project", "UserService")
for result in results:
    print(f"{result['file']}:{result['line']}")
```

#### `replace_in_files(project_path: str, search_text: str, replace_text: str, file_pattern: str = "*.java") -> Dict[str, Any]`

Replaces text across multiple files.

**Parameters:**
- `project_path` (str): Path to the project
- `search_text` (str): Text to search for
- `replace_text` (str): Text to replace with
- `file_pattern` (str, optional): File pattern (default: "*.java")

**Returns:**
- `Dict[str, Any]`: Replacement results

**Example:**
```python
result = replace_in_files(
    "/path/to/project",
    "OldService",
    "NewService"
)
```

#### `bulk_add_import(project_path: str, import_statement: str) -> Dict[str, Any]`

Adds import statement to all Java files.

**Parameters:**
- `project_path` (str): Path to the project
- `import_statement` (str): Import statement to add

**Returns:**
- `Dict[str, Any]`: Bulk operation results

**Example:**
```python
result = bulk_add_import("/path/to/project", "import java.util.List;")
```

#### `count_java_entities(project_path: str) -> Dict[str, int]`

Counts classes, methods, and fields across the project.

**Parameters:**
- `project_path` (str): Path to the project

**Returns:**
- `Dict[str, int]`: Entity counts

**Example:**
```python
counts = count_java_entities("/path/to/project")
print(f"Classes: {counts['classes']}")
print(f"Methods: {counts['methods']}")
print(f"Fields: {counts['fields']}")
```

#### `list_all_classes(project_path: str) -> List[Dict[str, Any]]`

Lists all classes with package information.

**Parameters:**
- `project_path` (str): Path to the project

**Returns:**
- `List[Dict[str, Any]]`: List of class information

**Example:**
```python
classes = list_all_classes("/path/to/project")
for cls in classes:
    print(f"{cls['package']}.{cls['name']}")
```

---

## Utilities

### Validation

Located in `src/utils/validation.py`

**Functions:**

- `validate_class_name(name: str) -> None`: Validates Java class name
- `validate_method_name(name: str) -> None`: Validates Java method name
- `validate_field_name(name: str) -> None`: Validates Java field name
- `validate_project_directory(path: str) -> None`: Validates project directory
- `validate_file_exists(path: str) -> None`: Validates file exists
- `not_none(value: Any, param_name: str) -> None`: Checks value is not None
- `not_empty(value: str, param_name: str) -> None`: Checks value is not empty

**Raises:**
- `ValidationError`: If validation fails

### Security

Located in `src/utils/security.py`

**Functions:**

- `sanitize_path(path: str) -> str`: Sanitizes file paths
- `sanitize_shell_command(command: str) -> str`: Sanitizes shell commands
- `sanitize_sql_input(input_str: str) -> str`: Sanitizes SQL inputs
- `sanitize_html_input(input_str: str) -> str`: Sanitizes HTML inputs
- `sanitize_filename(filename: str) -> str`: Sanitizes filenames
- `check_for_secrets(content: str) -> List[Dict[str, Any]]`: Detects secrets in content

### State Management

Located in `src/utils/state_manager.py`

**Class: `StateManager`**

**Methods:**

- `get_state(project_name: str) -> Dict`: Get project state
- `set_state(project_name: str, state: Dict) -> None`: Set project state
- `begin_transaction(project_name: str) -> str`: Begin a transaction
- `commit_transaction(transaction_id: str) -> None`: Commit a transaction
- `rollback_transaction(transaction_id: str) -> None`: Rollback a transaction
- `execute_with_rollback(project_name: str, func: Callable) -> Any`: Execute function with automatic rollback
- `verify_state_consistency(project_name: str) -> bool`: Verify state consistency
- `invalidate_class_state(project_name: str, class_name: str) -> None`: Invalidate specific class state

**Singleton Functions:**

- `get_state_manager() -> StateManager`: Get global state manager instance
- `reset_state_manager() -> None`: Reset global state manager

### Access Control

Located in `src/utils/access_control.py`

**Class: `AccessControlManager`**

**Methods:**

- `set_project_root(path: str) -> None`: Set project root directory
- `get_project_root() -> str`: Get project root directory
- `add_allowed_path(path: str) -> None`: Add allowed path
- `add_restricted_path(path: str) -> None`: Add restricted path
- `set_read_only_mode(enabled: bool) -> None`: Set read-only mode
- `check_permission(path: str, operation: AccessLevel) -> AccessControlEntry`: Check permission
- `ensure_access(path: str, operation: AccessLevel) -> None`: Ensure access (raises if denied)
- `log_operation(operation: str, path: str, success: bool, details: str) -> None`: Log operation
- `get_audit_log(limit: int = 100) -> List[AuditLogEntry]`: Get audit log
- `export_audit_log(file_path: str) -> None`: Export audit log to JSON
- `get_statistics() -> Dict`: Get access statistics

**Singleton Functions:**

- `get_access_control_manager() -> AccessControlManager`: Get global access control manager
- `reset_access_control_manager() -> None`: Reset global access control manager

---

## Workflow

The LangGraph workflow automates the test generation process through the following stages:

### Graph Structure

```
START → analyze_project → class_analysis → generate_test → review_test
         ↓                                                    ↓
    Should review?                                       Should validate?
         ↓                                                    ↓
    regenerate_test ←───────────────────────────────────────────┘
         ↓                                                    ↓
         └────────────────→ validate_test → fix_test (loop if needed)
                                  ↓
                            project_validator → END
```

### Workflow Stages

1. **analyze_project**: Scans codebase, identifies classes, builds dependency graph
2. **class_analysis**: Extracts metadata for a single class
3. **generate_test**: Generates initial test class using LLM
4. **review_test**: Reviews generated test for best practices
5. **validate_test**: Executes tests and captures errors
6. **fix_test**: Fixes failing tests based on validation errors
7. **project_validator**: Final integration checks and summary

### Conditional Edges

- **should_continue_review**: Checks if review found issues requiring regeneration
- **should_validate**: Checks test status and retry count for validation loop

### Example Usage

```python
from src.graphs.workflow import create_workflow
from src.states import ProjectState

app = create_workflow()

initial_state: ProjectState = {
    "messages": [],
    "project_path": "/path/to/project",
    "project_name": "my-project",
    # ... other fields
}

# Run workflow
result = await app.ainvoke(initial_state)
```

---

## Error Handling

All tools use custom exceptions for better error handling:

### Custom Exceptions

- `AgentError`: Base exception for all agent errors
- `ValidationError`: Input validation failures
- `LLMError`: LLM interaction failures
- `ToolError`: Base for tool-related errors
- `FileOperationError`: File operation failures
- `MavenError`: Maven operation failures
- `TestError`: Test execution failures
- `CompilationError`: Compilation errors
- `ParsingError`: Parsing errors
- `RetryExhaustedError`: Retry limit exceeded

### Error Response Format

Most tools return error responses in this format:

```python
{
    "success": False,
    "error": "Error message",
    "details": {
        # Additional error details
    }
}
```

---

## Best Practices

1. **Always validate paths** before operations
2. **Use transactions** for multi-step operations
3. **Check permissions** before file operations
4. **Sanitize inputs** from external sources
5. **Handle exceptions** gracefully
6. **Log operations** for debugging and auditing
7. **Use state management** for consistency
8. **Run tests** after code generation

---

## Examples

### Complete Analysis Workflow

```python
from src.tools.java_tools import find_java_files, create_java_class_state
from src.tools.maven_tools import create_project_state

# Analyze project
project_state = create_project_state("/path/to/project")

# Find all Java files
java_files = find_java_files("/path/to/project")

# Analyze each class
for file_path in java_files:
    class_state = create_java_class_state(file_path)
    print(f"Class: {class_state['name']}")
    print(f"  Methods: {len(class_state['methods'])}")
    print(f"  Fields: {len(class_state['fields'])}")
```

### Code Generation Workflow

```python
from src.tools.code_generation_tools import generate_getters_setters
from src.tools.java_tools import create_java_class_state, add_field

# Get class state
class_state = create_java_class_state("/path/to/User.java")

# Add a field
add_field("/path/to/User.java", "User", {
    "name": "email",
    "type": "String",
    "modifiers": ["private"]
})

# Generate getter/setter
code = generate_getters_setters(
    "/path/to/User.java",
    "User",
    class_state["fields"]
)
print(code)
```

### Maven Analysis Workflow

```python
from src.tools.maven_dependency_tools import (
    get_transitive_dependencies,
    detect_dependency_conflicts,
    suggest_dependency_updates
)

# Get all dependencies
deps = get_transitive_dependencies("/path/to/project")

# Check for conflicts
conflicts = detect_dependency_conflicts("/path/to/project")

# Suggest updates
updates = suggest_dependency_updates("/path/to/project")
```

### Security Check Workflow

```python
from src.utils.security import check_for_secrets
from src.utils.validation import validate_project_directory

# Validate project
try:
    validate_project_directory("/path/to/project")
except ValidationError as e:
    print(f"Validation error: {e}")

# Check for secrets
code = open("/path/to/file.java").read()
secrets = check_for_secrets(code)
for secret in secrets:
    print(f"Found secret: {secret['type']} at line {secret['line']}")
```

---

## API Version

Current version: 1.0.0

For updates and changelog, see the [README](README.md).
