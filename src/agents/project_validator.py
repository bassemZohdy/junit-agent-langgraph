from typing import Dict, List
from langchain_core.messages import HumanMessage, SystemMessage
from .base import BaseAgent
from ..tools.async_maven_tools import maven_test_async, maven_build_async


class ProjectValidatorAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm, name="ProjectValidatorAgent")

    async def process(self, state: dict) -> dict:
        await self.log("Starting project validation")
        
        test_classes = state.get("test_classes", [])
        java_classes = state.get("java_classes", [])
        test_results = state.get("test_results", {})
        
        validation_results = await self._perform_validation(state)
        
        summary_report = await self._generate_summary_report(
            java_classes,
            test_classes,
            test_results,
            validation_results
        )
        
        return {
            "build_status": validation_results.get("overall_status", "unknown"),
            "summary_report": summary_report,
            "last_action": "project_validated",
            "validation_results": validation_results
        }

    async def _perform_validation(self, state: dict) -> Dict:
        project_path = state.get("project_path", "")
        
        validation_results = {
            "build_status": "unknown",
            "test_status": "unknown",
            "coverage": 0,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": [],
            "warnings": []
        }
        
        try:
            build_result = await maven_build_async(project_path)
            
            if build_result.get("success", False):
                validation_results["build_status"] = "success"
            else:
                validation_results["build_status"] = "failed"
                validation_results["errors"].append("Build failed")
        except Exception as e:
            validation_results["build_status"] = "error"
            validation_results["errors"].append(f"Build error: {str(e)}")
        
        try:
            test_result = await maven_test_async(project_path)
            
            output = test_result.get("stdout", "") + test_result.get("stderr", "")
            
            if "BUILD SUCCESS" in output:
                validation_results["test_status"] = "success"
            elif "BUILD FAILURE" in output:
                validation_results["test_status"] = "failed"
            
            validation_results.update(self._extract_test_metrics(output))
        except Exception as e:
            validation_results["test_status"] = "error"
            validation_results["errors"].append(f"Test execution error: {str(e)}")
        
        test_results = state.get("test_results", {})
        validation_results["failed_tests"] = len([
            r for r in test_results.values() if not r.get("success", False)
        ])
        validation_results["passed_tests"] = len([
            r for r in test_results.values() if r.get("success", False)
        ])
        
        if validation_results["failed_tests"] == 0 and validation_results["test_status"] == "success":
            validation_results["overall_status"] = "success"
        elif validation_results["failed_tests"] > 0:
            validation_results["overall_status"] = "partial"
        else:
            validation_results["overall_status"] = "failed"
        
        return validation_results

    def _extract_test_metrics(self, output: str) -> Dict:
        import re
        
        metrics = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
            "errors": 0,
            "failures": 0
        }
        
        test_pattern = r'Tests run:\s*(\d+),\s*Failures:\s*(\d+),\s*Errors:\s*(\d+),\s*Skipped:\s*(\d+)'
        match = re.search(test_pattern, output)
        
        if match:
            metrics["total_tests"] = int(match.group(1))
            metrics["failures"] = int(match.group(2))
            metrics["errors"] = int(match.group(3))
            metrics["skipped_tests"] = int(match.group(4))
            metrics["failed_tests"] = metrics["failures"] + metrics["errors"]
            metrics["passed_tests"] = metrics["total_tests"] - metrics["failed_tests"] - metrics["skipped_tests"]
        
        return metrics

    async def _generate_summary_report(self, java_classes: List[Dict], test_classes: List[Dict], test_results: Dict, validation_results: Dict) -> str:
        report_parts = [
            "# Project Validation Report\n",
            "## Overview\n",
            f"- Total Java Classes: {len(java_classes)}\n",
            f"- Test Classes Generated: {len(test_classes)}\n",
            f"- Overall Status: {validation_results.get('overall_status', 'unknown').upper()}\n",
            "\n## Build Status\n",
            f"- Status: {validation_results.get('build_status', 'unknown').upper()}\n",
            "\n## Test Results\n",
            f"- Test Status: {validation_results.get('test_status', 'unknown').upper()}\n",
            f"- Total Tests: {validation_results.get('total_tests', 0)}\n",
            f"- Passed: {validation_results.get('passed_tests', 0)}\n",
            f"- Failed: {validation_results.get('failed_tests', 0)}\n",
            f"- Errors: {validation_results.get('errors', 0)}\n",
        ]
        
        if validation_results.get("errors"):
            report_parts.append("\n## Errors\n")
            for error in validation_results["errors"]:
                report_parts.append(f"- {error}\n")
        
        if validation_results.get("warnings"):
            report_parts.append("\n## Warnings\n")
            for warning in validation_results["warnings"]:
                report_parts.append(f"- {warning}\n")
        
        report_parts.append("\n## Test Classes\n")
        for test_class in test_classes:
            test_name = test_class.get("name", "Unknown")
            status = test_class.get("status", "unknown")
            report_parts.append(f"- {test_name}: {status}\n")
        
        report_parts.append("\n## Validation Summary\n")
        
        if validation_results.get("overall_status") == "success":
            report_parts.append("✓ All tests passed successfully. Project is ready for deployment.\n")
        elif validation_results.get("overall_status") == "partial":
            report_parts.append("⚠ Some tests failed. Review the errors above and fix the issues.\n")
        else:
            report_parts.append("✗ Validation failed. Critical issues need to be resolved.\n")
        
        return "".join(report_parts)
