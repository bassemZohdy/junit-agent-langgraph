import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils.state_manager import StateManager, reset_state_manager
from src.states.project import ProjectState

class TestStateManager(unittest.TestCase):
    """Unit tests for state_manager.py"""
    
    def setUp(self):
        self.manager = StateManager()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        reset_state_manager()
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_get_state_empty(self):
        state = self.manager.get_state()
        self.assertIsNone(state)
    
    def _create_valid_project_state(self) -> ProjectState:
        """Helper method to create a valid ProjectState for testing."""
        return {
            "messages": [],
            "project_path": str(self.temp_dir),
            "project_name": "test_project",
            "packaging_type": "jar",
            "version": "1.0.0",
            "description": "Test project",
            "java_classes": [
                {
                    "name": "TestClass",
                    "file_path": str(self.temp_dir / "TestClass.java"),
                    "package": "com.example",
                    "content": "public class TestClass {}",
                    "type": "class",
                    "modifiers": ["public"],
                    "extends": None,
                    "implements": [],
                    "annotations": [],
                    "fields": [],
                    "methods": [],
                    "imports": [],
                    "inner_classes": [],
                    "status": "analyzed",
                    "errors": [],
                    "line_number": 1
                }
            ],
            "test_classes": [],
            "current_class": None,
            "maven_group_id": "com.example",
            "maven_artifact_id": "test-project",
            "dependencies": [],
            "test_dependencies": [],
            "transitive_dependencies": [],
            "dependency_graph": {},
            "plugins": [],
            "build_status": {
                "last_build_time": None,
                "build_status": "not_built",
                "build_duration": None,
                "goals": [],
                "output_directory": str(self.temp_dir / "target"),
                "test_results": {},
                "compilation_errors": []
            },
            "last_action": "",
            "summary_report": None,
            "source_directory": str(self.temp_dir / "src" / "main" / "java"),
            "test_directory": str(self.temp_dir / "src" / "test" / "java"),
            "output_directory": str(self.temp_dir / "target"),
            "has_spring": False,
            "has_junit": False,
            "has_mockito": False,
            "retry_count": 0,
            "max_retries": 3,
            "test_results": {},
            "all_tests_passed": False
        }
    
    def test_set_state_success(self):
        test_state = self._create_valid_project_state()
        
        self.manager.set_state(test_state)
        result = self.manager.get_state()
        
        self.assertEqual("test_project", result["project_name"])
    
    def test_set_state_invalid_state(self):
        with self.assertRaises(Exception):
            self.manager.set_state({})  # Missing required fields
    
    def test_begin_transaction(self):
        transaction = self.manager.begin_transaction("test_operation")
        
        self.assertIsNotNone(transaction)
        self.assertEqual("test_operation", transaction.operation)
        self.assertFalse(transaction.success)
        self.assertIsNone(transaction.after_snapshot)
    
    def test_commit_transaction(self):
        # First set some state
        test_state = self._create_valid_project_state()
        self.manager.set_state(test_state)
        
        transaction = self.manager.begin_transaction("test_commit")
        initial_count = len(self.manager._snapshots)
        
        self.manager.commit_transaction(transaction)
        
        self.assertTrue(transaction.success)
        self.assertIsNotNone(transaction.after_snapshot)
        self.assertEqual(len(self.manager._snapshots), initial_count + 1)
    
    def test_rollback_transaction(self):
        test_state = self._create_valid_project_state()
        self.manager.set_state(test_state)
        
        transaction = self.manager.begin_transaction("test_rollback")
        state_before = self.manager.get_state()
        
        modified_state = self._create_valid_project_state()
        modified_state["project_name"] = "modified_project"
        
        self.manager.set_state(modified_state)
        
        self.manager.rollback_transaction(transaction, "Test rollback")
        
        state_after = self.manager.get_state()
        self.assertEqual(state_before["project_name"], state_after["project_name"])
    
    def test_execute_with_rollback_success(self):
        test_state = self._create_valid_project_state()
        self.manager.set_state(test_state)
        
        def test_operation():
            state = self.manager.get_state()
            state["project_name"] = "modified_project"
            self.manager.set_state(state)
            return state
        
        result = self.manager.execute_with_rollback("test_operation", test_operation)
        
        self.assertEqual("modified_project", result["project_name"])
    
    def test_execute_with_rollback_failure(self):
        def failing_operation():
            raise ValueError("Test failure")
        
        with self.assertRaises(ValueError):
            self.manager.execute_with_rollback("test_failure", failing_operation)
    
    def test_verify_state_consistency_valid(self):
        test_state = self._create_valid_project_state()
        
        # Create test file to make it valid
        test_file = self.temp_dir / "TestClass.java"
        test_file.write_text("public class TestClass {}")
        
        # Update class file path to exist
        test_state["java_classes"][0]["file_path"] = str(test_file)
        test_state["java_classes"][0]["last_modified"] = test_file.stat().st_mtime
        
        self.manager.set_state(test_state)
        
        result = self.manager.verify_state_consistency()
        
        self.assertTrue(result["consistent"])
        self.assertEqual([], result["issues"])
        self.assertEqual([], result["warnings"])
    
    def test_verify_state_consistency_invalid(self):
        invalid_state = self._create_valid_project_state()
        invalid_state["project_path"] = str(Path("nonexistent/path"))
        
        self.manager.set_state(invalid_state)
        result = self.manager.verify_state_consistency()
        
        self.assertFalse(result["consistent"])
        self.assertIn("nonexistent", result["issues"][0])
    
    def test_invalidate_class_state(self):
        test_state = self._create_valid_project_state()
        self.manager.set_state(test_state)
        
        self.manager.invalidate_class_state("TestClass")
        
        state = self.manager.get_state()
        
        self.assertEqual("stale", state["java_classes"][0]["status"])
    
    def test_clear_state(self):
        test_state = self._create_valid_project_state()
        self.manager.set_state(test_state)
        
        self.manager.clear_state()
        
        result = self.manager.get_state()
        self.assertIsNone(result)
    
    def test_get_snapshot(self):
        test_state = self._create_valid_project_state()
        self.manager.set_state(test_state)
        
        snapshot = self.manager.get_snapshot()
        
        self.assertIsNotNone(snapshot)
        self.assertIsNotNone(snapshot.timestamp)
        self.assertIsNotNone(snapshot.checksum)
        self.assertIsNotNone(snapshot.operation)
    
    def test_get_transaction_history(self):
        # Set initial state
        test_state = self._create_valid_project_state()
        self.manager.set_state(test_state)
        
        # Create and commit transactions
        transaction1 = self.manager.begin_transaction("test1")
        self.manager.commit_transaction(transaction1)
        
        transaction2 = self.manager.begin_transaction("test2")
        self.manager.commit_transaction(transaction2)
        
        history = self.manager.get_transaction_history()
        
        self.assertEqual(2, len(history))
    
    def test_get_transaction_history_limit(self):
        # Set initial state
        test_state = self._create_valid_project_state()
        self.manager.set_state(test_state)
        
        # Create and commit multiple transactions
        for i in range(5):
            transaction = self.manager.begin_transaction(f"test{i}")
            self.manager.commit_transaction(transaction)
        
        history = self.manager.get_transaction_history(limit=3)
        
        self.assertEqual(3, len(history))


if __name__ == '__main__':
    unittest.main()
