import unittest
import asyncio
from pathlib import Path
import tempfile
import shutil
import os
from unittest.mock import Mock, AsyncMock, patch
from langchain_core.messages import HumanMessage, AIMessage
from ..src.states.project import ProjectState, JavaClassState
from ..src.graphs.workflow import create_workflow
from ..src.tools.java_tools import find_java_files, create_java_class_state
from ..src.tools.maven_tools import create_project_state, maven_build
from ..src.tools.code_generation_tools import generate_getters_setters
from ..src.tools.git_tools import git_status, git_is_repository
from ..src.utils.state_manager import get_state_manager, StateManager
from ..src.utils.access_control import get_access_control_manager
from ..src.utils.validation import validate_class_name, validate_project_directory, ValidationError
from ..src.utils.security import check_for_secrets

SAMPLES_DIR = Path(__file__).resolve().parent / "samples"


class TestIntegrationWorkflows(unittest.TestCase):
    """Integration tests for complete workflows using sample projects"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
        get_state_manager().reset()
        get_access_control_manager().reset()
    
    def test_complete_analysis_workflow(self):
        """Test complete project analysis workflow with junit4-sample"""
        sample_project = SAMPLES_DIR / "junit4-sample"
        self.assertTrue(sample_project.exists(), f"Sample project not found at {sample_project}")
        
        java_files = find_java_files(str(sample_project))
        self.assertGreater(len(java_files), 0, "Should find Java files in sample project")
        
        calculator_found = False
        for file_path in java_files:
            class_state = create_java_class_state(file_path)
            self.assertIsNotNone(class_state)
            
            if class_state["name"] == "Calculator":
                calculator_found = True
                self.assertEqual("com.example", class_state["package"])
                self.assertGreater(len(class_state["fields"]), 0)
                self.assertGreater(len(class_state["methods"]), 0)
        
        self.assertTrue(calculator_found, "Should find Calculator class")
    
    def test_code_generation_workflow(self):
        """Test code generation workflow using junit4-sample"""
        sample_project = SAMPLES_DIR / "junit4-sample"
        calculator_file = sample_project / "src" / "main" / "java" / "com" / "example" / "Calculator.java"
        
        self.assertTrue(calculator_file.exists())
        
        class_state = create_java_class_state(str(calculator_file))
        self.assertIsNotNone(class_state)
        
        result = generate_getters_setters(
            str(calculator_file),
            "Calculator",
            class_state["fields"]
        )
        self.assertIn("getOperand1", result)
        self.assertIn("setOperand1", result)
    
    def test_maven_project_workflow(self):
        """Test Maven project analysis workflow with junit4-sample"""
        sample_project = SAMPLES_DIR / "junit4-sample"
        self.assertTrue(sample_project.exists())
        
        project_state = create_project_state(str(sample_project))
        self.assertIsNotNone(project_state)
        self.assertEqual("com.example", project_state["maven_group_id"])
        self.assertEqual("simple-java", project_state["maven_artifact_id"])
        self.assertEqual("1.0.0", project_state["version"])
        self.assertTrue(project_state["has_junit"])
    
    def test_state_management_workflow(self):
        """Test state management with transactions"""
        state_manager = get_state_manager()
        
        initial_state = {
            "project_path": str(self.temp_dir),
            "java_classes": []
        }
        
        state_manager.set_state("test_project", initial_state)
        
        transaction_id = state_manager.begin_transaction("test_project")
        self.assertIsNotNone(transaction_id)
        
        modified_state = {
            "project_path": str(self.temp_dir),
            "java_classes": [{"name": "TestClass"}]
        }
        state_manager.set_state("test_project", modified_state)
        
        state_manager.commit_transaction(transaction_id)
        
        final_state = state_manager.get_state("test_project")
        self.assertEqual(1, len(final_state["java_classes"]))
    
    def test_access_control_workflow(self):
        """Test access control and auditing"""
        access_manager = get_access_control_manager()
        access_manager.set_project_root(str(self.temp_dir))
        
        access_manager.add_restricted_path(str(self.temp_dir / "restricted"))
        
        restricted_dir = self.temp_dir / "restricted"
        restricted_dir.mkdir()
        
        access_entry = access_manager.check_permission(
            str(restricted_dir),
            "WRITE"
        )
        
        self.assertFalse(access_entry.allowed)
        self.assertIn("restricted", access_entry.reason.lower())
        
        audit_log = access_manager.get_audit_log()
        self.assertGreater(len(audit_log), 0)
    
    def test_security_validation_workflow(self):
        """Test security validation workflow"""
        malicious_inputs = [
            "../../../etc/passwd",
            "file.jsp<script>alert('xss')</script>",
            "SELECT * FROM users WHERE 1=1; DROP TABLE users;--",
            "AKIAIOSFODNN7EXAMPLE",
            "sk-1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        ]
        
        for input_str in malicious_inputs:
            secrets = check_for_secrets(input_str)
            self.assertGreater(len(secrets), 0, 
                            f"Should detect malicious content in: {input_str}")
    
    def test_validation_workflow(self):
        """Test input validation workflow"""
        invalid_class_names = ["123Class", "My-Class", "class", "User@Name"]
        valid_class_names = ["UserService", "ValidClassName", "MyClass123"]
        
        for name in invalid_class_names:
            with self.assertRaises(ValidationError):
                validate_class_name(name)
        
        for name in valid_class_names:
            try:
                validate_class_name(name)
            except ValidationError:
                self.fail(f"Valid class name {name} failed validation")
    
    def test_git_integration_workflow(self):
        """Test Git integration workflow"""
        git_dir = self.temp_dir / ".git"
        git_dir.mkdir()
        
        is_repo = git_is_repository(str(self.temp_dir))
        self.assertTrue(is_repo)
        
        status = git_status(str(self.temp_dir))
        self.assertIsNotNone(status)
    
    async def test_concurrent_operations_workflow(self):
        """Test concurrent operations on same project"""
        java_file1 = self.java_dir / "User1.java"
        java_file2 = self.java_dir / "User2.java"
        
        java_file1.write_text("package com.example; public class User1 {}", encoding="utf-8")
        java_file2.write_text("package com.example; public class User2 {}", encoding="utf-8")
        
        async def analyze_file(file_path):
            return create_java_class_state(str(file_path))
        
        tasks = [
            analyze_file(java_file1),
            analyze_file(java_file2)
        ]
        
        results = await asyncio.gather(*tasks)
        
        self.assertEqual(2, len(results))
        self.assertEqual("User1", results[0]["name"])
        self.assertEqual("User2", results[1]["name"])
    
    def test_error_scenarios_workflow(self):
        """Test error handling in various scenarios"""
        test_file = self.java_dir / "NonExistent.java"
        
        try:
            create_java_class_state(str(test_file))
        except Exception as e:
            self.assertIsNotNone(str(e))
        
        non_existent_dir = self.temp_dir / "nonexistent"
        try:
            validate_project_directory(str(non_existent_dir))
        except (ValidationError, FileNotFoundError):
            pass
        else:
            self.fail("Should raise exception for non-existent directory")


class TestRealJavaProjects(unittest.TestCase):
    """Integration tests with real Java project scenarios"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_spring_boot_project_structure(self):
        """Test analysis of a Spring Boot project structure"""
        sample_project = SAMPLES_DIR / "springboot-sample"
        self.assertTrue(sample_project.exists())
        
        project_state = create_project_state(str(sample_project))
        self.assertIsNotNone(project_state)
        self.assertTrue(project_state["has_spring"])
        self.assertEqual("com.example", project_state["maven_group_id"])
        self.assertEqual("springboot-sample", project_state["maven_artifact_id"])
    
    def test_multi_module_maven_project(self):
        """Test analysis of a multi-module Maven project"""
        sample_project = SAMPLES_DIR / "multi-module"
        self.assertTrue(sample_project.exists())
        
        java_files = find_java_files(str(sample_project))
        self.assertGreater(len(java_files), 0, "Should find Java files in multi-module project")
        
        project_state = create_project_state(str(sample_project))
        self.assertIsNotNone(project_state)
        self.assertEqual("com.example", project_state["maven_group_id"])
        self.assertEqual("multi-module", project_state["maven_artifact_id"])
    
    def test_project_with_tests(self):
        """Test analysis of a project with test files using junit5-sample"""
        sample_project = SAMPLES_DIR / "junit5-sample"
        self.assertTrue(sample_project.exists())
        
        project_state = create_project_state(str(sample_project))
        self.assertIsNotNone(project_state)
        self.assertTrue(project_state["has_junit"], "Should detect JUnit in sample project")
        
        java_files = find_java_files(str(sample_project))
        test_files = [f for f in java_files if "test" in f.lower()]
        self.assertGreater(len(test_files), 0, "Should find test files")


if __name__ == "__main__":
    unittest.main()
