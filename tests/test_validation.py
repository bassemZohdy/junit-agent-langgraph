import unittest
import tempfile
import shutil
from pathlib import Path
from ..src.utils.validation import (
    validate_not_none,
    validate_not_empty,
    validate_file_exists,
    validate_directory_exists,
    validate_path,
    validate_class_name,
    validate_method_name,
    validate_field_name,
    validate_positive_integer,
    validate_not_empty,
    validate_maven_goal,
    validate_maven_scope,
    validate_in_allowed_values
)
from ..src.exceptions.handler import ValidationError


class TestValidationUtils(unittest.TestCase):
    """Unit tests for validation.py"""
    
    def test_validate_not_none_valid(self):
        self.assertIsNone(validate_not_none(None))
    
    def test_validate_not_none_invalid(self):
        with self.assertRaises(ValidationError):
            validate_not_none(None, "test_field")
    
    def test_validate_not_empty_valid(self):
        self.assertEqual("test", validate_not_empty("test"))
    
    def test_validate_not_empty_invalid_string(self):
        with self.assertRaises(ValidationError):
            validate_not_empty("  ", "test_field")
    
    def test_validate_not_empty_invalid(self):
        with self.assertRaises(ValidationError):
            validate_not_empty("", "test_field")
    
    def test_validate_path_valid(self):
        path_obj = validate_path("/valid/path")
        self.assertTrue(isinstance(path_obj, Path))
    
    def test_validate_path_traversal_rejected(self):
        with self.assertRaises(ValidationError):
            validate_path("../path")
    
    def test_validate_path_absolute_allowed(self):
        path_obj = validate_path("/absolute/path", allow_absolute=True)
        self.assertTrue(isinstance(path_obj, Path))
    
    def test_validate_class_name_valid(self):
        validate_class_name("ValidClass")
    
    def test_validate_class_name_invalid_lowercase(self):
        with self.assertRaises(ValidationError):
            validate_class_name("invalidClass")
    
    def test_validate_class_name_invalid_start_digit(self):
        with self.assertRaises(ValidationError):
            validate_class_name("1InvalidClass")
    
    def test_validate_method_name_valid(self):
        validate_method_name("validMethod")
    
    def test_validate_method_name_invalid_uppercase(self):
        with self.assertRaises(ValidationError):
            validate_method_name("InvalidMethod")
    
    def test_validate_field_name_valid(self):
        validate_field_name("validField")
    
    def test_validate_field_name_invalid_uppercase(self):
        with self.assertRaises(ValidationError):
            validate_field_name("invalidField")
    
    def test_validate_range_valid(self):
        validate_range(5, "value", 1, 10)
        validate_range(7, "value", 1, 10)
        validate_range(5, "value", 1, 5)
        validate_range(5, "value", 5, 10)
    
    def test_validate_range_invalid_min(self):
        with self.assertRaises(ValidationError):
            validate_range(5, "value", 10, 10)
    
    def test_validate_range_invalid_max(self):
        with self.assertRaises(ValidationError):
            validate_range(5, "value", 1, 0)
    
    def test_validate_in_allowed_values_valid(self):
        validate_in_allowed_values("value", "test_field", ["value1", "value2", "value3"])
    
    def test_validate_in_allowed_values_invalid(self):
        with self.assertRaises(ValidationError):
            validate_in_allowed_values("invalid", "test_field", ["value1", "value2", "value3"])
    
    def test_validate_positive_integer_valid(self):
        validate_positive_integer(5, "value")
        validate_positive_integer(100, "value")
    
    def test_validate_positive_integer_invalid_zero(self):
        with self.assertRaises(ValidationError):
            validate_positive_integer(0, "value")
    
    def test_validate_positive_integer_invalid_negative(self):
        with self.assertRaises(ValidationError):
            validate_positive_integer(-5, "value")
    
    def test_validate_maven_goal_valid(self):
        validate_maven_goal("compile")
        validate_maven_goal("test")
        validate_maven_goal("package")
        validate_maven_goal("clean")
    
    def test_validate_maven_goal_invalid(self):
        with self.assertRaises(ValidationError):
            validate_maven_goal("invalid")
    
    def test_validate_maven_scope_valid(self):
        validate_maven_scope("compile")
        validate_maven_scope("test")
        validate_maven_scope("provided")
        validate_maven_scope("runtime")
    
    def test_validate_maven_scope_invalid(self):
        with self.assertRaises(ValidationError):
            validate_maven_scope("invalid")


if __name__ == '__main__':
    unittest.main()
