import javalang
from pathlib import Path
from typing import List, Optional, Dict
from langchain_core.tools import tool
from ..exceptions.handler import FileOperationError, ValidationError, create_error_response
from ..utils.validation import validate_directory_exists, validate_not_empty


@tool
def search_in_files(project_path: str, search_term: str, file_pattern: str = "*.java") -> str:
    """Search for text across all Java files in project."""
    try:
        validate_directory_exists(project_path)
        validate_not_empty(search_term, "search_term")
        
        project_dir = Path(project_path)
        results = []
        
        for java_file in project_dir.rglob(file_pattern):
            try:
                content = java_file.read_text(encoding="utf-8")
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    if search_term.lower() in line.lower():
                        relative_path = str(java_file.relative_to(project_dir))
                        results.append(f"{relative_path}:{line_num}: {line.strip()[:100]}")
            except Exception:
                continue
        
        if not results:
            return f"No matches found for '{search_term}'"
        
        return f"Found {len(results)} matches for '{search_term}':\n\n" + "\n".join(results[:50])
    except Exception as e:
        response = create_error_response(e)
        return f"Error searching files: {response['errors'][0]}"


@tool
def replace_in_files(project_path: str, search_term: str, replacement: str, file_pattern: str = "*.java") -> str:
    """Replace text across all Java files in project."""
    try:
        validate_directory_exists(project_path)
        validate_not_empty(search_term, "search_term")
        validate_not_empty(replacement, "replacement")
        
        project_dir = Path(project_path)
        modified_files = []
        
        for java_file in project_dir.rglob(file_pattern):
            try:
                content = java_file.read_text(encoding="utf-8")
                
                if search_term in content:
                    new_content = content.replace(search_term, replacement)
                    java_file.write_text(new_content, encoding="utf-8")
                    relative_path = str(java_file.relative_to(project_dir))
                    modified_files.append(relative_path)
            except Exception:
                continue
        
        if not modified_files:
            return f"No files contain '{search_term}'"
        
        return f"Replaced '{search_term}' with '{replacement}' in {len(modified_files)} files:\n" + "\n".join(modified_files)
    except Exception as e:
        response = create_error_response(e)
        return f"Error replacing in files: {response['errors'][0]}"


@tool
def bulk_add_import(project_path: str, import_statement: str, file_pattern: str = "*.java") -> str:
    """Add import statement to all Java files in project."""
    try:
        validate_directory_exists(project_path)
        validate_not_empty(import_statement, "import_statement")
        
        project_dir = Path(project_path)
        modified_files = []
        
        for java_file in project_dir.rglob(file_pattern):
            try:
                content = java_file.read_text(encoding="utf-8")
                
                if import_statement not in content:
                    lines = content.split('\n')
                    
                    package_idx = -1
                    for i, line in enumerate(lines):
                        if line.strip().startswith("package "):
                            package_idx = i
                        elif line.strip().startswith("import ") or line.strip().startswith("static import "):
                            if package_idx >= 0:
                                lines.insert(package_idx + 1, import_statement)
                                break
                    
                    new_content = '\n'.join(lines)
                    java_file.write_text(new_content, encoding="utf-8")
                    
                    relative_path = str(java_file.relative_to(project_dir))
                    modified_files.append(relative_path)
            except Exception:
                continue
        
        if not modified_files:
            return "Import statement already exists or no Java files found"
        
        return f"Added import to {len(modified_files)} files:\n" + "\n".join(modified_files)
    except Exception as e:
        response = create_error_response(e)
        return f"Error adding import in files: {response['errors'][0]}"


@tool
def bulk_remove_import(project_path: str, import_statement: str, file_pattern: str = "*.java") -> str:
    """Remove import statement from all Java files in project."""
    try:
        validate_directory_exists(project_path)
        validate_not_empty(import_statement, "import_statement")
        
        project_dir = Path(project_path)
        modified_files = []
        
        for java_file in project_dir.rglob(file_pattern):
            try:
                content = java_file.read_text(encoding="utf-8")
                
                if import_statement in content:
                    new_content = content.replace(import_statement, "")
                    java_file.write_text(new_content, encoding="utf-8")
                    
                    relative_path = str(java_file.relative_to(project_dir))
                    modified_files.append(relative_path)
            except Exception:
                continue
        
        if not modified_files:
            return "Import statement not found in any files"
        
        return f"Removed import from {len(modified_files)} files:\n" + "\n".join(modified_files)
    except Exception as e:
        response = create_error_response(e)
        return f"Error removing import from files: {response['errors'][0]}"


@tool
def count_java_entities(project_path: str) -> str:
    """Count classes, methods, and fields across all Java files."""
    try:
        validate_directory_exists(project_path)
        
        project_dir = Path(project_path)
        total_classes = 0
        total_methods = 0
        total_fields = 0
        total_files = 0
        
        for java_file in project_dir.rglob("*.java"):
            try:
                total_files += 1
                content = java_file.read_text(encoding="utf-8")
                tree = javalang.parse.parse(content)
                
                for path_info, node in tree:
                    if isinstance(node, javalang.tree.ClassDeclaration):
                        total_classes += 1
                        total_fields += len(node.fields) if node.fields else 0
                        total_methods += len(node.methods) if node.methods else 0
            except Exception:
                continue
        
        return f"Project Statistics:\n- Java Files: {total_files}\n- Classes: {total_classes}\n- Total Methods: {total_methods}\n- Total Fields: {total_fields}"
    except Exception as e:
        response = create_error_response(e)
        return f"Error counting entities: {response['errors'][0]}"


@tool
def refactor_multiple_classes(project_path: str, refactoring_type: str) -> str:
    """Apply refactoring to multiple classes at once."""
    try:
        validate_directory_exists(project_path)
        validate_not_empty(refactoring_type, "refactoring_type")
        
        project_dir = Path(project_path)
        results = []
        
        for java_file in project_dir.rglob("*.java"):
            try:
                content = java_file.read_text(encoding="utf-8")
                tree = javalang.parse.parse(content)
                new_content = content
                
                for path_info, node in tree:
                    if isinstance(node, javalang.tree.ClassDeclaration):
                        if refactoring_type == "add_serialVersionUID":
                            if not hasattr(node, 'implements') or 'java.io.Serializable' not in str(new_content):
                                continue
                            
                            if 'serialVersionUID' not in new_content:
                                indent = "    "
                                class_end_idx = new_content.find('}')
                                
                                if class_end_idx > 0:
                                    before = new_content[:class_end_idx]
                                    after = new_content[class_end_idx:]
                                    field = f"{indent}private static final long serialVersionUID = 1L;\n"
                                    new_content = before + field + after
                
                if new_content != content:
                    java_file.write_text(new_content, encoding="utf-8")
                    relative_path = str(java_file.relative_to(project_dir))
                    results.append(relative_path)
            except Exception:
                continue
        
        if not results:
            return "No files were refactored"
        
        return f"Applied '{refactoring_type}' to {len(results)} files:\n" + "\n".join(results)
    except Exception as e:
        response = create_error_response(e)
        return f"Error refactoring classes: {response['errors'][0]}"


@tool
def list_all_classes(project_path: str) -> str:
    """List all classes found in Java files with package info."""
    try:
        validate_directory_exists(project_path)
        
        project_dir = Path(project_path)
        classes_info = []
        
        for java_file in project_dir.rglob("*.java"):
            try:
                content = java_file.read_text(encoding="utf-8")
                tree = javalang.parse.parse(content)
                
                package_name = None
                if tree.package:
                    package_name = tree.package.name
                
                for path_info, node in tree:
                    if isinstance(node, javalang.tree.ClassDeclaration):
                        relative_path = str(java_file.relative_to(project_dir))
                        classes_info.append({
                            'package': package_name,
                            'class': node.name,
                            'file': relative_path
                        })
            except Exception:
                continue
        
        if not classes_info:
            return "No Java classes found"
        
        result = ["Classes found in project:"]
        for info in classes_info:
            pkg = f"Package: {info['package']}" if info['package'] else "Default Package"
            result.append(f"- {pkg}")
            result.append(f"  Class: {info['class']}")
            result.append(f"  File: {info['file']}")
        
        return "\n".join(result)
    except Exception as e:
        response = create_error_response(e)
        return f"Error listing classes: {response['errors'][0]}"


project_operations_tools = [
    search_in_files,
    replace_in_files,
    bulk_add_import,
    bulk_remove_import,
    count_java_entities,
    refactor_multiple_classes,
    list_all_classes
]
