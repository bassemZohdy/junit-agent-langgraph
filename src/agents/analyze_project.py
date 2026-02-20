import os
from typing import Optional, Dict, List
from ..tools.java_tools import find_java_files, read_file
from ..utils.java_parser import extract_imports, extract_dependencies, parse_java_file
from .base import BaseAgent


class AnalyzeProjectAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__(llm)

    async def process(self, state: dict) -> dict:
        project_path = state.get("project_path", "")
        
        java_files = find_java_files(project_path)
        
        java_classes = []
        dependency_graph = {}
        
        for java_file in java_files:
            class_info = await self._analyze_java_file(java_file, project_path, dependency_graph)
            if class_info:
                java_classes.append(class_info)
        
        return {
            "java_classes": java_classes,
            "dependency_graph": dependency_graph,
            "last_action": "analyzed_project"
        }

    async def _analyze_java_file(self, file_path: str, project_path: str, dependency_graph: dict) -> Optional[dict]:
        try:
            content = read_file(file_path)
            if not content:
                return None
            
            tree = parse_java_file(content)
            
            classes = []
            for path, node in tree:
                if isinstance(node, javalang.tree.ClassDeclaration):
                    class_name = node.name
                    full_class_name = self._get_full_class_name(file_path, project_path, class_name)
                    
                    imports = extract_imports(tree)
                    deps = extract_dependencies(tree, imports)
                    
                    class_info = {
                        "name": class_name,
                        "full_name": full_class_name,
                        "file_path": file_path,
                        "content": content,
                        "status": "analyzed",
                        "errors": [],
                        "methods": [],
                        "fields": [],
                        "dependencies": deps
                    }
                    
                    for method in node.methods:
                        class_info["methods"].append({
                            "name": method.name,
                            "return_type": str(method.return_type) if method.return_type else "void",
                            "parameters": [p.name for p in method.parameters],
                            "modifiers": method.modifiers
                        })
                    
                    for field in node.fields:
                        for declarator in field.declarators:
                            class_info["fields"].append({
                                "name": declarator.name,
                                "type": str(field.type) if field.type else "Object",
                                "modifiers": field.modifiers
                            })
                    
                    classes.append(class_info)
                    dependency_graph[full_class_name] = deps
            
            return classes[0] if classes else None
        except Exception as e:
            return {
                "name": os.path.basename(file_path).replace(".java", ""),
                "file_path": file_path,
                "content": None,
                "status": "error",
                "errors": [str(e)],
                "methods": [],
                "fields": [],
                "dependencies": []
            }

    def _get_full_class_name(self, file_path: str, project_path: str, class_name: str) -> str:
        relative_path = os.path.relpath(file_path, project_path)
        package_path = os.path.dirname(relative_path).replace(os.sep, ".")
        return f"{package_path}.{class_name}" if package_path else class_name
