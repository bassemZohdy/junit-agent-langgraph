# LangGraph + Ollama Application

A Python application using LangGraph with Ollama for AI agent workflows with automated test generation for Java projects.

## Features

- **AI-Powered Java Analysis**: Analyze Java projects using Ollama LLM
- **Automated Test Generation**: Generate JUnit/Spring Boot tests automatically
- **Code Management**: Add, remove, replace, and comment Java components (imports, fields, methods, annotations)
- **Maven Integration**: Build, test, package, and analyze Maven projects
- **Direct File System Operations**: Stateless approach with on-demand state creation
- **Comprehensive State Tracking**: Detailed state models for Java classes, dependencies, builds, and projects
- **Maven Dependency Analysis**: Transitive dependencies, dependency graph, conflict detection, version update suggestions

## Setup

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

## Usage

Run the application with a project path:
```bash
python -m src.main --project-path /path/to/project
```

## Project Structure

```
.
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── requirements.txt     # Python dependencies
├── src/
│   ├── config.py        # Configuration settings
│   ├── main.py          # Application entry point
│   ├── agents/          # Agent definitions (modular, self-contained)
│   │   ├── base.py      # Abstract base agent
│   │   ├── reasoning.py # ReasoningAgent with LLM
│   │   └── tool.py      # ToolAgent without LLM
│   ├── constants/       # Status enums and constants
│   ├── config/          # Centralized configuration
│   ├── exceptions/       # Custom exceptions and error handling
│   ├── llm/             # LLM factory
│   │   └── __init__.py  # create_llm() function
│   ├── graphs/          # LangGraph workflows
│   ├── states/          # State definitions
│   │   └── project.py   # ProjectState and JavaClassState
│   ├── tools/           # Tools and utilities
│   │   ├── file_tools.py    # File operations (read, write, list, delete)
│   │   ├── java_tools.py    # Java analysis & management
│   │   ├── maven_tools.py   # Maven operations
│   │   ├── async_maven_tools.py # Async Maven operations
│   │   ├── maven_dependency_tools.py # Dependency analysis
│   │   └── utils.py         # General utilities
│   │       ├── java_parser.py   # Java AST parsing utilities
│   │       ├── llm_helpers.py   # LLM prompt/response helpers
│   │       ├── logging.py       # Structured logging
│   │       ├── caching.py       # Thread-safe caching
│   │       ├── concurrent.py    # Concurrent operations
│   │       └── tool_registry.py # Tool dependency injection
│   └── __init__.py
└── tests/              # Test files
```

## Agent Architecture

Modular, dependency-injected agent design:

### Core Agent Classes

- **base.py**: `BaseAgent` abstract class
  - LLM is optional (agents can work without LLM)
  - Implements abstract method `process()` that subclasses must override
  - Provides helper methods `invoke()` and `invoke_sync()`
  - Integrated with structured logging

### Test Generation Agents

All agents extend `BaseAgent` and are used in the test generation workflow:

- **analyze_project.py**: Scans codebase, identifies classes, builds dependency graph
- **class_analysis.py**: Extracts metadata for a single class (methods, fields, dependencies)
- **generate_test.py**: The LLM writes the initial JUnit/Spring Boot test class
- **review_test.py**: A separate LLM (or specialized prompt) "lints" the code for best practices
- **validate_test.py**: Crucial: Executes the code (e.g., via mvn test or a dynamic compiler) and captures stack traces
- **fix_test.py**: Takes the error logs from validation and asks the LLM to provide a corrected version
- **project_validator.py**: Performs final integration checks and generates a summary report

### Utility Modules (`src/utils/`)

#### Shared Utilities

- **java_parser.py**: Shared javalang parsing functions
  - `extract_imports()` - Extract import statements from AST
  - `extract_dependencies()` - Extract external dependencies
  - `parse_java_file()` - Parse Java source code
  - `extract_class_name_from_tree()` - Extract class name from AST
  - Eliminates code duplication between agents

- **llm_helpers.py**: LLM interaction helpers
  - `parse_code_from_response()` - Extract code blocks from LLM responses
  - `extract_list_from_response()` - Parse review comments
  - `build_test_generation_prompt()` - Builds test generation prompts
  - `build_test_fix_prompt()` - Builds fix prompts
  - `build_code_review_prompt()` - Builds review prompts

- **logging.py**: Structured logging infrastructure
  - `AgentLogger` class - Centralized logger with file/console output
  - `get_logger()` - Get/create logger instances
  - `set_global_level()` - Set log level for all loggers
  - `log_function_call()` decorator - Log function execution
  - `log_execution_time()` decorator - Measure and log execution times

- **caching.py**: Thread-safe caching layer
  - `CacheManager` class - LRU cache with TTL support
  - `get_cache()` - Get global cache instance
  - `cache_file_read()` decorator - Cache file reads with mtime checking
  - `cache_ast_parse()` decorator - Cache AST parsing results
  - `invalidate_file_cache()` - Invalidate specific file cache
  - `invalidate_all_cache()` - Clear all cache entries
  - `get_cache_stats()` - Cache statistics (hits, misses, hit rate)

- **concurrent.py**: Concurrent file operations
  - `run_concurrent_tasks()` - Execute tasks in parallel with ThreadPoolExecutor
  - `read_multiple_files_async()` - Read multiple files in parallel
  - `write_multiple_files_async()` - Write multiple files in parallel
  - `process_files_concurrently()` - Process files with custom functions
  - `RateLimiter` class - Control concurrent operations with semaphore
  - `with_rate_limiter()` - Execute functions with rate limiting

- **tool_registry.py**: Tool dependency injection
  - `ToolDefinition` dataclass - Tool metadata (name, func, description, is_async)
  - `ToolRegistry` class - Central registry with mock support
  - `get_registry()` - Get global registry instance
  - `get_tool()` - Convenience function to retrieve tools
  - `register_tool()` - Register tools programmatically
  - `mock_tool()` / `unmock_tool()` - Testing support

- **validation.py**: Input validation and security
  - Path validation (validate_file_exists, validate_directory_exists, validate_project_directory)
  - Java-specific validation (class_name, method_name, field_name, annotation_name, package_name)
  - Maven validation (validate_maven_goal, validate_maven_scope)
  - General validation (not_none, not_empty, range, in_allowed_values)
  - Security validation (sanitize_path, prevent path traversal)
  - Type validation (validate_class_name, validate_method_name, validate_field_name, validate_annotation_name, validate_import_statement, validate_modifier)

- **security.py**: Comprehensive security utilities
  - SecurityUtils class with static security methods
  - Path sanitization (sanitize_path) - prevents path traversal and dangerous patterns
  - Shell command sanitization (sanitize_shell_command, sanitize_shell_args) - prevents injection
  - SQL input sanitization (sanitize_sql_input) - prevents SQL injection
  - HTML input sanitization (sanitize_html_input) - prevents XSS attacks
  - Filename sanitization (sanitize_filename) - validates dangerous chars and reserved names
  - Extension validation (validate_allowed_extensions)
  - Java identifier sanitization (package_name, class_name, method_name, field_name)
  - Secret detection (check_for_secrets) - identifies passwords, API keys, tokens
  - Project path validation (validate_project_path)
  - Dangerous pattern detection (path traversal, XSS, SQL injection, shell injection, secrets)

- **state_manager.py**: State consistency and transaction management
  - `StateManager` class - Manages state with validation, rollback, and concurrency control
  - `StateSnapshot` dataclass - State snapshot at specific point in time
  - `StateTransaction` dataclass - Represents a state transaction
  - Functions: get_state(), set_state(), validate_state(), begin_transaction(), commit_transaction(), rollback_transaction()
  - Transaction support: execute_with_rollback(), sync_state_with_filesystem()
  - Consistency verification: verify_state_consistency()
  - State management: invalidate_class_state(), clear_state()
  - Global singleton: get_state_manager(), reset_state_manager()

- **access_control.py**: File operation access control and auditing
  - `AccessControlManager` class - Manages access control for file operations
  - `AccessLevel` enum - Access levels: READ, WRITE, DELETE, EXECUTE
  - `AccessControlEntry` dataclass - Represents access control decision
  - `AuditLogEntry` dataclass - Represents audit log entry
  - Functions: set_project_root(), get_project_root(), add_allowed_path(), add_restricted_path()
  - Access control: set_read_only_mode(), is_read_only_mode(), check_permission(), ensure_access()
  - Audit logging: log_operation(), get_audit_log(), clear_audit_log(), export_audit_log()
  - Statistics: get_statistics()
  - Global singleton: get_access_control_manager(), reset_access_control_manager()
  - Features: file permission checking, restrict operations outside project, read-only mode, audit logging

### Constants (`src/constants/status.py`)

Status enums for type safety:
- `TestStatus` - GENERATED, PASSED, FAILED, REVIEWED, etc.
- `BuildStatus` - SUCCESS, FAILED, ERROR, RUNNING
- `ClassStatus` - ANALYZED, ERROR, PENDING
- `AgentAction` - Workflow action identifiers
- `MavenScope` - COMPILE, TEST, RUNTIME, etc.
- `ProjectType`, `PackagingType` - Project type enums

### Configuration (`src/config/settings.py`)

Centralized configuration with environment variable support:
- `AppConfig` dataclass - All configuration values
- `from_env()` - Load from environment variables
- `validate()` - Configuration validation
- Configurable: timeouts, retries, paths, logging, caching

### Error Handling (`src/exceptions/handler.py`)

Custom exception hierarchy:
- `AgentError` - Base exception for all agent errors
- `ValidationError` - Input validation failures
- `LLMError` - LLM interaction failures
- `ToolError` - Base for tool-related errors
- `FileOperationError`, `MavenError`, `TestError`
- `CompilationError`, `ParsingError`, `RetryExhaustedError`
- Helper functions: `create_error_response()`, `format_error_message()`

## State Management

Application states defined in `src/states/project.py`:

### ProjectState
Represents the entire project with:
- `messages` - Conversation message history
- `project_path` - Path to the project directory
- `java_classes` - List of `JavaClassState` objects
- `test_classes` - List of `TestClassState` objects
- `dependency_graph` - Dependency relationships
- `build_status` - Overall build status
- `last_action` - Last performed action
- `current_class` - Currently processing class
- `test_results` - Test execution results
- `summary_report` - Final validation summary
- `retry_count` - Current retry count
- `max_retries` - Maximum allowed retries
- `all_tests_passed` - Overall test pass status

### JavaClassState
Represents a single Java class with:
- `name` - Class name
- `file_path` - Path to the Java source file
- `package` - Package declaration
- `content` - File content
- `type` - Class type
- `modifiers` - List of modifiers (public, private, etc.)
- `extends` - Superclass name
- `implements` - List of implemented interfaces
- `annotations` - List of class annotations
- `fields` - List of `FieldState` objects with full metadata
- `methods` - List of `MethodState` objects with full metadata
- `imports` - List of `ImportState` objects
- `inner_classes` - List of nested classes
- `status` - Analysis/compilation status
- `errors` - List of errors encountered
- `line_number` - Line number in source file

### TestClassState
Represents a test class with:
- `name` - Test class name
- `file_path` - Path to the test source file
- `content` - Test code content
- `target_class` - Class being tested
- `test_methods` - List of test methods
- `status` - Test status (generated, passed, failed, etc.)
- `errors` - List of errors
- `review_comments` - Code review feedback

## Workflow

### Graph Structure

**Linear Edges:**
- START → analyze_project → class_analysis → generate_test → review_test

**Review Cycle (Conditional):**
- `should_continue_review()` checks if issues found
- Issues found → regenerate_test
- Passed → validate_test

**Validation/Fix Cycle (Conditional):**
- `should_validate()` checks test status and retry count
- Tests fail AND retries < max → fix_test
- Tests pass → project_validator
- Max retries reached → END (with "Failed" status)

**Fix Path:**
- fix_test → validate_test (Re-run execution to check the fix)

## Tools

Available tools for agent operations:

### File Tools (`file_tools.py`)
- `read_file` - Read contents of a file
- `write_file` - Write content to a file
- `list_files` - List files in directory with pattern matching
- `list_directories` - List directories in a path
- `delete_file` - Delete a file

### Java Tools (`java_tools.py`)
- `find_java_files` - Find all Java source files
- `create_java_class_state` - Create JavaClassState from Java file with full metadata
- `get_java_classes` - Get all classes declared in a Java file
- `get_java_methods` - Get all methods from a Java file or specific class
- `get_java_fields` - Get all fields from a Java file or specific class
- `get_java_imports` - Get all imports from a Java file
- `get_java_annotations` - Get all annotations from a Java file
- `get_java_package` - Get package declaration from a Java file
- `analyze_java_class` - Get complete analysis of a Java class
- `add_import` - Add an import statement to a Java file
- `remove_import` - Remove an import statement from a Java file
- `replace_import` - Replace an import statement in a Java file
- `comment_import` - Comment out an import statement in a Java file
- `add_field` - Add a field to a specific class in a Java file
- `remove_field` - Remove a field from a specific class in a Java file
- `replace_field` - Replace a field in a specific class in a Java file
- `comment_field` - Comment out a field in a specific class in a Java file
- `add_method` - Add a method to a specific class in a Java file
- `remove_method` - Remove a method from a specific class in Java file
- `replace_method` - Replace a method in a specific class in a Java file
- `comment_method` - Comment out a method in a specific class in a Java file
- `add_annotation` - Add an annotation to a class, method, or field in a Java file
- `remove_annotation` - Remove an annotation from a class, method, or field
- `replace_annotation` - Replace an annotation in a class, method, or field in a Java file
- `comment_annotation` - Comment out an annotation in a class, method, or field

### Maven Tools (`maven_tools.py`, `async_maven_tools.py`)
- `maven_build` - Run Maven build with custom goals
- `maven_test` - Run Maven tests
- `maven_clean` - Clean Maven build artifacts
- `maven_package` - Package project into JAR
- `maven_dependency_tree` - Show dependency tree
- `maven_info` - Get effective Maven project information

### Maven Dependency Analysis Tools (`maven_dependency_tools.py`)
- `get_transitive_dependencies` - Get all direct and indirect dependencies
- `build_dependency_graph` - Build dependency graph with nodes and edges
- `detect_dependency_conflicts` - Find version conflicts
- `suggest_dependency_updates` - Suggest version updates

### Code Generation Tools (`code_generation_tools.py`)
- `generate_getters_setters` - Generate getter and setter methods for all fields
- `generate_constructor` - Generate constructor with all or no fields
- `generate_tostring_equals_hashcode` - Generate toString, equals, and hashCode methods
- `generate_builder_pattern` - Generate complete builder pattern for class

### Git Tools (`git_tools.py`)
- `git_status` - Get git status of the project
- `git_log` - Get git commit history
- `git_diff` - Show git diff for project or specific file
- `git_file_history` - Show modification history for a specific file
- `git_branch` - Get current git branch
- `git_add` - Add file to git staging area
- `git_commit` - Create git commit with message
- `generate_commit_message` - Generate commit message based on staged changes
- `git_is_repository` - Check if directory is a git repository

### Code Quality Tools (`code_quality_tools.py`)
- `detect_code_smells` - Detect code smells (long methods, large classes, magic numbers)
- `detect_security_issues` - Identify security vulnerabilities (SQL injection, command injection, weak encryption)
- `check_naming_conventions` - Check Java naming standards for classes, methods, fields

### Project Operations Tools (`project_operations.py`)
- `search_in_files` - Search for text across all Java files in project
- `replace_in_files` - Replace text across multiple files
- `bulk_add_import` - Add import statement to all Java files
- `bulk_remove_import` - Remove import statement from all Java files
- `count_java_entities` - Count classes, methods, and fields across project
- `refactor_multiple_classes` - Apply refactoring to multiple classes at once
- `list_all_classes` - List all classes with package information

### Utils (`utils.py`)
- `calculator` - Evaluate mathematical expressions
- `search` - Search for information (placeholder)

### Utils
- **java_parser.py** - Shared javalang parsing utilities
- **llm_helpers.py** - LLM prompt/response helpers
- **logging.py** - Structured logging infrastructure
- **caching.py** - Thread-safe caching with LRU eviction
- **concurrent.py** - Concurrent file operations
- **tool_registry.py** - Tool dependency injection

## Completed Features

### ✅ Core Functionality

All critical functionality has been implemented:

1. **Dependency Resolution** - All version conflicts resolved in requirements.txt
2. **Tool Error Handling & Validation** - Comprehensive validation framework with custom exceptions
3. **State Consistency** - Thread-safe state management with transactions and rollback support
4. **Input Sanitization & Security** - Multi-layered security (path traversal, SQL injection, XSS, shell injection, secret detection)
5. **Access Control** - File operation permissions, read-only mode, audit logging, statistics
6. **Java State Extraction** - Full metadata extraction using javalang (fields, methods, annotations, imports)
7. **Code Generation Tools** - Generate getters/setters, constructors, toString/equals/hashCode, builder patterns
8. **Git Integration** - Git status, history, diff, add/commit, commit message generation
9. **Code Quality Analysis** - Code smells detection, security vulnerability detection, naming convention checks
10. **Project-Level Operations** - Bulk search/replace, import management, entity counting, multi-class refactoring

### ✅ User Experience & Documentation

- **CLI User Experience** - Command history with arrow keys, tab completion for file paths, color-coded output, progress bars for long operations
- **Integration Tests** - Complete workflow tests, real Java project testing, error scenario coverage, concurrent operations testing
- **API Documentation** - All tool parameters documented with code examples, state object fields documented, workflow diagrams added (see [API.md](API.md))
- **User Guide** - Detailed getting started tutorial, common use cases, troubleshooting guide, FAQ section (see [USER_GUIDE.md](USER_GUIDE.md))
- **Test Sample Projects** - Consolidated sample projects in `tests/samples/` (not tracked by Git) including:
  - **junit4-sample**: Simple JUnit 4 project with Calculator
  - **junit5-sample**: JUnit 5 project with StringValidator and advanced testing features
  - **springboot-sample**: Complete Spring Boot 3.2.0 REST API application
  - **multi-module**: Multi-module Maven project with inter-module dependencies

### ✅ Infrastructure & Utilities

20+ new modules created for robust architecture:

**Security & Safety:**
- `src/utils/validation.py` - Input validation and security checks
- `src/utils/security.py` - Comprehensive security utilities and sanitization
- `src/utils/access_control.py` - Permission management and audit logging

**State Management:**
- `src/utils/state_manager.py` - Thread-safe state with transactions and rollback

**Performance & Reliability:**
- `src/utils/logging.py` - Structured logging infrastructure
- `src/utils/caching.py` - Thread-safe LRU cache with TTL
- `src/utils/concurrent.py` - Concurrent file operations with rate limiting

**Core Infrastructure:**
- `src/utils/java_parser.py` - Shared javalang parsing utilities
- `src/utils/llm_helpers.py` - LLM prompt/response helpers
- `src/utils/tool_registry.py` - Tool dependency injection with mock support
- `src/constants/status.py` - Type-safe status enums
- `src/config/settings.py` - Centralized configuration with env support
- `src/exceptions/handler.py` - Custom exception hierarchy

**Additional Tools:**
- `src/tools/async_maven_tools.py` - Async Maven operations
- `src/tools/maven_dependency_tools.py` - Dependency analysis
- `src/tools/code_generation_tools.py` - Code generation utilities
- `src/tools/git_tools.py` - Git integration
- `src/tools/code_quality_tools.py` - Code quality analysis
- `src/tools/project_operations.py` - Project-level operations
