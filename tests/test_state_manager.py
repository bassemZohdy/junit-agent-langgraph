import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from ..src.utils.state_manager import StateManager, StateSnapshot, StateTransaction, get_state_manager, reset_state_manager
from ..src.states.project import ProjectState


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
    
    def test_set_state_success(self):
        test_state = {
            "project_path": str(self.temp_dir),
            "project_name": "test_project",
            "java_classes": [],
            "test_classes": []
            "dependencies": [],
            "build_status": {}
        }
        
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
        transaction = self.manager.begin_transaction("test_commit")
        initial_count = len(self.manager._snapshots)
        
        self.manager.commit_transaction(transaction)
        
        self.assertTrue(transaction.success)
        self.assertIsNotNone(transaction.after_snapshot)
        self.assertEqual(len(self.manager._snapshots), initial_count + 1)
    
    def test_rollback_transaction(self):
        test_state = {
            "project_path": str(self.temp_dir),
            "project_name": "test_project",
            "java_classes": [{"name": "TestClass"}],
            "test_classes": [],
            "dependencies": [],
            "build_status": {}
        }
        
        self.manager.set_state(test_state)
        transaction = self.manager.begin_transaction("test_rollback")
        
        state_before = self.manager.get_state()
        
        modified_state = test_state.copy()
        modified_state["project_name"] = "modified_project"
        
        self.manager.set_state(modified_state)
        
        self.manager.rollback_transaction(transaction, "Test rollback")
        
        state_after = self.manager.get_state()
        self.assertEqual(state_before["project_name"], state_after["project_name"])
    
    def test_execute_with_rollback_success(self):
        test_state = {
            "project_path": str(self.temp_dir),
            "project_name": "test_project",
            "java_classes": [],
            "test_classes": [],
            "dependencies": [],
            "build_status": {}
        }
        
        def test_operation():
            test_state["project_name"] = "modified_project"
            self.manager.set_state(test_state)
        
        result = self.manager.execute_with_rollback("test_operation", test_operation)
        
        self.assertEqual("modified_project", result["project_name"])
    
    def test_execute_with_rollback_failure(self):
        def failing_operation():
            raise ValueError("Test failure")
        
        with self.assertRaises(ValueError):
            self.manager.execute_with_rollback("test_failure", failing_operation)
    
    def test_verify_state_consistency_valid(self):
        test_state = {
            "project_path": str(self.temp_dir),
            "project_name": "test_project",
            "java_classes": [
                {
                    "name": "TestClass",
                    "file_path": str(self.temp_dir / "TestClass.java"),
                    "package": "com.example",
                    "content": "content",
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
            "dependencies": [],
            "build_status": {}
        }
        
        self.manager.set_state(test_state)
        
        result = self.manager.verify_state_consistency()
        
        self.assertTrue(result["consistent"])
        self.assertEqual([], result["issues"])
        self.assertEqual([], result["warnings"])
    
    def test_verify_state_consistency_invalid(self):
        invalid_state = {
            "project_path": "nonexistent/path",
            "project_name": "invalid",
            "java_classes": [],
            "test_classes": [],
            "dependencies": [],
            "build_status": {}
        }
        
        self.manager.set_state(invalid_state)
        result = self.manager.verify_state_consistency()
        
        self.assertFalse(result["consistent"])
        self.assertIn("nonexistent", result["issues"][0])
    
    def test_invalidate_class_state(self):
        test_state = {
            "project_path": str(self.temp_dir),
            "project_name": "test_project",
            "java_classes": [
                {
                    "name": "TestClass",
                    "file_path": str(self.temp_dir / "TestClass.java"),
                    "package": "com.example",
                    "content": "content",
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
            "dependencies": [],
            "build_status": {}
        }
        
        self.manager.set_state(test_state)
        self.manager.invalidate_class_state("TestClass")
        
        state = self.manager.get_state()
        
        self.assertEqual("stale", state["java_classes"][0]["status"])
    
    def test_clear_state(self):
        test_state = {
            "project_path": str(self.temp_dir),
            "project_name": "test_project",
            "java_classes": [],
            "test_classes": [],
            "dependencies": [],
            "build_status": {}
        }
        
        self.manager.set_state(test_state)
        
        self.manager.clear_state()
        
        result = self.manager.get_state()
        self.assertIsNone(result)
    
    def test_get_snapshot(self):
        test_state = {
            "project_path": str(self.temp_dir),
            "project_name": "test_project",
            "java_classes": [],
            "test_classes": [],
            "dependencies": [],
            "build_status": {}
        }
        
        self.manager.set_state(test_state)
        
        snapshot = self.manager.get_snapshot()
        
        self.assertIsNotNone(snapshot)
        self.assertIsNotNone(snapshot.timestamp)
        self.assertIsNotNone(snapshot.checksum)
        self.assertIsNotNone(snapshot.operation)
    
    def test_get_transaction_history(self):
        transaction1 = self.manager.begin_transaction("test1")
        self.manager.commit_transaction(transaction1)
        
        transaction2 = self.manager.begin_transaction("test2")
        self.manager.commit_transaction(transaction2)
        
        history = self.manager.get_transaction_history()
        
        self.assertEqual(2, len(history))
    
    def test_get_transaction_history_limit(self):
        for i in range(5):
            self.manager.begin_transaction(f"test{i}")
            self.manager.commit_transaction(f"test{i}")
        
        history = self.manager.get_transaction_history(limit=3)
        
        self.assertEqual(3, len(history))


if __name__ == '__main__':
    unittest.main()
