from typing import Optional, Dict, List
from ..tools.java_tools import read_file
from ..utils.java_parser import extract_imports, extract_dependencies, parse_java_file
from .base import BaseAgent


class ClassAnalysisAgent(BaseAgent):
    def __init__(self, llm=None):
        super().__init__(llm)

    async def process(self, state: dict) -> dict:
        current_class = state.get("current_class")
        
        if not current_class:
            return {"last_action": "class_analysis_skipped"}
        
        file_path = current_class.get("file_path", "")
        
        if not file_path:
            return {"last_action": "class_analysis_failed", "error": "No file path provided"}
        
        metadata = await self._extract_class_metadata(file_path)
        
        return {
            "current_class": {
                **current_class,
                **metadata
            },
            "last_action": "class_analyzed"
        }

    async def _extract_class_metadata(self, file_path: str) -> dict:
        try:
            import javalang
            content = read_file(file_path)
            if not content:
                return {
                    "status": "error",
                    "errors": ["Could not read file"],
                    "methods": [],
                    "fields": [],
                    "dependencies": []
                }
            
            tree = parse_java_file(content)
            
            metadata = {
                "status": "analyzed",
                "errors": [],
                "methods": [],
                "fields": [],
                "dependencies": []
            }
            
            for path, node in tree:
                if isinstance(node, javalang.tree.ClassDeclaration):
                    for method in node.methods:
                        method_info = {
                            "name": method.name,
                            "return_type": str(method.return_type) if method.return_type else "void",
                            "parameters": [
                                {
                                    "name": p.name,
                                    "type": str(p.type)
                                }
                                for p in method.parameters
                            ],
                            "modifiers": method.modifiers,
                            "annotations": [a.name for a in method.annotations] if method.annotations else [],
                            "is_public": "public" in method.modifiers,
                            "is_static": "static" in method.modifiers,
                            "is_final": "final" in method.modifiers
                        }
                        metadata["methods"].append(method_info)
                    
                    for field in node.fields:
                        for declarator in field.declarators:
                            field_info = {
                                "name": declarator.name,
                                "type": str(field.type) if field.type else "Object",
                                "modifiers": field.modifiers,
                                "annotations": [a.name for a in field.annotations] if field.annotations else [],
                                "is_public": "public" in field.modifiers,
                                "is_static": "static" in field.modifiers,
                                "is_final": "final" in field.modifiers
                            }
                            metadata["fields"].append(field_info)
            
            imports = extract_imports(tree)
            metadata["dependencies"] = extract_dependencies(tree, imports)
            
            return metadata
        except Exception as e:
            return {
                "status": "error",
                "errors": [str(e)],
                "methods": [],
                "fields": [],
                "dependencies": []
            }
