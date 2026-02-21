#!/usr/bin/env python3
"""
Test Generation Demo Script

This script demonstrates the test generation workflow on sample projects
without requiring the full application to run.

Usage:
    python test_generation_demo.py --project tests/samples/junit4-sample
"""

import sys
import os
from pathlib import Path
import argparse


def analyze_sample_project(project_path: str):
    """Analyze a sample project and show what tests should be generated."""
    project_dir = Path(project_path)
    
    print(f"\n{'='*60}")
    print(f"Analyzing: {project_dir.name}")
    print(f"{'='*60}\n")
    
    # Find Java source files
    java_files = list(project_dir.rglob("src/main/java/**/*.java"))
    
    print(f"Found {len(java_files)} Java source files:")
    for java_file in java_files:
        relative_path = java_file.relative_to(project_dir)
        print(f"  - {relative_path}")
    
    # Determine expected test files
    print(f"\nExpected test files:")
    for java_file in java_files:
        relative_path = java_file.relative_to(project_dir)
        # Convert source path to test path
        test_path = str(relative_path).replace(
            "src/main/java",
            "src/test/java"
        ).replace(".java", "Test.java")
        
        print(f"  - {test_path}")
    
    print(f"\nTest file location: {project_dir / 'src/test/java'}")
    print(f"Source file location: {project_dir / 'src/main/java'}")
    
    # Check if test directory exists
    test_dir = project_dir / "src/test/java"
    if test_dir.exists():
        existing_tests = list(test_dir.rglob("**/*Test.java"))
        print(f"\nExisting test files ({len(existing_tests)}):")
        for test_file in existing_tests:
            relative_path = test_file.relative_to(project_dir)
            print(f"  - {relative_path}")
    else:
        print(f"\nTest directory does not exist (will be created during generation)")
    
    # Show project info
    pom_file = project_dir / "pom.xml"
    if pom_file.exists():
        print(f"\n[OK] Maven project detected (pom.xml exists)")
        print(f"  Run tests with: cd {project_dir.name} && mvn test")
    else:
        print(f"\n[!] No pom.xml found - may not be a Maven project")
    
    return {
        "project_name": project_dir.name,
        "java_files": len(java_files),
        "test_directory_exists": test_dir.exists(),
        "maven_project": pom_file.exists()
    }


def show_test_example(project_name: str):
    """Show an example of what a generated test should look like."""
    print(f"\n{'='*60}")
    print(f"Example Test for {project_name}")
    print(f"{'='*60}\n")
    
    examples = {
        "junit4-sample": """package com.example;

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
    
    @Test(expected = IllegalArgumentException.class)
    public void testDivideByZero() {
        Calculator calc = new Calculator();
        calc.divide(1, 0);
    }
}""",
        
        "junit5-sample": """package com.example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.junit.jupiter.api.Assertions.*;

public class StringValidatorTest {
    
    @Test
    public void testValidEmail() {
        StringValidator validator = new StringValidator();
        assertTrue(validator.isValidEmail("test@example.com"));
    }
    
    @ParameterizedTest
    @ValueSource(strings = {"", " ", "test@test"})
    public void testInvalidEmail(String email) {
        StringValidator validator = new StringValidator();
        assertFalse(validator.isValidEmail(email));
    }
    
    @Test
    @DisplayName("Test email with special characters")
    public void testEmailWithSpecialChars() {
        StringValidator validator = new StringValidator();
        assertFalse(validator.isValidEmail("test@@example.com"));
    }
}""",
        
        "springboot-sample": """package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
public class UserServiceTest {
    
    @Autowired
    private UserService userService;
    
    @Test
    public void testGetUserById() {
        // Test implementation
        assertNotNull(userService.getUserById(1L));
    }
    
    @Test
    public void testCreateUser() {
        // Test implementation
        User user = userService.createUser(
            new User("test@example.com", "Test User")
        );
        assertNotNull(user.getId());
    }
    
    @Test
    public void testGetAllUsers() {
        // Test implementation
        assertNotNull(userService.getAllUsers());
        assertFalse(userService.getAllUsers().isEmpty());
    }
}"""
    }
    
    if project_name in examples:
        print(examples[project_name])
    else:
        print(f"No example available for {project_name}")


def main():
    parser = argparse.ArgumentParser(
        description="Test Generation Demo - Analyze sample projects"
    )
    parser.add_argument(
        "--project",
        type=str,
        required=True,
        help="Path to sample project"
    )
    parser.add_argument(
        "--show-example",
        action="store_true",
        help="Show example test code"
    )
    
    args = parser.parse_args()
    
    # Analyze project
    analysis = analyze_sample_project(args.project)
    
    # Show example if requested
    if args.show_example:
        show_test_example(analysis["project_name"])
    
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")
    print(f"Project: {analysis['project_name']}")
    print(f"Java files: {analysis['java_files']}")
    print(f"Test directory exists: {analysis['test_directory_exists']}")
    print(f"Maven project: {analysis['maven_project']}")
    print()
    print("To generate tests with the full application:")
    print(f"  python -m src.main --project-path {args.project}")
    print()
    print("To run integration tests:")
    print("  python -m pytest tests/test_integration.py -v")


if __name__ == "__main__":
    main()
