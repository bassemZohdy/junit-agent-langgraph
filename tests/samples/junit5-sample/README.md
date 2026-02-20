# JUnit 5 Sample Project

This is a sample Maven project using JUnit 5 (Jupiter) for testing.

## Structure

- `src/main/java/com/example/StringValidator.java` - String validation class
- `src/test/java/com/example/StringValidatorTest.java` - JUnit 5 tests with features:
  - `@Test` for standard tests
  - `@DisplayName` for readable test names
  - `@ParameterizedTest` for data-driven tests
  - `@ValueSource` for parameterized values
  - `@CsvSource` for CSV parameter data

## Build and Test

```bash
cd junit5
mvn clean test
```

## Package

```bash
mvn package
```

The JAR will be created in `target/junit5-sample-1.0.0.jar`

## JUnit 5 Features Used

- `@BeforeEach` - Setup method before each test
- `@Test` - Standard test method annotation
- `@DisplayName` - Custom test name
- `@ParameterizedTest` - Data-driven testing
- `@ValueSource` - Simple value parameters
- `@CsvSource` - CSV-based parameters
- Assertions from `org.junit.jupiter.api.Assertions`
