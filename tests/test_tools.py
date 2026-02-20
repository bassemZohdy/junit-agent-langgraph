import unittest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch
from langchain_core.tools import tool
from ..src.tools.file_tools import read_file, write_file, list_files, list_directories, delete_file
from ..src.tools.java_tools import find_java_files, create_java_class_state, get_java_classes, get_java_methods
from ..src.tools.maven_tools import maven_build, maven_test, maven_clean, create_project_state
from ..src.utils.validation import ValidationError, FileOperationError


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
        
        result = read_file(str(test_file))
        
        self.assertEqual("Test content", result)
    
    def test_read_file_not_exists(self):
        result = read_file("/nonexistent/file.txt")
        
        self.assertIn("Error", result)
        self.assertIn("does not exist", result)
    
    def test_write_file_success(self):
        test_file = self.temp_dir / "test.txt"
        
        result = write_file(str(test_file), "New content")
        
        self.assertIn("Successfully wrote", result)
        self.assertTrue(test_file.exists())
    
    def test_write_file_creates_directories(self):
        test_file = self.temp_dir / "newdir" / "test.txt"
        
        result = write_file(str(test_file), "Content")
        
        self.assertTrue(test_file.exists())
        self.assertTrue((self.temp_dir / "newdir").exists())
    
    def test_list_files(self):
        test_file1 = self.temp_dir / "file1.txt"
        test_file2 = self.temp_dir / "file2.txt"
        test_file1.write_text("Content 1", encoding="utf-8")
        test_file2.write_text("Content 2", encoding="utf-8")
        
        result = list_files(str(self.temp_dir))
        
        self.assertIn("file1.txt", result)
        self.assertIn("file2.txt", result)
    
    def test_list_directories(self):
        test_dir = self.temp_dir / "subdir"
        test_dir.mkdir()
        
        result = list_directories(str(self.temp_dir))
        
        self.assertIn("subdir", result)
    
    def test_delete_file(self):
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("To delete", encoding="utf-8")
        
        result = delete_file(str(test_file))
        
        self.assertIn("Successfully deleted", result)
        self.assertFalse(test_file.exists())
    
    def test_delete_file_not_exists(self):
        result = delete_file("/nonexistent/file.txt")
        
        self.assertIn("Error", result)
        self.assertIn("does not exist", result)


class TestJavaTools(unittest.TestCase):
    """Unit tests for java_tools.py"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_find_java_files_success(self):
        java_file = self.temp_dir / "TestClass.java"
        java_file.write_text("public class TestClass {}", encoding="utf-8")
        
        result = find_java_files(str(self.temp_dir))
        
        self.assertIn("TestClass.java", result)
    
    def test_find_java_files_empty(self):
        empty_dir = self.temp_dir / "empty"
        empty_dir.mkdir()
        
        result = find_java_files(str(empty_dir))
        
        self.assertIn("No Java files found", result)
    
    def test_create_java_class_state_success(self):
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
        
        result = create_java_class_state(str(java_file))
        
        self.assertEqual("TestClass", result["name"])
        self.assertEqual("com.example", result["package"])
        self.assertTrue(len(result["fields"]) >= 1)
        self.assertTrue(len(result["methods"]) >= 1)
    
    def test_get_java_classes_success(self):
        java_file = self.temp_dir / "MultiClass.java"
        java_content = """
package com.example;

public class FirstClass {}
public class SecondClass {}
"""
        java_file.write_text(java_content, encoding="utf-8")
        
        result = get_java_classes(str(java_file))
        
        self.assertIn("FirstClass", result)
        self.assertIn("SecondClass", result)
    
    def test_get_java_methods_success(self):
        java_file = self.temp_dir / "MethodClass.java"
        java_content = """
package com.example;

public class MethodClass {
    public void method1() {}
    public void method2() {}
}
"""
        java_file.write_text(java_content, encoding="utf-8")
        
        result = get_java_methods(str(java_file), "MethodClass")
        
        self.assertIn("method1", result)
        self.assertIn("method2", result)


class TestMavenTools(unittest.TestCase):
    """Unit tests for maven_tools.py"""
    
    def test_create_project_state_success(self):
        with patch('pathlib.Path.cwd', return_value=Path.cwd()):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_dir', return_value=True):
                    result = create_project_state(".")
                    
                    self.assertIsInstance(result, dict)
                    self.assertIn("project_path", result)
                    self.assertIn("java_classes", result)
                    self.assertIn("dependencies", result)


if __name__ == '__main__':
    unittest.main()
