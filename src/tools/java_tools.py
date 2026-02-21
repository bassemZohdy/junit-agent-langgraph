import javalang
from pathlib import Path
from typing import Optional, Union
from langchain_core.tools import tool
from ..exceptions.handler import ParsingError, create_error_response
from ..utils.validation import (
    validate_directory_exists,
    validate_file_exists,
    validate_java_file,
    validate_not_empty,
    validate_class_name,
    validate_method_name,
    validate_field_name,
    validate_annotation_name,
    validate_import_statement,
    validate_modifier
)
from ..states.project import (
    JavaClassState,
    MethodState,
    FieldState,
    ImportState,
    AnnotationState
)


def _parse_java_file(file_path: str) -> Optional[javalang.tree.CompilationUnit]:
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        content = path.read_text(encoding="utf-8")
        return javalang.parse.parse(content)
    except Exception:
        return None


def _extract_class_name(file_path: str, tree: javalang.tree.CompilationUnit) -> Optional[str]:
    """Extract the first class/interface/enum name from tree."""
    for path, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            return node.name
        if isinstance(node, javalang.tree.InterfaceDeclaration):
            return node.name
        if isinstance(node, javalang.tree.EnumDeclaration):
            return node.name
    return None


def _extract_fields_from_node(node: javalang.tree.ClassDeclaration) -> list[FieldState]:
    """Extract field information from a class node."""
    fields: list[FieldState] = []
    for field in node.fields:
        field_modifiers = [m for m in field.modifiers]
        is_static = "static" in field_modifiers
        is_final = "final" in field_modifiers
        field_annotations = []

        if field.annotations:
            for ann in field.annotations:
                ann_name = ann.name if hasattr(ann, "name") else str(ann)
                ann_elements = {}
                if hasattr(ann, "element"):
                    ann_elements[ann.element.name] = str(ann.element)

                field_annotations.append({
                    "name": ann_name,
                    "elements": ann_elements,
                    "target": None,
                    "line_number": None
                })

        for decl in field.declarators:
            field_type = str(field.type) if field.type else "Object"
            fields.append({
                "name": decl.name,
                "type": field_type,
                "modifiers": field_modifiers,
                "is_static": is_static,
                "is_final": is_final,
                "default_value": None,
                "annotations": field_annotations,
                "line_number": None
            })
    return fields


def _extract_methods_from_node(node: javalang.tree.ClassDeclaration) -> list[MethodState]:
    """Extract method information from a class node."""
    methods: list[MethodState] = []
    for method in node.methods:
        method_modifiers = [m for m in method.modifiers]
        is_abstract = "abstract" in method_modifiers
        method_annotations = []
        throws = []

        if method.throws:
            for throw_clause in method.throws:
                throws.append(throw_clause.name if hasattr(throw_clause, "name") else str(throw_clause))

        method_annotations.extend([
            {
                "name": ann.name if hasattr(ann, "name") else str(ann),
                "elements": {},
                "target": None,
                "line_number": None
            }
            for ann in method.annotations
        ])

        parameters = []
        for param in method.parameters:
            param_type = str(param.type) if param.type else "Object"
            parameters.append({
                "name": param.name,
                "type": param_type,
                "position": "method parameter"
            })

        methods.append({
            "name": method.name,
            "return_type": str(method.return_type) if method.return_type else "void",
            "parameters": parameters,
            "modifiers": method_modifiers,
            "annotations": method_annotations,
            "throws": throws,
            "body": None,
            "is_abstract": is_abstract,
            "line_number": None
        })
    return methods


def _extract_class_details_from_tree(source_file: str, tree: javalang.tree.CompilationUnit) -> list[JavaClassState]:
    """
    Extract all class details from an AST tree into structured JavaClassState objects.

    This is the unified, centralized function for extracting Java class information.
    All class extraction logic goes through here to maintain DRY principle.

    Args:
        source_file: Path to the source file
        tree: Parsed AST tree from javalang

    Returns:
        List of JavaClassState objects, one per class in the file
    """
    classes: list[JavaClassState] = []
    file_content = Path(source_file).read_text(encoding="utf-8") if Path(source_file).exists() else None
    package_name = tree.package.name if tree.package else None

    # Extract imports once for all classes in file
    imports_list: list[ImportState] = []
    for imp in tree.imports:
        is_static = getattr(imp, "static", False)
        imports_list.append({
            "name": imp.path,
            "is_static": is_static,
            "is_wildcard": "*" in imp.path,
            "line_number": None
        })

    # Extract each class in the file
    for path_elem, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            modifiers = list(node.modifiers) if node.modifiers else []
            extends = node.extends.name if node.extends else None
            implements = [impl.name for impl in node.implements] if node.implements else []

            # Extract fields and methods using helpers
            fields = _extract_fields_from_node(node)
            methods = _extract_methods_from_node(node)

            # Extract class annotations
            class_annotations: list[AnnotationState] = []
            for ann in (node.annotations if node.annotations else []):
                ann_name = ann.name if hasattr(ann, "name") else str(ann)
                ann_elements = {}
                if hasattr(ann, "element"):
                    ann_elements[ann.element.name] = str(ann.element)

                class_annotations.append({
                    "name": ann_name,
                    "elements": ann_elements,
                    "target": "class",
                    "line_number": None
                })

            class_state: JavaClassState = {
                "name": node.name,
                "file_path": source_file,
                "package": package_name,
                "content": file_content,
                "type": "class",
                "modifiers": modifiers,
                "extends": extends,
                "implements": implements,
                "annotations": class_annotations,
                "fields": fields,
                "methods": methods,
                "imports": imports_list,
                "inner_classes": [],
                "status": "analyzed",
                "errors": [],
                "line_number": None
            }
            classes.append(class_state)

    return classes


def _analyze_java_class_impl(path: Optional[str] = None, source_code: Optional[str] = None) -> JavaClassState:
    """Analyze a single Java class from file path or source code.

    CANONICAL entry point for Java class analysis. Returns complete JavaClassState
    with all class information (methods, fields, imports, annotations, etc.).

    Args:
        path: File path to Java source file (e.g., "/path/to/User.java")
              If provided, source_code must be None
        source_code: Full Java source code as string (e.g., "public class User { ... }")
                    If provided, path must be None

    Returns:
        JavaClassState: Complete class information including:
            - name: Class name
            - fields: List of FieldState objects
            - methods: List of MethodState objects
            - imports: List of ImportState objects
            - annotations: List of AnnotationState objects
            - package: Package name
            - extends: Parent class name
            - implements: Interface names
            - status: "analyzed" or "error"
            - errors: List of error messages if any

    Raises:
        ValueError: If both path and source_code are provided, or neither are provided

    Note: Returns the FIRST class found in the source/file.
    Use list_java_classes() for directory iteration.

    This is the ATOMIC operation - all class analysis flows through here.
    """
    try:
        # Validation: exactly one parameter must be provided
        if path and source_code:
            raise ValueError("Provide either 'path' OR 'source_code', not both")

        if not path and not source_code:
            return _make_error_class_state(
                "Provide either 'path' or 'source_code' parameter",
                "<empty>"
            )

        # Handle file path
        if path:
            validate_java_file(path)
            file_path = path
            tree = _parse_java_file(file_path)
        else:
            # Handle source code
            file_path = "<inline_source>"
            try:
                tree = javalang.parse.parse(source_code)
            except Exception:
                tree = None

        if not tree:
            return _make_error_class_state(
                "Failed to parse Java source",
                file_path
            )

        # Use unified extraction logic - SINGLE SOURCE OF TRUTH
        classes = _extract_class_details_from_tree(file_path, tree)

        if not classes:
            return _make_error_class_state(
                "No classes found in source",
                file_path
            )

        # Return the first class
        return classes[0]

    except ValueError as e:
        # Re-raise validation errors
        return _make_error_class_state(str(e), path or "<inline_source>")
    except Exception as e:
        return _make_error_class_state(str(e), path or "<inline_source>")


@tool
def analyze_java_class(path: Optional[str] = None, source_code: Optional[str] = None) -> JavaClassState:
    """Decorated wrapper for Java class analysis (see _analyze_java_class_impl for docs)."""
    return _analyze_java_class_impl(path=path, source_code=source_code)


def _list_java_files(directory: str) -> list[Path]:
    """Get all Java file paths in directory (private helper for file discovery).

    Args:
        directory: Directory path to search for Java files

    Returns:
        List of Path objects for all .java files found (sorted)
    """
    path = validate_directory_exists(directory)
    return sorted(path.rglob("*.java"))


@tool
def list_java_classes(directory: str) -> list[JavaClassState]:
    """Analyze all Java classes in a directory.

    Iterates through all .java files in directory (recursively) and returns
    a list of JavaClassState objects. Uses _analyze_java_class_impl() internally
    for consistent analysis.

    Args:
        directory: Directory path to search for Java files

    Returns:
        List[JavaClassState]: All Java classes found, each with complete analysis

    This is a convenience function that combines file discovery with analysis.
    Replaces find_java_files() for most use cases.
    """
    try:
        java_files = _list_java_files(directory)

        if not java_files:
            return []

        results: list[JavaClassState] = []
        for java_file in java_files:
            try:
                class_state = _analyze_java_class_impl(path=str(java_file))
                results.append(class_state)
            except Exception as e:
                # Include error states for failed analyses
                results.append(_make_error_class_state(
                    f"Failed to analyze: {str(e)}",
                    str(java_file)
                ))

        return results

    except Exception as e:
        # Return empty list with error in logging (directory validation failed)
        return []


def _make_error_class_state(error_msg: str, file_path: str) -> JavaClassState:
    """Create an error JavaClassState for failed analysis."""
    path = Path(file_path)
    return {
        "name": path.stem if file_path != "<inline_source>" else "unknown",
        "file_path": file_path,
        "package": None,
        "content": None,
        "type": "class",
        "modifiers": [],
        "extends": None,
        "implements": [],
        "annotations": [],
        "fields": [],
        "methods": [],
        "imports": [],
        "inner_classes": [],
        "status": "error",
        "errors": [error_msg],
        "line_number": None
    }


@tool
def add_import(source_file: str, import_path: str) -> str:
    """Add an import statement to a Java file."""
    try:
        validate_java_file(source_file)
        validate_not_empty(import_path, "import_path")
        
        path = validate_file_exists(source_file)
        content = path.read_text(encoding="utf-8")
        tree = _parse_java_file(source_file)
        
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        new_import = f"import {import_path};"
        
        for imp in tree.imports:
            if imp.path == import_path:
                return f"Import '{import_path}' already exists"
        
        lines = content.split("\n")
        package_line_idx = -1
        
        if tree.package:
            for i, line in enumerate(lines):
                if line.strip().startswith("package "):
                    package_line_idx = i
                    break
        
        if package_line_idx >= 0:
            lines.insert(package_line_idx + 1, new_import)
        else:
            first_class_line = -1
            for i, line in enumerate(lines):
                if "class " in line or "interface " in line or "enum " in line:
                    first_class_line = i
                    break
            
            if first_class_line >= 0:
                lines.insert(first_class_line, new_import)
            else:
                lines.insert(0, new_import)
        
        new_content = "\n".join(lines)
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully added import: {import_path}"
    except Exception as e:
        response = create_error_response(e)
        return f"Error adding import: {response['errors'][0]}"


@tool
def remove_import(source_file: str, import_path: str) -> str:
    """Remove an import statement from a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        tree = _parse_java_file(source_file)
        
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        lines = content.split("\n")
        new_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped == f"import {import_path};" or stripped.startswith(f"import {import_path} "):
                continue
            new_lines.append(line)
        
        new_content = "\n".join(new_lines)
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully removed import: {import_path}"
    except Exception as e:
        return f"Error removing import: {str(e)}"


@tool
def replace_import(source_file: str, old_import: str, new_import: str) -> str:
    """Replace an import statement in a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        
        new_content = content.replace(f"import {old_import};", f"import {new_import};")
        
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully replaced import '{old_import}' with '{new_import}'"
    except Exception as e:
        return f"Error replacing import: {str(e)}"


@tool
def comment_import(source_file: str, import_path: str) -> str:
    """Comment out an import statement in a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        
        new_content = content.replace(f"import {import_path};", f"// import {import_path};")
        
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully commented out import: {import_path}"
    except Exception as e:
        return f"Error commenting import: {str(e)}"


@tool
def add_field(source_file: str, class_name: str, field_declaration: str) -> str:
    """Add a field to a specific class in a Java file."""
    try:
        validate_java_file(source_file)
        validate_class_name(class_name)
        validate_not_empty(field_declaration, "field_declaration")
        
        path = validate_file_exists(source_file)
        content = path.read_text(encoding="utf-8")
        tree = _parse_java_file(source_file)
        
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        lines = content.split("\n")
        class_open_brace_idx = -1
        
        for path_info, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration) and node.name == class_name:
                for i, line in enumerate(lines):
                    if f"class {class_name}" in line:
                        for j in range(i, len(lines)):
                            if "{" in lines[j]:
                                class_open_brace_idx = j + lines[j].index("{") + 1
                                break
                        break
        
        if class_open_brace_idx == -1:
            return f"Error: Class '{class_name}' not found"
        
        indent = "    "
        lines.insert(class_open_brace_idx + 1, f"{indent}{field_declaration};")
        
        new_content = "\n".join(lines)
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully added field to class '{class_name}': {field_declaration}"
    except Exception as e:
        response = create_error_response(e)
        return f"Error adding field: {response['errors'][0]}"


@tool
def remove_field(source_file: str, class_name: str, field_name: str) -> str:
    """Remove a field from a specific class in a Java file."""
    try:
        validate_java_file(source_file)
        validate_class_name(class_name)
        validate_field_name(field_name)
        
        path = validate_file_exists(source_file)
        content = path.read_text(encoding="utf-8")
        tree = _parse_java_file(source_file)
        
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        lines = content.split("\n")
        class_start = -1
        class_end = -1
        class_stack = 0
        
        for i, line in enumerate(lines):
            if f"class {class_name}" in line:
                class_start = i
                break
        
        if class_start == -1:
            return f"Error: Class '{class_name}' not found"
        
        for i in range(class_start, len(lines)):
            if "{" in lines[i]:
                class_stack += lines[i].count("{")
            if "}" in lines[i]:
                class_stack -= lines[i].count("}")
            if class_stack == 0:
                class_end = i
                break
        
        new_lines = lines[:class_start] + lines[class_end + 1:]
        
        for i in range(class_start, class_end):
            if field_name in lines[i] and "=" in lines[i]:
                new_lines.append(lines[i])
        
        new_content = "\n".join(new_lines)
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully removed field '{field_name}' from class '{class_name}'"
    except Exception as e:
        return f"Error removing field: {str(e)}"


@tool
def replace_field(source_file: str, class_name: str, old_field: str, new_field: str) -> str:
    """Replace a field in a specific class in a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        
        new_content = content.replace(old_field, new_field)
        
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully replaced field in class '{class_name}'"
    except Exception as e:
        return f"Error replacing field: {str(e)}"


@tool
def comment_field(source_file: str, class_name: str, field_name: str) -> str:
    """Comment out a field in a specific class in a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        
        lines = content.split("\n")
        new_lines = []
        
        for line in lines:
            if field_name in line and "private" in line or "public" in line or "protected" in line:
                new_lines.append(f"// {line}")
            else:
                new_lines.append(line)
        
        new_content = "\n".join(new_lines)
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully commented out field '{field_name}' in class '{class_name}'"
    except Exception as e:
        return f"Error commenting field: {str(e)}"


@tool
def add_method(source_file: str, class_name: str, method_declaration: str) -> str:
    """Add a method to a specific class in a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        tree = _parse_java_file(source_file)
        
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        lines = content.split("\n")
        class_open_brace_idx = -1
        
        for path_info, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration) and node.name == class_name:
                for i, line in enumerate(lines):
                    if f"class {class_name}" in line:
                        for j in range(i, len(lines)):
                            if "{" in lines[j]:
                                class_open_brace_idx = j + lines[j].index("{") + 1
                                break
                        break
        
        if class_open_brace_idx == -1:
            return f"Error: Class '{class_name}' not found"
        
        indent = "    "
        method_lines = method_declaration.split("\n")
        for i, ml in enumerate(method_lines):
            method_lines[i] = f"{indent}{ml}"
        
        lines.insert(class_open_brace_idx + 1, "\n".join(method_lines))
        
        new_content = "\n".join(lines)
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully added method to class '{class_name}'"
    except Exception as e:
        return f"Error adding method: {str(e)}"


@tool
def remove_method(source_file: str, class_name: str, method_name: str) -> str:
    """Remove a method from a specific class in a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        
        lines = content.split("\n")
        new_lines = []
        in_method = False
        brace_stack = 0
        
        for line in lines:
            if f"{method_name}(" in line:
                in_method = True
            
            if in_method:
                if "{" in line:
                    brace_stack += line.count("{")
                if "}" in line:
                    brace_stack -= line.count("}")
                if brace_stack <= 0 and "}" in line:
                    in_method = False
                    continue
            
            new_lines.append(line)
        
        new_content = "\n".join(new_lines)
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully removed method '{method_name}' from class '{class_name}'"
    except Exception as e:
        return f"Error removing method: {str(e)}"


@tool
def replace_method(source_file: str, class_name: str, old_method: str, new_method: str) -> str:
    """Replace a method in a specific class in a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        
        new_content = content.replace(old_method, new_method)
        
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully replaced method in class '{class_name}'"
    except Exception as e:
        return f"Error replacing method: {str(e)}"


@tool
def comment_method(source_file: str, class_name: str, method_name: str) -> str:
    """Comment out a method in a specific class in a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        
        lines = content.split("\n")
        new_lines = []
        in_method = False
        brace_stack = 0
        
        for line in lines:
            if f"{method_name}(" in line:
                in_method = True
                new_lines.append(f"// {line}")
            elif in_method:
                new_lines.append(f"// {line}")
                if "{" in line:
                    brace_stack += line.count("{")
                if "}" in line:
                    brace_stack -= line.count("}")
                if brace_stack <= 0 and "}" in line:
                    in_method = False
            else:
                new_lines.append(line)
        
        new_content = "\n".join(new_lines)
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully commented out method '{method_name}' in class '{class_name}'"
    except Exception as e:
        return f"Error commenting method: {str(e)}"


@tool
def add_annotation(source_file: str, target: str, annotation: str) -> str:
    """Add an annotation to a class, method, or field."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        
        annotation_with_at = f"@{annotation}" if not annotation.startswith("@") else annotation
        new_content = content.replace(target, f"{annotation_with_at}\n    {target}")
        
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully added annotation '{annotation_with_at}' to '{target}'"
    except Exception as e:
        return f"Error adding annotation: {str(e)}"


@tool
def remove_annotation(source_file: str, annotation: str) -> str:
    """Remove an annotation from a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        
        annotation_with_at = f"@{annotation}" if not annotation.startswith("@") else annotation
        new_content = content.replace(annotation_with_at, "")
        
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully removed annotation: {annotation_with_at}"
    except Exception as e:
        return f"Error removing annotation: {str(e)}"


@tool
def replace_annotation(source_file: str, old_annotation: str, new_annotation: str) -> str:
    """Replace an annotation in a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        
        old_with_at = f"@{old_annotation}" if not old_annotation.startswith("@") else old_annotation
        new_with_at = f"@{new_annotation}" if not new_annotation.startswith("@") else new_annotation
        new_content = content.replace(old_with_at, new_with_at)
        
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully replaced annotation '{old_with_at}' with '{new_with_at}'"
    except Exception as e:
        return f"Error replacing annotation: {str(e)}"


@tool
def comment_annotation(source_file: str, annotation: str) -> str:
    """Comment out an annotation in a Java file."""
    try:
        path = Path(source_file)
        if not path.exists():
            return f"Error: File '{source_file}' does not exist"
        
        content = path.read_text(encoding="utf-8")
        
        annotation_with_at = f"@{annotation}" if not annotation.startswith("@") else annotation
        new_content = content.replace(annotation_with_at, f"// {annotation_with_at}")
        
        path.write_text(new_content, encoding="utf-8")
        
        return f"Successfully commented out annotation: {annotation_with_at}"
    except Exception as e:
        return f"Error commenting annotation: {str(e)}"


def extract_classes_from_tree(tree: javalang.tree.CompilationUnit, source_file: str = "<unknown>") -> list[JavaClassState]:
    """Extract class information from a parsed AST tree.

    This function encapsulates javalang-specific logic for agent use.
    Returns structured JavaClassState objects for use across all layers.

    Agents should call this instead of directly accessing javalang types.

    Args:
        tree: Parsed AST tree from javalang
        source_file: Path to source file (for context in returned states)

    Returns:
        List of JavaClassState objects with full class details
    """
    return _extract_class_details_from_tree(source_file, tree)


java_tools = [
    # Core Analysis Tools
    analyze_java_class,
    list_java_classes,
    # Modification tools
    add_import,
    remove_import,
    replace_import,
    comment_import,
    add_field,
    remove_field,
    replace_field,
    comment_field,
    add_method,
    remove_method,
    replace_method,
    comment_method,
    add_annotation,
    remove_annotation,
    replace_annotation,
    comment_annotation
]
