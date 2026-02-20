# Test Sample Projects

This directory contains sample Maven projects used for integration testing the LangGraph + Ollama Java test generation application.

These samples are **not tracked by Git** (see `.gitignore`) as they are used primarily to test how the application analyzes and generates test classes for various project types.

## Projects

### junit4-sample

A simple Maven project using JUnit 4 for testing.

**Features:**
- Java 8 compatibility
- JUnit 4.13.2
- Calculator class with basic operations
- Comprehensive test coverage

**Structure:**
- `Calculator.java` - Calculator with add, subtract, multiply, divide
- `CalculatorTest.java` - JUnit 4 tests

**Use Case:** Testing basic Java project analysis and JUnit 4 test generation

### junit5-sample

A Maven project using JUnit 5 (Jupiter) for testing.

**Features:**
- Java 11 compatibility
- JUnit 5.10.0
- StringValidator class
- Advanced JUnit 5 features

**Structure:**
- `StringValidator.java` - String validation utility
- `StringValidatorTest.java` - JUnit 5 tests featuring:
  - `@Test` - Standard tests
  - `@DisplayName` - Custom test names
  - `@ParameterizedTest` - Data-driven tests
  - `@ValueSource` - Value parameters
  - `@CsvSource` - CSV-based parameters

**Use Case:** Testing JUnit 5 feature detection and advanced test generation

### springboot-sample

A complete Spring Boot 3.2.0 REST API application.

**Features:**
- Spring Boot 3.2.0
- Spring Web MVC
- Spring Data JPA with H2 database
- Bean Validation
- JUnit 5 testing with Spring Boot Test
- Mockito for mocking

**Structure:**
- `model/User.java` - JPA Entity with validation
- `repository/UserRepository.java` - JPA Repository
- `service/UserService.java` - Business logic layer
- `controller/UserController.java` - REST API endpoints
- `SpringBootSampleApplication.java` - Main application class
- `UserServiceTest.java` - Service layer tests
- `UserRepositoryTest.java` - Repository layer tests

**REST API Endpoints:**
- `GET /api/users` - Get all users
- `GET /api/users/{id}` - Get user by ID
- `GET /api/users/email/{email}` - Get user by email
- `POST /api/users` - Create new user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

**Use Case:** Testing Spring Boot detection, JPA analysis, and REST API test generation

### multi-module

A multi-module Maven project demonstrating inter-module dependencies.

**Features:**
- Maven multi-module structure
- Inter-module dependencies
- Java 17
- Clean module separation

**Modules:**
- `module1` - Depends on module2, contains Service1
- `module2` - Base module, contains Service2

**Use Case:** Testing multi-module project analysis and dependency graphing

## Usage

### Running Integration Tests

The integration tests use these sample projects:

```bash
# Run all integration tests
python -m pytest tests/test_integration.py -v

# Run specific test
python -m pytest tests/test_integration.py::TestRealJavaProjects::test_spring_boot_project_structure
```

### Manual Testing

Test the application manually with these samples:

```bash
# Analyze JUnit 4 sample
python -m src.main --project-path tests/samples/junit4-sample

# Analyze JUnit 5 sample
python -m src.main --project-path tests/samples/junit5-sample

# Analyze Spring Boot sample
python -m src.main --project-path tests/samples/springboot-sample

# Analyze multi-module sample
python -m src.main --project-path tests/samples/multi-module
```

### Example Queries

Try these queries when testing with sample projects:

For junit4-sample:
- "Analyze Java classes in this project"
- "List all test methods"
- "Show Maven dependencies"

For junit5-sample:
- "What JUnit 5 features are used?"
- "Find all parameterized tests"
- "Generate tests for StringValidator"

For springboot-sample:
- "Analyze Spring Boot application"
- "What are the REST API endpoints?"
- "Generate tests for UserController"
- "Show dependency tree"

For multi-module:
- "Analyze multi-module project"
- "Show inter-module dependencies"
- "Generate dependency graph"

## Building Projects

```bash
# Build JUnit 4 sample
cd tests/samples/junit4-sample && mvn clean package

# Build JUnit 5 sample
cd tests/samples/junit5-sample && mvn clean package

# Build Spring Boot sample
cd tests/samples/springboot-sample && mvn clean package

# Build multi-module project
cd tests/samples/multi-module && mvn clean package
```

## Running Tests

```bash
# Test JUnit 4 sample
cd tests/samples/junit4-sample && mvn clean test

# Test JUnit 5 sample
cd tests/samples/junit5-sample && mvn clean test

# Test Spring Boot sample
cd tests/samples/springboot-sample && mvn clean test

# Test multi-module project
cd tests/samples/multi-module && mvn clean test
```

## Running Spring Boot Sample

```bash
cd tests/samples/springboot-sample
mvn spring-boot:run
```

The application will be available at http://localhost:8080

## Modifying Samples

When modifying sample projects for testing:

1. Keep them simple and focused on specific features
2. Ensure they compile and test successfully
3. Follow Maven best practices
4. Use consistent naming conventions
5. Document any special features or requirements

## Adding New Samples

To add a new sample project:

1. Create a new directory in `tests/samples/`
2. Set up the project structure (pom.xml, src/main/java, src/test/java, etc.)
3. Add Java source files and tests
4. Update this README with:
   - Project description
   - Features
   - Structure
   - Use case
   - Usage examples
5. Add integration tests in `tests/test_integration.py` if needed

## Notes

- These samples are designed to test different aspects of the application:
  - Different Java versions (8, 11, 17)
  - Different testing frameworks (JUnit 4, JUnit 5)
  - Different project types (simple, Spring Boot, multi-module)
  - Different dependency configurations
- Each sample targets specific test scenarios
- Samples may be updated as new features are added to the application
