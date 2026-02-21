import os
from typing import Optional, Dict, List
from ..tools.java_tools import list_java_classes, analyze_java_class
from ..utils.java_parser import extract_dependencies
from .base import BaseAgent


class AnalyzeProjectAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__(llm)

    async def process(self, state: dict) -> dict:
        project_path = state.get("project_path", "")

        # Use new unified API: list_java_classes returns List[JavaClassState]
        java_class_states = list_java_classes(project_path)

        java_classes = []
        dependency_graph = {}

        for class_state in java_class_states:
            if class_state.get("status") == "error":
                continue

            full_class_name = self._get_full_class_name(
                class_state.get("file_path", ""),
                project_path,
                class_state.get("name", "")
            )

            # Extract dependencies from the class state
            deps = self._extract_deps_from_class_state(class_state)

            class_info = {
                "name": class_state.get("name", ""),
                "full_name": full_class_name,
                "file_path": class_state.get("file_path", ""),
                "content": class_state.get("content"),
                "status": "analyzed",
                "errors": [],
                "methods": class_state.get("methods", []),
                "fields": class_state.get("fields", []),
                "dependencies": deps
            }

            java_classes.append(class_info)
            dependency_graph[full_class_name] = deps

        return {
            "java_classes": java_classes,
            "dependency_graph": dependency_graph,
            "last_action": "analyzed_project"
        }

    def _extract_deps_from_class_state(self, class_state: dict) -> List[str]:
        """Extract dependencies from a JavaClassState."""
        deps = []

        # Extract from imports
        for imp in class_state.get("imports", []):
            deps.append(imp.get("name", ""))

        # Extract from parent class
        if class_state.get("extends"):
            deps.append(class_state["extends"])

        # Extract from implemented interfaces
        for interface in class_state.get("implements", []):
            deps.append(interface)

        return list(set(deps))  # Remove duplicates

    def _get_full_class_name(self, file_path: str, project_path: str, class_name: str) -> str:
        relative_path = os.path.relpath(file_path, project_path)
        package_path = os.path.dirname(relative_path).replace(os.sep, ".")
        return f"{package_path}.{class_name}" if package_path else class_name
