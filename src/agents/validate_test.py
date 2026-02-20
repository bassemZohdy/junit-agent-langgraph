import os
import re
from typing import Dict, List
from .base import BaseAgent
from ..tools.file_tools import write_file
from ..tools.async_maven_tools import maven_build_async, maven_test_async


class ValidateTestAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__(llm, name="ValidateTestAgent")

    async def process(self, state: dict) -> dict:
        test_classes = state.get("test_classes", [])
        project_path = state.get("project_path", "")
        
        if not test_classes:
            return {"last_action": "validate_test_skipped", "error": "No tests to validate"}
        
        latest_test = test_classes[-1]
        
        await self.log(f"Validating test class: {latest_test['name']}")
        
        validation_result = await self._validate_test(latest_test, project_path)
        
        updated_test_classes = test_classes.copy()
        updated_test_classes[-1]["status"] = validation_result["status"]
        updated_test_classes[-1]["errors"] = validation_result["errors"]
        
        test_results = state.get("test_results", {})
        test_results[latest_test["name"]] = validation_result
        
        return {
            "test_classes": updated_test_classes,
            "test_results": test_results,
            "last_action": "test_validated"
        }

    async def _validate_test(self, test_class: dict, project_path: str) -> Dict:
        test_content = test_class.get("content", "")
        test_name = test_class.get("name", "")
        
        if not test_content:
            return {
                "status": "error",
                "errors": ["Test content is empty"],
                "success": False
            }
        
        test_file_path = test_class.get("file_path", "")
        if not test_file_path:
            return {
                "status": "error",
                "errors": ["Test file path not provided"],
                "success": False
            }
        
        write_result = await self._write_test_file(test_file_path, test_content)
        if not write_result["success"]:
            return write_result
        
        compile_result = await self._compile_project(project_path)
        if not compile_result["success"]:
            return {
                "status": "compilation_failed",
                "errors": compile_result["errors"],
                "success": False
            }
        
        test_result = await self._run_tests(project_path, test_name)
        
        return {
            "status": "passed" if test_result["success"] else "failed",
            "errors": test_result["errors"],
            "success": test_result["success"],
            "output": test_result.get("output", ""),
            "stack_traces": test_result.get("stack_traces", [])
        }

    async def _write_test_file(self, file_path: str, content: str) -> Dict:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            write_file(file_path, content)
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Failed to write test file: {str(e)}"]
            }

    async def _compile_project(self, project_path: str) -> Dict:
        try:
            result = await maven_build_async(project_path)
            
            if not result.get("success", False):
                errors = self._extract_errors(result.get("stderr", "") + result.get("stdout", ""))
                return {
                    "success": False,
                    "errors": errors
                }
            
            return {"success": True}
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Compilation failed: {str(e)}"]
            }

    async def _run_tests(self, project_path: str, test_name: str) -> Dict:
        try:
            result = await maven_test_async(project_path)
            
            if not result.get("success", False):
                output = result.get("stderr", "") + result.get("stdout", "")
                errors = self._extract_errors(output)
                stack_traces = self._extract_stack_traces(output)
                
                return {
                    "success": False,
                    "errors": errors,
                    "stack_traces": stack_traces,
                    "output": output
                }
            
            output = result.get("stdout", "")
            
            if "BUILD SUCCESS" in output and "Tests run:" in output:
                return {
                    "success": True,
                    "errors": [],
                    "stack_traces": [],
                    "output": output
                }
            
            return {
                "success": False,
                "errors": ["Tests did not pass"],
                "stack_traces": [],
                "output": output
            }
        except Exception as e:
            return {
                "success": False,
                "errors": [f"Test execution failed: {str(e)}"],
                "stack_traces": []
            }

    def _extract_errors(self, output: str) -> List[str]:
        errors = []
        
        error_patterns = [
            r'ERROR:?\s*(.+)',
            r'error:\s*(.+)',
            r'FAILURE:\s*(.+)',
            r'Failed:\s*(.+)',
            r'Caused by:\s*(.+)',
            r'Exception:\s*(.+)'
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, output)
            errors.extend(matches)
        
        if not errors:
            lines = output.split("\n")
            for i, line in enumerate(lines):
                if any(keyword in line for keyword in ["ERROR", "FAILURE", "Exception", "Failed"]):
                    if line.strip():
                        errors.append(line.strip())
        
        return list(set(errors))

    def _extract_stack_traces(self, output: str) -> List[str]:
        stack_traces = []
        
        lines = output.split("\n")
        current_trace = []
        in_trace = False
        
        for line in lines:
            if line.strip().startswith("at "):
                in_trace = True
                current_trace.append(line.strip())
            elif in_trace:
                if line.strip() and not line.strip().startswith("at ") and not line.strip().startswith("Caused by:"):
                    if current_trace:
                        stack_traces.append("\n".join(current_trace))
                        current_trace = []
                    in_trace = False
                elif line.strip().startswith("Caused by:"):
                    current_trace.append(line.strip())
        
        if current_trace:
            stack_traces.append("\n".join(current_trace))
        
        return stack_traces
