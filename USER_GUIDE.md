# User Guide

Welcome to the LangGraph + Ollama Java Test Generator! This guide will help you get started and make the most of the application.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running Your First Analysis](#running-your-first-analysis)
- [Common Use Cases](#common-use-cases)
  - [Analyzing a Java Project](#analyzing-a-java-project)
  - [Generating Unit Tests](#generating-unit-tests)
  - [Generating Spring Boot Tests](#generating-spring-boot-tests)
  - [Code Generation](#code-generation)
  - [Maven Analysis](#maven-analysis)
  - [Git Integration](#git-integration)
  - [Code Quality Checks](#code-quality-checks)
- [Advanced Features](#advanced-features)
  - [State Management](#state-management)
  - [Access Control](#access-control)
  - [Security Features](#security-features)
  - [CLI Features](#cli-features)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
  - [Error Messages](#error-messages)
  - [Performance Issues](#performance-issues)
- [FAQ](#faq)

---

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher**: Download from [python.org](https://www.python.org/)
- **Java 17 or higher**: Download from [oracle.com](https://www.oracle.com/java/technologies/downloads/)
- **Maven 3.6+**: Download from [maven.apache.org](https://maven.apache.org/download.cgi)
- **Ollama**: Install from [ollama.com](https://ollama.com/)
- **Git**: Download from [git-scm.com](https://git-scm.com/)

**Ollama Setup:**
```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (e.g., codellama or deepseek-coder)
ollama pull codellama:7b

# Start Ollama server
ollama serve
```

### Installation

1. **Clone the repository** (if you haven't already):
```bash
git clone <repository-url>
cd agent
```

2. **Create a virtual environment**:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/macOS
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred settings
# Default values should work for most cases
```

### Configuration

The `.env` file contains configurable settings:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=codellama:7b
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=2048

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/agent.log

# Cache Configuration
CACHE_ENABLED=true
CACHE_TTL=3600

# Security Configuration
READ_ONLY_MODE=false
PROJECT_ROOT=
```

**Key Configuration Options:**

| Variable | Description | Default |
|----------|-------------|----------|
| `OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Model to use for generation | `codellama:7b` |
| `OLLAMA_TEMPERATURE` | Temperature for LLM (0.0-1.0) | `0.7` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `CACHE_ENABLED` | Enable caching | `true` |
| `READ_ONLY_MODE` | Prevent write operations | `false` |

### Running Your First Analysis

1. **Start Ollama** (if not already running):
```bash
ollama serve
```

2. **Run the application** with your project path:
```bash
python -m src.main --project-path /path/to/your/java/project
```

3. **Interact with the CLI**:
```
╔════════════════════════════════════════════════════════╗
║     LangGraph + Ollama Java Test Generator           ║
╚════════════════════════════════════════════════════════╝

ℹ Project: /path/to/your/java/project

Available Commands:
  analyze <path>        - Analyze a project or file
  generate test         - Generate tests for classes
  build                - Run Maven build
  test                 - Run Maven tests
  list classes        - List all Java classes
  git status           - Show git status
  help                 - Show this help message
  exit                 - Exit application

Agent> list classes
✓ Found 15 Java classes
```

---

## Common Use Cases

### Analyzing a Java Project

**Scenario**: You want to understand the structure of an existing Java project.

**Steps**:

1. Start the application:
```bash
python -m src.main --project-path /path/to/project
```

2. List all classes:
```
Agent> list classes
✓ Found 15 Java classes

Classes:
  • com.example.UserService
  • com.example.OrderService
  • com.example.repository.UserRepository
  • ...
```

3. Get detailed class information:
```
Agent> analyze class UserService
✓ Analyzing UserService

Class: UserService
Package: com.example
Type: class
Modifiers: [public]

Fields (5):
  • private String name
  • private int age
  • private List<String> emails
  ...

Methods (8):
  • public String getName()
  • public void setName(String)
  • public boolean isAdult()
  ...

Annotations (1):
  • @Service
```

### Generating Unit Tests

**Scenario**: You have a Java class and want to generate JUnit tests for it.

**Steps**:

1. Start the application:
```bash
python -m src.main --project-path /path/to/project
```

2. Generate tests for a specific class:
```
Agent> generate test UserService
⏳ Processing...
✓ Test generation complete

Generated: UserServiceTest.java
Location: src/test/java/com/example/UserServiceTest.java
```

3. The generated test will include:
- Setup and teardown methods
- Test methods for each public method
- Assertions for expected behavior
- Mocking where appropriate

**Example Generated Test**:
```java
package com.example;

import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

public class UserServiceTest {
    private UserService userService;
    
    @Before
    public void setUp() {
        userService = new UserService("John Doe", 25);
    }
    
    @Test
    public void testGetName() {
        assertEquals("John Doe", userService.getName());
    }
    
    @Test
    public void testIsAdult() {
        assertTrue(userService.isAdult());
    }
    
    @Test
    public void testAddEmail() {
        userService.addEmail("john@example.com");
        assertEquals(1, userService.getEmails().size());
    }
}
```

### Generating Spring Boot Tests

**Scenario**: You have a Spring Boot application and want to test controllers and services.

**Steps**:

1. Analyze the project (it will auto-detect Spring Boot):
```
Agent> analyze project
✓ Spring Boot detected
✓ JUnit 5 detected
✓ Spring Web detected
```

2. Generate controller tests:
```
Agent> generate test UserController
✓ Spring Boot test generation complete

Generated: UserControllerTest.java
Location: src/test/java/com/example/UserControllerTest.java
```

The generated tests include:
- `@SpringBootTest` annotations
- `@MockBean` for dependencies
- `MockMvc` for testing endpoints
- Request/response assertions

**Example**:
```java
@SpringBootTest
@AutoConfigureMockMvc
public class UserControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private UserService userService;
    
    @Test
    public void testGetUser() throws Exception {
        mockMvc.perform(get("/api/users/1"))
               .andExpect(status().isOk())
               .andExpect(jsonPath("$.name").value("John Doe"));
    }
}
```

### Code Generation

**Scenario**: You want to generate boilerplate code for a class.

#### Generating Getters and Setters

```
Agent> generate getters/setters UserService
✓ Generated getters and setters for 5 fields

Generated methods:
  • public String getName()
  • public void setName(String name)
  • public int getAge()
  • public void setAge(int age)
  ...
```

#### Generating Constructors

```
Agent> generate constructor UserService --all
✓ Generated constructor with all fields

public UserService(String name, int age, List<String> emails) {
    this.name = name;
    this.age = age;
    this.emails = emails;
}
```

#### Generating toString, equals, hashCode

```
Agent> generate toString/equals/hashCode UserService
✓ Generated toString, equals, and hashCode methods
```

#### Generating Builder Pattern

```
Agent> generate builder UserService
✓ Generated builder pattern

Generated: UserBuilder.java
```

### Maven Analysis

**Scenario**: You want to understand dependencies and detect conflicts.

#### View Dependency Tree

```
Agent> maven dependency tree
✓ Dependency tree generated

[INFO] com.example:simple-java:jar:1.0.0
[INFO] └─ junit:junit:jar:4.13.2:test
```

#### Detect Conflicts

```
Agent> maven detect conflicts
✓ No dependency conflicts found
```

#### Suggest Updates

```
Agent> maven suggest updates
✓ Update suggestions found

Updates available:
  • junit: 4.13.2 → 4.13.3
  • commons-lang3: 3.12.0 → 3.14.0
```

#### Build and Test

```
Agent> build
⏳ Building project...
✓ Build successful

Agent> test
⏳ Running tests...
✓ All 12 tests passed
```

### Git Integration

**Scenario**: You want to check git status or generate commit messages.

#### View Status

```
Agent> git status
✓ Git status

On branch main
Changes not staged:
  modified:   src/main/java/com/example/UserService.java
  modified:   src/test/java/com/example/UserServiceTest.java
```

#### View Commit History

```
Agent> git log
✓ Recent commits

commit a1b2c3d (HEAD -> main)
Author: John Doe <john@example.com>
Date:   2024-02-20

    Add user registration feature
```

#### Generate Commit Message

```
Agent> git generate commit message
✓ Generated commit message

feat: add user registration with email validation

- Add UserService.emails field
- Add email validation in UserService.addEmail()
- Add tests for email validation
- Update User entity with email field
```

#### Stage and Commit

```
Agent> git add .
✓ Staged all changes

Agent> git commit "feat: add user registration"
✓ Commit created: a1b2c3d
```

### Code Quality Checks

**Scenario**: You want to identify code smells and security issues.

#### Detect Code Smells

```
Agent> code quality smells
✓ Code smell analysis complete

Issues found:
  • Long method: UserService.processOrder (45 lines)
  • Large class: OrderService (350 lines)
  • Magic number: UserService.MIN_AGE (18)
```

#### Check Naming Conventions

```
Agent> code quality naming
✓ Naming convention check complete

Violations found:
  • Class name: user_service (should be PascalCase)
  • Field name: MAX_SIZE (should be camelCase for non-static)
```

#### Detect Security Issues

```
Agent> code quality security
✓ Security analysis complete

Issues found:
  • SQL Injection risk: DatabaseService.executeUserQuery
  • Weak encryption: EncryptionService.encrypt
  • Hardcoded secret: ConfigService.API_KEY
```

---

## Advanced Features

### State Management

The application maintains project state throughout operations for consistency and rollback capabilities.

**View Current State**:
```python
from src.utils.state_manager import get_state_manager

manager = get_state_manager()
state = manager.get_state("my-project")
print(state["java_classes"])
```

**Transaction Support**:
```python
from src.utils.state_manager import get_state_manager

manager = get_state_manager()

# Begin transaction
transaction_id = manager.begin_transaction("my-project")

try:
    # Perform operations
    # Modify state...
    
    # Commit if successful
    manager.commit_transaction(transaction_id)
except Exception as e:
    # Rollback on error
    manager.rollback_transaction(transaction_id)
```

**Execute with Automatic Rollback**:
```python
def update_project():
    # Multiple operations
    # If any fails, all are rolled back

manager = get_state_manager()
manager.execute_with_rollback("my-project", update_project)
```

### Access Control

Control which files can be accessed and modified.

**Set Project Root**:
```python
from src.utils.access_control import get_access_control_manager

manager = get_access_control_manager()
manager.set_project_root("/path/to/project")
```

**Restrict Directories**:
```python
# Prevent access to configuration directory
manager.add_restricted_path("/path/to/project/config")

# Try to read restricted file
try:
    manager.ensure_access("/path/to/project/config/secrets.properties", "READ")
except Exception as e:
    print(f"Access denied: {e}")
```

**Enable Read-Only Mode**:
```python
# Prevent any write operations
manager.set_read_only_mode(True)

# Try to write file
try:
    manager.ensure_access("/path/to/project/User.java", "WRITE")
except Exception as e:
    print(f"Read-only mode: {e}")
```

**View Audit Log**:
```python
# Get recent operations
log = manager.get_audit_log(limit=50)
for entry in log:
    print(f"{entry.timestamp}: {entry.operation} on {entry.path}")

# Export to JSON
manager.export_audit_log("audit-log.json")

# Get statistics
stats = manager.get_statistics()
print(f"Total operations: {stats['total_operations']}")
print(f"Success rate: {stats['success_rate']}%")
```

### Security Features

The application includes multiple security layers:

**Path Sanitization**:
```python
from src.utils.security import SecurityUtils

# Prevent path traversal
sanitized = SecurityUtils.sanitize_path("../../../etc/passwd")
# Returns: "etc/passwd"
```

**Secret Detection**:
```python
from src.utils.security import SecurityUtils

code = """
public class Config {
    private static final String API_KEY = "sk-1234567890abcdef";
}
"""

secrets = SecurityUtils.check_for_secrets(code)
for secret in secrets:
    print(f"Found {secret['type']} at line {secret['line']}")
```

**Shell Command Sanitization**:
```python
# Prevent command injection
sanitized = SecurityUtils.sanitize_shell_args(["file.txt", "file; rm -rf /"])
```

**Input Validation**:
```python
from src.utils.validation import (
    validate_class_name,
    validate_project_directory,
    ValidationError
)

try:
    validate_class_name("MyClass")
    validate_project_directory("/path/to/project")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### CLI Features

The enhanced CLI provides several features for improved user experience:

**Command History**:
- Use arrow keys (↑/↓) to navigate through command history
- History is saved to `~/.agent_history`

**Tab Completion**:
- Press Tab to autocomplete commands and file paths
- Auto-complete for:
  - Commands (`analyze`, `generate`, `build`, etc.)
  - File paths (supports `..` and `~`)

**Color-Coded Output**:
- ℹ Info messages (cyan)
- ⚠ Warning messages (yellow)
- ✗ Error messages (red)
- ✓ Success messages (green)

**Progress Bars**:
- Visual progress indicators for long operations
- Shows current operation and percentage

**Interactive Prompts**:
- Confirm destructive operations
- Select from multiple options

**Examples**:
```
Agent> an<TAB>
analyze

Agent> analyze cla<TAB>
analyze class
analyze project

Agent> ../my-<TAB>
../my-project/
```

---

## Troubleshooting

### Common Issues

#### Issue: "Module 'langchain' not found"

**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

#### Issue: "Ollama connection refused"

**Solution**: Ensure Ollama is running:
```bash
# Check if Ollama is running
ollama list

# If not, start it
ollama serve
```

#### Issue: "Java files not found"

**Solution**: Verify the project path is correct:
```bash
# Check if path exists
ls /path/to/project

# Check for Java files
find /path/to/project -name "*.java"
```

#### Issue: "Maven build failed"

**Solution**: Check the build output for specific errors:
```
Agent> build
✗ Build failed

Check logs:
• Missing dependencies
• Compilation errors
• Test failures
```

Common fixes:
- Run `mvn clean` first
- Check `pom.xml` for dependency conflicts
- Verify Java version compatibility

#### Issue: "Tests not generating"

**Solution**: 
1. Ensure the target class is properly formatted
2. Check that javalang can parse the file
3. Verify Ollama model is loaded:
```bash
ollama list
```

#### Issue: "Permission denied"

**Solution**:
1. Check file permissions:
```bash
ls -l /path/to/project
```

2. Ensure project root is set:
```python
from src.utils.access_control import get_access_control_manager
manager = get_access_control_manager()
manager.set_project_root("/path/to/project")
```

### Error Messages

#### ValidationError

```
Error: Invalid class name '123Class'
Reason: Class name must start with a letter
```

**Fix**: Use valid Java naming conventions.

#### FileOperationError

```
Error: Cannot read file '/path/to/file.txt'
Reason: File does not exist
```

**Fix**: Verify the file path is correct.

#### MavenError

```
Error: Maven build failed
Reason: Compilation error: cannot find symbol: User
```

**Fix**: Check for missing imports or dependencies.

#### ToolError

```
Error: Tool execution failed
Reason: Invalid input parameters
```

**Fix**: Review tool parameters in API documentation.

### Performance Issues

#### Slow Test Generation

**Solution**:
1. Use a faster Ollama model:
```env
OLLAMA_MODEL=deepseek-coder:6.7b
```

2. Increase max tokens if needed:
```env
OLLAMA_MAX_TOKENS=4096
```

3. Enable caching:
```env
CACHE_ENABLED=true
```

#### Large Project Analysis

**Solution**:
1. Use incremental analysis:
```python
# Analyze one module at a time
for module in modules:
    analyze_project(f"/path/to/project/{module}")
```

2. Increase memory allocation:
```bash
export MAVEN_OPTS="-Xmx2g"
```

#### Out of Memory Errors

**Solution**:
1. Increase Java heap size:
```bash
export JAVA_OPTS="-Xmx4g"
```

2. Use batch processing:
```python
from src.utils.concurrent import run_concurrent_tasks

# Process files in batches
batch_size = 10
for i in range(0, len(files), batch_size):
    batch = files[i:i+batch_size]
    run_concurrent_tasks(process_file, batch)
```

---

## FAQ

### General

**Q: What Java versions are supported?**
A: Java 8 and higher. The application is tested with Java 17 and Java 21.

**Q: Can I use this with Gradle projects?**
A: Currently, only Maven projects are supported. Gradle support is planned for future releases.

**Q: What LLM models are supported?**
A: Any model available in Ollama. Recommended models:
- `codellama:7b` or `codellama:13b`
- `deepseek-coder:6.7b`
- `stable-code:3b`

**Q: Can I run this offline?**
A: Yes, once Ollama is installed and models are downloaded, the application runs completely offline.

### Usage

**Q: How do I generate tests for multiple classes at once?**
A: Use the project operations:
```
Agent> generate tests all
✓ Generating tests for 15 classes
```

**Q: Can I customize test templates?**
A: Yes, create custom templates in `templates/` directory and configure the path in `.env`.

**Q: How do I handle multi-module Maven projects?**
A: The application automatically detects multi-module projects. Analyze each module individually:
```
Agent> analyze project module1
Agent> analyze project module2
```

**Q: Can I use this for non-Java projects?**
A: Currently, only Java projects are supported. Other languages may be added in the future.

### Configuration

**Q: How do I change the Ollama model?**
A: Update `.env`:
```env
OLLAMA_MODEL=deepseek-coder:6.7b
```

**Q: Can I disable caching?**
A: Set in `.env`:
```env
CACHE_ENABLED=false
```

**Q: How do I increase logging verbosity?**
A: Set in `.env`:
```env
LOG_LEVEL=DEBUG
```

### Troubleshooting

**Q: Tests are failing after generation. What should I do?**
A: The application includes an automated fix cycle. If tests fail:
1. Review the error messages
2. The system will automatically attempt to fix issues
3. If issues persist, manually review the generated test

**Q: How do I handle circular dependencies?**
A: Use the dependency graph to identify circular dependencies:
```python
graph = build_dependency_graph("/path/to/project")
# Analyze edges for cycles
```

**Q: What if Ollama is not responding?**
A: 
1. Check Ollama status: `ollama list`
2. Restart Ollama: `ollama serve`
3. Check logs: `logs/agent.log`

### Best Practices

**Q: What are some best practices for test generation?**
A:
- Start with simple classes
- Review generated tests before using
- Use descriptive test method names
- Test both success and failure cases
- Mock external dependencies

**Q: How do I ensure test quality?**
A:
- Run code quality checks on generated tests
- Use the review workflow
- Verify test coverage
- Keep tests up to date with code changes

**Q: Can I integrate this into CI/CD?**
A: Yes, the application can be run in CI/CD pipelines:
```yaml
# Example GitHub Actions
- name: Generate Tests
  run: |
    python -m src.main --project-path . --generate-tests
    
- name: Run Tests
  run: mvn test
```

---

## Getting Help

### Documentation

- **API Reference**: See [API.md](API.md) for detailed API documentation
- **README**: See [README.md](README.md) for project overview
- **TODO**: See [TODO.md](TODO.md) for planned features

### Community

- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Join community discussions on GitHub

### Debugging

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

Check log files:
```bash
tail -f logs/agent.log
```

Export diagnostic information:
```bash
python -m src.main --diagnose
```

---

## Next Steps

Now that you're familiar with the basics, explore:

1. **Advanced Workflows**: Combine multiple tools for complex operations
2. **Custom Templates**: Create your own test and code templates
3. **Integration**: Integrate with your CI/CD pipeline
4. **Contribution**: Contribute features or improvements

Happy coding! 🚀
