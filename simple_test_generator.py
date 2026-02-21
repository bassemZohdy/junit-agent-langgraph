#!/usr/bin/env python3
"""
Simple Test Generator - Generates JUnit tests for sample projects
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def generate_calculator_test():
    """Generate CalculatorTest.java for junit4-sample"""
    test_content = """package com.example;

import org.junit.Test;
import static org.junit.Assert.*;

public class CalculatorTest {
    
    @Test
    public void testAdd() {
        Calculator calc = new Calculator();
        assertEquals(5, calc.add(2, 3));
    }
    
    @Test
    public void testAddNegative() {
        Calculator calc = new Calculator();
        assertEquals(-1, calc.add(-2, 1));
    }
    
    @Test
    public void testAddZero() {
        Calculator calc = new Calculator();
        assertEquals(5, calc.add(5, 0));
    }
    
    @Test
    public void testSubtract() {
        Calculator calc = new Calculator();
        assertEquals(1, calc.subtract(3, 2));
    }
    
    @Test
    public void testSubtractNegativeResult() {
        Calculator calc = new Calculator();
        assertEquals(-2, calc.subtract(2, 4));
    }
    
    @Test
    public void testMultiply() {
        Calculator calc = new Calculator();
        assertEquals(6, calc.multiply(2, 3));
    }
    
    @Test
    public void testMultiplyByZero() {
        Calculator calc = new Calculator();
        assertEquals(0, calc.multiply(5, 0));
    }
    
    @Test
    public void testMultiplyNegative() {
        Calculator calc = new Calculator();
        assertEquals(-6, calc.multiply(-2, 3));
    }
    
    @Test
    public void testDivide() {
        Calculator calc = new Calculator();
        assertEquals(2, calc.divide(6, 3));
    }
    
    @Test
    public void testDivideByZero() {
        Calculator calc = new Calculator();
        try {
            calc.divide(1, 0);
            fail("Expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            assertTrue(true);
        }
    }
    
    @Test
    public void testDivideNegative() {
        Calculator calc = new Calculator();
        assertEquals(-2, calc.divide(-6, 3));
    }
}
"""
    return test_content


def generate_stringvalidator_test():
    """Generate StringValidatorTest.java for junit5-sample"""
    test_content = """package com.example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.junit.jupiter.params.provider.EmptySource;
import org.junit.jupiter.params.provider.NullSource;
import static org.junit.jupiter.api.Assertions.*;

public class StringValidatorTest {
    
    @Test
    public void testValidEmail() {
        assertTrue(StringValidator.isValidEmail("test@example.com"));
    }
    
    @Test
    @ParameterizedTest
    @ValueSource(strings = {"", " ", "test@test"})
    public void testInvalidEmail(String email) {
        assertFalse(StringValidator.isValidEmail(email));
    }
    
    @NullSource
    @Test
    public void testEmailNull() {
        assertFalse(StringValidator.isValidEmail(null));
    }
    
    @EmptySource
    @Test
    public void testEmailEmpty() {
        assertFalse(StringValidator.isValidEmail(""));
    }
    
    @Test
    @DisplayName("Test email with special characters")
    public void testEmailWithSpecialChars() {
        assertFalse(StringValidator.isValidEmail("test@@example.com"));
    }
    
    @Test
    @DisplayName("Test email with numbers")
    public void testEmailWithNumbers() {
        assertTrue(StringValidator.isValidEmail("test123@example.com"));
    }
}
"""
    return test_content


def main():
    """Main function to generate test classes"""
    script_dir = Path(__file__).parent
    samples_dir = script_dir / "tests" / "samples"
    
    print("\n" + "="*60)
    print("SIMPLE TEST GENERATOR")
    print("="*60 + "\n")
    
    # Generate tests for junit4-sample
    print("Generating tests for junit4-sample...")
    
    junit4_sample = samples_dir / "junit4-sample"
    test_dir = junit4_sample / "src" / "test" / "java" / "com" / "example"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate CalculatorTest.java
    calculator_test = generate_calculator_test()
    calculator_test_path = test_dir / "CalculatorTest.java"
    
    with open(calculator_test_path, 'w', encoding='utf-8') as f:
        f.write(calculator_test)
    
    print(f"  [OK] Created: {calculator_test_path.relative_to(script_dir)}")
    
    # Generate tests for junit5-sample
    print("\nGenerating tests for junit5-sample...")
    
    junit5_sample = samples_dir / "junit5-sample"
    test_dir = junit5_sample / "src" / "test" / "java" / "com" / "example"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate StringValidatorTest.java
    stringvalidator_test = generate_stringvalidator_test()
    stringvalidator_test_path = test_dir / "StringValidatorTest.java"
    
    with open(stringvalidator_test_path, 'w', encoding='utf-8') as f:
        f.write(stringvalidator_test)
    
    print(f"  [OK] Created: {stringvalidator_test_path.relative_to(script_dir)}")
    
    # Summary
    print("\n" + "="*60)
    print("TEST GENERATION COMPLETE")
    print("="*60 + "\n")
    
    print("Generated test files:")
    print(f"  1. {calculator_test_path.relative_to(script_dir)}")
    print(f"  2. {stringvalidator_test_path.relative_to(script_dir)}")
    
    print("\nTo run the tests:")
    print(f"  cd tests/samples/junit4-sample && mvn test")
    print(f"  cd tests/samples/junit5-sample && mvn test")
    
    print("\nGenerated tests are ready!")


if __name__ == "__main__":
    main()
