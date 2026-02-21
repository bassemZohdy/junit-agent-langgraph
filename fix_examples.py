# Example fixes for the failing tests:

# 1. Fix for test_set_state_success and test_set_state_invalid_state:
def test_set_state_success(self):
    # Create a proper ProjectState object instead of a simple dict
    test_state = {
        "messages": [],
        "project_path": str(self.temp_dir),
        "project_name": "test_project",
        "packaging_type": "jar",
        "version": "1.0.0",
        "description": "Test project",
        "java_classes": [],
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
    
    self.manager.set_state(test_state)
    result = self.manager.get_state()
    
    self.assertEqual("test_project", result["project_name"])

# 2. Fix for test_commit_transaction:
def test_commit_transaction(self):
    # First set some state (required for snapshots)
    test_state = self._create_valid_project_state()
    self.manager.set_state(test_state)
    
    # Create and commit a transaction properly
    transaction = self.manager.begin_transaction("test_commit")
    initial_count = len(self.manager._snapshots)
    
    self.manager.commit_transaction(transaction)
    
    self.assertTrue(transaction.success)
    self.assertIsNotNone(transaction.after_snapshot)
    self.assertEqual(len(self.manager._snapshots), initial_count + 1)

# 3. Fix for test_rollback_transaction:
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

# 4. Fix for test_execute_with_rollback_success:
def test_execute_with_rollback_success(self):
    test_state = self._create_valid_project_state()
    self.manager.set_state(test_state)
    
    def test_operation():
        # Get current state, modify it, and set it back
        state = self.manager.get_state()
        state["project_name"] = "modified_project"
        self.manager.set_state(state)
        return state  # Return the modified state
    
    result = self.manager.execute_with_rollback("test_operation", test_operation)
    
    self.assertEqual("modified_project", result["project_name"])

# 5. Fix for test_verify_state_consistency_valid:
def test_verify_state_consistency_valid(self):
    test_state = self._create_valid_project_state()
    
    # Create test file to make it valid
    test_file = self.temp_dir / "TestClass.java"
    test_file.write_text("public class TestClass {}")
    
    # Update class file path to exist and add last_modified
    test_state["java_classes"][0]["file_path"] = str(test_file)
    test_state["java_classes"][0]["last_modified"] = test_file.stat().st_mtime
    
    self.manager.set_state(test_state)
    
    result = self.manager.verify_state_consistency()
    
    self.assertTrue(result["consistent"])
    self.assertEqual([], result["issues"])
    self.assertEqual([], result["warnings"])
