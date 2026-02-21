# Integration Tests - Sample Projects Analysis

**Date**: February 21, 2026
**Purpose**: Verify sample projects and test generation workflow

## 📋 Sample Projects Overview

### 1. junit4-sample

**Description**: Simple Maven project using JUnit 4 for testing

**Features**:
- Java 8 compatibility
- JUnit 4.13.2
- Calculator class with basic operations

**Structure**:
```
junit4-sample/
├── pom.xml
├── src/
│   └── main/
│       └── java/
│           └── com/
│               └── example/
│                   └── Calculator.java
├── src/
│   └── test/
│       └── java/
│           └── com/
│               └── example/
│                   └── CalculatorTest.java  ← TO BE GENERATED
└── README.md
```

**Calculator.java Contents**:
```java
package com.example;

public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    public int subtract(int a, int b) {
        return a - b;
    }

    public int multiply(int a, int b) {
        return a * b;
    }

    public int divide(int a, int b) {
        if (b == 0) {
            throw new IllegalArgumentException("Cannot divide by zero");
        }
        return a / b;
    }
}
```

### 2. junit5-sample

**Description**: Maven project using JUnit 5 (Jupiter) for testing

**Features**:
- Java 11 compatibility
- JUnit 5.10.0
- StringValidator class with advanced features
- Parameterized tests
- Custom display names

**Structure**:
```
junit5-sample/
├── pom.xml
├── src/
│   └── main/
│       └── java/
│           └── com/
│               └── example/
│                   └── StringValidator.java
├── src/
│   └── test/
│       └── java/
│           └── com/
│               └── example/
│                   └── StringValidatorTest.java  ← TO BE GENERATED
└── README.md
```

### 3. springboot-sample

**Description**: Complete Spring Boot 3.2.0 REST API application

**Features**:
- Spring Boot 3.2.0
- Spring Web MVC
- Spring Data JPA with H2 database
- Bean validation
- JUnit 5 testing with Spring Boot Test
- Mockito for mocking

**Structure**:
```
springboot-sample/
├── pom.xml
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           ├── SpringBootSampleApplication.java
│   │   │           ├── model/
│   │   │           │   └── User.java
│   │   │           ├── repository/
│   │   │           │   └── UserRepository.java
│   │   │           ├── service/
│   │   │           │   └── UserService.java
│   │   │           └── controller/
│   │   │               └── UserController.java
│   └── test/
│       └── java/
│           └── com/
│               └── example/
│                   ├── UserServiceTest.java  ← TO BE GENERATED
│                   ├── UserRepositoryTest.java  ← TO BE GENERATED
│                   └── UserControllerTest.java  ← TO BE GENERATED
└── application.properties
```

### 4. multi-module

**Description**: Multi-module Maven project with inter-module dependencies

**Features**:
- Maven multi-module structure
- Module 1 contains Service1
- Module 2 depends on Module 1
- Demonstrates inter-module dependency graphing

## 🧪 Test Generation Workflow

### Expected Test Classes

For each sample project, the application should generate:

**junit4-sample**:
- `CalculatorTest.java` - Test all Calculator methods

**junit5-sample**:
- `StringValidatorTest.java` - Test StringValidator features

**springboot-sample**:
- `UserServiceTest.java` - Service layer tests
- `UserRepositoryTest.java` - Repository layer tests
- `UserControllerTest.java` - REST API endpoint tests

**multi-module**:
- Tests for both modules
- Tests demonstrating inter-module dependencies

## 🚀 Running Application on Samples

### Prerequisites

1. **Ollama Service Running**:
   ```bash
   ollama serve
   ```

2. **Verify Ollama Model**:
   ```bash
   ollama list
   # Should show llama3.2 or other available models
   ```

### Running on Each Sample

#### junit4-sample

```bash
python -m src.main --project-path tests/samples/junit4-sample
```

**Expected Output**:
- Analysis of Calculator.java
- Generation of CalculatorTest.java
- Test class saved to `tests/samples/junit4-sample/src/test/java/com/example/CalculatorTest.java`

#### junit5-sample

```bash
python -m src.main --project-path tests/samples/junit5-sample
```

**Expected Output**:
- Analysis of StringValidator.java
- Generation of StringValidatorTest.java with JUnit 5 features
- Test class saved to `tests/samples/junit5-sample/src/test/java/com/example/StringValidatorTest.java`

#### springboot-sample

```bash
python -m src.main --project-path tests/samples/springboot-sample
```

**Expected Output**:
- Analysis of all Java classes
- Detection of Spring Boot features
- Generation of test classes with Spring Boot Test annotations
- Tests for service, repository, and controller layers
- Test classes saved to `tests/samples/springboot-sample/src/test/java/com/example/`

#### multi-module

```bash
python -m src.main --project-path tests/samples/multi-module
```

**Expected Output**:
- Analysis of both modules
- Dependency graph generation
- Test classes for each module
- Tests demonstrating inter-module dependencies

## 🔍 Verification Steps

### 1. Check Generated Test Files

After running the application on a sample:

```bash
# Verify test file was created
ls tests/samples/[sample-name]/src/test/java/

# Check test file contents
cat tests/samples/[sample-name]/src/test/java/com/example/[TestClassName].java
```

### 2. Run Generated Tests

```bash
# Run Maven test
cd tests/samples/[sample-name]
mvn test

# Or run with specific test
mvn test -Dtest=CalculatorTest
```

### 3. Verify Test Coverage

```bash
# Run Maven test with coverage
cd tests/samples/[sample-name]
mvn test jacoco:report

# Check coverage report
cat target/site/jacoco/index.html
```

## 📝 Sample Test Class Expectations

### junit4-sample/CalculatorTest.java

**Expected Content**:
```java
package com.example;

import org.junit.Test;
import static org.junit.Assert.*;

public class CalculatorTest {
    @Test
    public void testAdd() {
        Calculator calc = new Calculator();
        assertEquals(5, calc.add(2, 3));
    }

    @Test
    public void testSubtract() {
        Calculator calc = new Calculator();
        assertEquals(1, calc.subtract(3, 2));
    }

    @Test
    public void testMultiply() {
        Calculator calc = new Calculator();
        assertEquals(6, calc.multiply(2, 3));
    }

    @Test
    public void testDivide() {
        Calculator calc = new Calculator();
        assertEquals(2, calc.divide(6, 3));
    }

    @Test(expected = IllegalArgumentException.class)
    public void testDivideByZero() {
        Calculator calc = new Calculator();
        calc.divide(1, 0);
    }
}
```

### junit5-sample/StringValidatorTest.java

**Expected Features**:
- `@Test` annotations
- `@DisplayName` for custom test names
- `@ParameterizedTest` for data-driven tests
- `@ValueSource` or `@CsvSource` for parameters
- `@NullSource` for null value testing
- `@EmptySource` for empty value testing

### springboot-sample/Test Classes

**Expected Features**:
- `@SpringBootTest` annotation
- `@WebMvcTest` for controller tests
- `@DataJpaTest` for repository tests
- `@MockBean` or `@Mock` for mocking
- `@Autowired` for dependency injection
- REST Assured for endpoint testing

## 🎯 Integration Test Verification

### Running Integration Tests

```bash
# Run all integration tests
python -m pytest tests/test_integration.py -v

# Run specific test
python -m pytest tests/test_integration.py::TestIntegrationWorkflows::test_complete_analysis_workflow -v
```

### Expected Integration Test Results

| Test | Purpose | Expected Result |
|-------|---------|----------------|
| test_complete_analysis_workflow | Analyze project structure | ✅ Finds Calculator class |
| test_code_generation_workflow | Generate getters/setters | ✅ Generates correct code |
| test_maven_project_workflow | Analyze Maven project | ✅ Detects Maven metadata |
| test_state_management_workflow | Test transactions | ✅ State saved correctly |
| test_access_control_workflow | Test permissions | ✅ Access denied to restricted |
| test_security_validation_workflow | Test security | ✅ Detects malicious inputs |
| test_validation_workflow | Test validation | ✅ Validates class names |
| test_git_integration_workflow | Test Git | ✅ Detects Git repository |
| test_concurrent_operations_workflow | Test concurrency | ✅ Processes 2 files |

## 📊 Test Quality Checks

### Manual Verification

After generating test classes, verify:

1. **Imports**:
   - All necessary imports present
   - No unused imports

2. **Test Methods**:
   - All public methods tested
   - Edge cases covered (null values, boundary conditions)
   - Exception cases tested where applicable

3. **Assertions**:
   - Appropriate assertions used (assertEquals, assertTrue, etc.)
   - Clear test names
   - Descriptive assertion messages (optional)

4. **Test Structure**:
   - Proper package declaration
   - Class name ends with "Test"
   - Test methods annotated with `@Test` (JUnit 4) or `@Test` (JUnit 5)

5. **Spring Boot Specific**:
   - Proper annotations (@SpringBootTest, @WebMvcTest, etc.)
   - Mocking where appropriate
   - REST Assured for endpoint tests
   - @Transactional for repository tests if needed

## 🚀 Quick Start Guide

### 1. Start Ollama

```bash
# Terminal 1 - Run Ollama
ollama serve
```

### 2. Run Application on Sample

```bash
# Terminal 2 - Run JUnit Agent
cd junit-agent-langgraph
python -m src.main --project-path tests/samples/junit4-sample
```

### 3. Follow CLI Prompts

The application will guide you through:
1. Initial project analysis
2. Class identification
3. Test generation for each class
4. Test review and validation
5. Test execution and fixing (if configured)

### 4. Verify Results

```bash
# Navigate to sample project
cd tests/samples/junit4-sample

# Check generated test files
ls src/test/java/com/example/

# Run Maven tests
mvn test
```

## 📁 Sample Projects Location

All sample projects are located in:
```
tests/samples/
├── junit4-sample/
├── junit5-sample/
├── springboot-sample/
└── multi-module/
```

Each sample includes:
- `pom.xml` - Maven project file
- `src/main/java/` - Java source code
- `src/test/java/` - Test directory (initially empty, tests generated here)
- `README.md` - Project documentation

## ✅ Completion Criteria

Integration testing is complete when:

1. ✅ All sample projects analyzed successfully
2. ✅ Test classes generated for all main classes
3. ✅ Generated tests compile successfully
4. ✅ Generated tests run successfully with Maven
5. ✅ All integration tests in `test_integration.py` pass
6. ✅ Test coverage meets expectations (> 80%)
7. ✅ No critical errors in test generation workflow

## 🎯 Next Steps

1. **Run Application**: Generate test classes for each sample
2. **Verify Tests**: Ensure generated tests compile and run
3. **Run Integration Tests**: Validate workflow end-to-end
4. **Check Coverage**: Verify test coverage is adequate
5. **Document Issues**: Record any problems or edge cases
6. **Refine Prompts**: Adjust LLM prompts if tests are low quality

---

**Last Updated**: February 21, 2026
