# Spring Boot Sample Project

This is a sample Maven project using Spring Boot 3.2.0 with a complete REST API implementation.

## Features

- Spring Boot 3.2.0
- Spring Web (REST Controller)
- Spring Data JPA (H2 in-memory database)
- Bean Validation
- JUnit 5 testing
- Mockito for mocking

## Structure

```
src/main/java/com/example/
├── model/
│   └── User.java           # JPA Entity with validation
├── repository/
│   └── UserRepository.java # JPA Repository
├── service/
│   └── UserService.java    # Business logic layer
├── controller/
│   └── UserController.java # REST API endpoints
└── SpringBootSampleApplication.java

src/main/resources/
└── application.properties    # H2 database configuration

src/test/java/com/example/
├── UserServiceTest.java     # Service layer tests
└── UserRepositoryTest.java   # Repository layer tests
```

## REST API Endpoints

- `GET /api/users` - Get all users
- `GET /api/users/{id}` - Get user by ID
- `GET /api/users/email/{email}` - Get user by email
- `POST /api/users` - Create new user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

## Build and Test

```bash
cd springboot
mvn clean test
```

## Run Application

```bash
mvn spring-boot:run
```

The application will start on `http://localhost:8080`

## Package

```bash
mvn package
```

The executable JAR will be created in `target/springboot-sample-1.0.0.jar`

## Testing

Run the executable JAR:
```bash
java -jar target/springboot-sample-1.0.0.jar
```

Test the API:
```bash
# Create a user
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","age":30}'

# Get all users
curl http://localhost:8080/api/users

# Get user by ID
curl http://localhost:8080/api/users/1
```

## User Model

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

Validation rules:
- `name`: Required, 2-50 characters
- `email`: Required, valid email format
- `age`: Required, 0-150 range
