import unittest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch
from langchain_core.tools import tool
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import undecorated functions
from src.tools.file_tools import read_file_func, write_file_func, list_files_func, list_directories_func, delete_file_func
from src.tools.java_tools import analyze_java_class, list_java_classes
from src.tools.maven_tools import create_project_state
from src.utils.validation import ValidationError, FileOperationError

# Helper function to invoke LangChain tools
def invoke_tool(tool, **kwargs):
    """Invoke a LangChain tool with given arguments."""
    if hasattr(tool, 'invoke'):
        return tool.invoke(kwargs)
    else:
        return tool(**kwargs)


class TestFileTools(unittest.TestCase):
    """Unit tests for file_tools.py"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_read_file_success(self):
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("Test content", encoding="utf-8")

        result = read_file_func(str(test_file))

        self.assertEqual("Test content", result)

    def test_read_file_not_exists(self):
        result = read_file_func("/nonexistent/file.txt")

        self.assertIn("does not exist", result)

    def test_write_file_success(self):
        test_file = self.temp_dir / "test.txt"

        result = write_file_func(str(test_file), "New content")

        self.assertIn("Successfully wrote", result)
        self.assertTrue(test_file.exists())

    def test_write_file_creates_directories(self):
        test_file = self.temp_dir / "newdir" / "test.txt"

        result = write_file_func(str(test_file), "Content")

        self.assertTrue(test_file.exists())
        self.assertTrue((self.temp_dir / "newdir").exists())

    def test_list_files(self):
        test_file1 = self.temp_dir / "file1.txt"
        test_file2 = self.temp_dir / "file2.txt"
        test_file1.write_text("Content 1", encoding="utf-8")
        test_file2.write_text("Content 2", encoding="utf-8")

        result = list_files_func(str(self.temp_dir))

        self.assertIn("file1.txt", result)
        self.assertIn("file2.txt", result)

    def test_list_directories(self):
        test_dir = self.temp_dir / "subdir"
        test_dir.mkdir()

        result = list_directories_func(str(self.temp_dir))

        self.assertIn("subdir", result)

    def test_delete_file(self):
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("To delete", encoding="utf-8")

        result = delete_file_func(str(test_file))

        self.assertIn("Successfully deleted", result)
        self.assertFalse(test_file.exists())

    def test_delete_file_not_exists(self):
        result = delete_file_func("/nonexistent/file.txt")

        self.assertIn("does not exist", result)


class TestJavaTools(unittest.TestCase):
    """Unit tests for java_tools.py"""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_list_java_classes_success(self):
        java_file = self.temp_dir / "TestClass.java"
        java_file.write_text("public class TestClass {}", encoding="utf-8")

        result = invoke_tool(list_java_classes, directory=str(self.temp_dir))

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertEqual("TestClass", result[0]["name"])

    def test_list_java_classes_empty(self):
        empty_dir = self.temp_dir / "empty"
        empty_dir.mkdir()

        result = invoke_tool(list_java_classes, directory=str(empty_dir))

        self.assertEqual([], result)

    def test_analyze_java_class_success(self):
        java_file = self.temp_dir / "TestClass.java"
        java_content = """package com.example;

public class TestClass {
    private String name;

    public TestClass(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }
}
"""
        java_file.write_text(java_content, encoding="utf-8")

        result = invoke_tool(analyze_java_class, path=str(java_file))

        self.assertEqual("TestClass", result["name"])
        self.assertEqual("com.example", result["package"])
        self.assertTrue(len(result["fields"]) >= 1)
        self.assertTrue(len(result["methods"]) >= 1)

class TestMavenTools(unittest.TestCase):
    """Unit tests for maven_tools.py"""

    def test_create_project_state_success(self):
        with patch('pathlib.Path.cwd', return_value=Path.cwd()):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_dir', return_value=True):
                    result = invoke_tool(create_project_state, project_path=".")

                    self.assertIsInstance(result, dict)
                    self.assertIn("project_path", result)
                    self.assertIn("java_classes", result)
                    self.assertIn("dependencies", result)


if __name__ == '__main__':
    unittest.main()
