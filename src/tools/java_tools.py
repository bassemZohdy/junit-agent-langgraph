import javalang
from pathlib import Path
from typing import Optional
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
from ..states.java_project_states import (
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
    for path, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            return node.name
        if isinstance(node, javalang.tree.InterfaceDeclaration):
            return node.name
        if isinstance(node, javalang.tree.EnumDeclaration):
            return node.name
    return None


@tool
def find_java_files(directory: str) -> str:
    """Find all Java source files in a directory."""
    try:
        path = validate_directory_exists(directory)
        java_files = [str(f) for f in path.rglob("*.java")]
        return "\n".join(java_files) if java_files else "No Java files found"
    except Exception as e:
        response = create_error_response(e)
        return f"Error finding Java files: {response['errors'][0]}"


@tool
def create_java_class_state(source_file: str) -> JavaClassState:
    """Create JavaClassState from a Java source file."""
    try:
        path = validate_java_file(source_file)
        
        tree = _parse_java_file(source_file)
        if not tree:
            return {
                "name": path.stem,
                "file_path": source_file,
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
                "errors": ["Failed to parse Java file"],
                "line_number": None
            }
        
        class_name = _extract_class_name(source_file, tree) or path.stem
        
        fields: list[FieldState] = []
        methods: list[MethodState] = []
        imports: list[ImportState] = []
        annotations: list[AnnotationState] = []
        modifiers: list[str] = []
        extends: Optional[str] = None
        implements: list[str] = []
        inner_classes: list[str] = []
        
        for path, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration):
                for modifier in node.modifiers:
                    if modifier not in modifiers:
                        modifiers.append(modifier)
                
                if node.extends:
                    extends = node.extends.name
                
                if node.implements:
                    implements = [impl.name for impl in node.implements]
                
                for field in node.fields:
                    field_modifiers = [m for m in field.modifiers]
                    is_static = "static" in field_modifiers
                    is_final = "final" in field_modifiers
                    field_annotations = []
                    
                    for decl in field.declarators:
                        field_type = str(field.type) if field.type else "Object"
                        
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
                
                for method in node.methods:
                    method_modifiers = [m for m in method.modifiers]
                    is_static = "static" in method_modifiers
                    is_abstract = "abstract" in method_modifiers
                    is_final = "final" in method_modifiers
                    method_annotations = []
                    throws = []
                    
                    if method.throws:
                        for throw_clause in method.throws:
                            throws.append(throw_clause.name if throw_clause.name else str(throw_clause))
                    
                    method_annotations.extend([
                        {
                            "name": ann.name if hasattr(ann, "name") else str(ann),
                            "elements": ann_elements if hasattr(ann, "element") else {},
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
                            "position": "method parameter" if not hasattr(param, "position") else None
                        })
                    
                    methods.append({
                        "name": method.name,
                        "return_type": str(method.return_type) if method.return_type else "void",
                        "parameters": parameters,
                        "modifiers": method_modifiers,
                        "is_static": is_static,
                        "is_abstract": is_abstract,
                        "is_final": is_final,
                        "annotations": method_annotations,
                        "throws": throws,
                        "body": None,
                        "line_number": None
                    })
        
        imports_list: list[ImportState] = []
        for imp in tree.imports:
            is_static = imp.static if hasattr(imp, "static") and imp.static else False
            is_wildcard = False
            
            imports_list.append({
                "name": imp.path,
                "is_static": is_static,
                "is_wildcard": is_wildcard,
                "line_number": None
            })
        
        class_annotations: list[AnnotationState] = []
        for ann in node.annotations:
            ann_name = ann.name if hasattr(ann, "name") else str(ann)
            ann_elements = {}
            
            if hasattr(ann, "element"):
                ann_elements[ann.element.name] = str(ann.element)
            
            target = None
            if hasattr(node, javalang.tree.ClassDeclaration):
                target = "class"
            elif hasattr(node, javalang.tree.FieldDeclaration):
                target = "field"
            elif hasattr(node, javalang.tree.MethodDeclaration):
                target = "method"
            
            class_annotations.append({
                "name": ann_name,
                "elements": ann_elements,
                "target": target,
                "line_number": None
            })
        
        package_name = tree.package.name if tree.package else None
        
        return {
            "name": class_name,
            "file_path": source_file,
            "package": package_name,
            "content": path.read_text(encoding="utf-8"),
            "type": "class",
            "modifiers": modifiers,
            "extends": extends,
            "implements": implements,
            "annotations": class_annotations,
            "fields": fields,
            "methods": methods,
            "imports": imports_list,
            "inner_classes": inner_classes,
            "status": "analyzed",
            "errors": [],
            "line_number": None
        }
    except Exception as e:
        return {
            "name": path.stem,
            "file_path": source_file,
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
            "errors": [str(e)],
            "line_number": None
        }
        
        tree = _parse_java_file(source_file)
        if not tree:
            return {
                "name": Path(source_file).stem,
                "file_path": source_file,
                "package": tree.package.name if tree.package else None,
                "content": path.read_text(encoding="utf-8"),
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
                "errors": ["Failed to parse Java file"],
                "line_number": None
            }
        
        class_name = _extract_class_name(source_file, tree) or Path(source_file).stem
        
        return {
            "name": class_name,
            "file_path": source_file,
            "package": tree.package.name if tree.package else None,
            "content": path.read_text(encoding="utf-8"),
            "type": "class",
            "modifiers": [],
            "extends": None,
            "implements": [],
            "annotations": [],
            "fields": [],
            "methods": [],
            "imports": [],
            "inner_classes": [],
            "status": "analyzed",
            "errors": [],
            "line_number": None
        }
    except Exception as e:
        return {
            "name": "",
            "file_path": source_file,
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
            "errors": [str(e)],
            "line_number": None
        }


@tool
def get_java_classes(source_file: str) -> str:
    """Get all classes declared in a Java file."""
    try:
        validate_java_file(source_file)
        tree = _parse_java_file(source_file)
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        classes = []
        for path, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration):
                extends_str = f" (extends {node.extends.name})" if node.extends else ""
                classes.append(f"Class: {node.name}{extends_str}")
            elif isinstance(node, javalang.tree.InterfaceDeclaration):
                classes.append(f"Interface: {node.name}")
            elif isinstance(node, javalang.tree.EnumDeclaration):
                classes.append(f"Enum: {node.name}")
        
        return "\n".join(classes) if classes else "No classes found"
    except Exception as e:
        response = create_error_response(e)
        return f"Error getting classes: {response['errors'][0]}"


@tool
def get_java_methods(source_file: str, class_name: Optional[str] = None) -> str:
    """Get all methods from a Java file or specific class."""
    try:
        validate_java_file(source_file)
        if class_name:
            validate_class_name(class_name)
        tree = _parse_java_file(source_file)
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        methods_info = []
        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                modifiers = " ".join(node.modifiers) if node.modifiers else ""
                return_type = node.return_type.name if node.return_type else "void"
                params = ", ".join([f"{p.type.name} {p.name}" for p in node.parameters]) if node.parameters else ""
                methods_info.append(f"  {modifiers} {return_type} {node.name}({params})")
        
        return "\n".join(methods_info) if methods_info else "No methods found"
    except Exception as e:
        return f"Error getting methods: {str(e)}"


@tool
def get_java_fields(source_file: str, class_name: Optional[str] = None) -> str:
    """Get all fields from a Java file or specific class."""
    try:
        tree = _parse_java_file(source_file)
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        fields_info = []
        for path, node in tree:
            if isinstance(node, javalang.tree.FieldDeclaration):
                modifiers = " ".join(node.modifiers) if node.modifiers else ""
                field_type = node.type.name
                declarators = [f"{d.name}" for d in node.declarators]
                fields_info.append(f"  {modifiers} {field_type} {', '.join(declarators)}")
        
        return "\n".join(fields_info) if fields_info else "No fields found"
    except Exception as e:
        return f"Error getting fields: {str(e)}"


@tool
def get_java_imports(source_file: str) -> str:
    """Get all imports from a Java file."""
    try:
        tree = _parse_java_file(source_file)
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        imports = [imp.path for imp in tree.imports]
        return "\n".join(imports) if imports else "No imports found"
    except Exception as e:
        return f"Error getting imports: {str(e)}"


@tool
def get_java_annotations(source_file: str, target_type: Optional[str] = None) -> str:
    """Get all annotations from a Java file. Target type can be 'class', 'method', 'field'."""
    try:
        tree = _parse_java_file(source_file)
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        annotations_info = []
        
        for path, node in tree:
            if hasattr(node, 'annotations') and node.annotations:
                node_type = type(node).__name__
                if target_type is None or (target_type and target_type.lower() in node_type.lower()):
                    for ann in node.annotations:
                        ann_name = ann.name if hasattr(ann, 'name') else str(ann)
                        element = ""
                        if hasattr(ann, 'element') and ann.element:
                            element = f"({ann.element})"
                        annotations_info.append(f"  @{ann_name}{element} on {node_type}")
        
        return "\n".join(annotations_info) if annotations_info else "No annotations found"
    except Exception as e:
        return f"Error getting annotations: {str(e)}"


@tool
def get_java_package(source_file: str) -> str:
    """Get package declaration from a Java file."""
    try:
        tree = _parse_java_file(source_file)
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        return tree.package.name if tree.package else "No package declaration"
    except Exception as e:
        return f"Error getting package: {str(e)}"


@tool
def analyze_java_class(source_file: str, class_name: Optional[str] = None) -> str:
    """Get complete analysis of a Java class including fields, methods, annotations."""
    try:
        tree = _parse_java_file(source_file)
        if not tree:
            return f"Error: Could not parse '{source_file}'"
        
        analysis = []
        analysis.append(f"File: {source_file}")
        analysis.append(f"Package: {tree.package.name if tree.package else 'default'}")
        
        for path, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration):
                if class_name is None or node.name == class_name:
                    analysis.append(f"\nClass: {node.name}")
                    
                    if node.extends:
                        analysis.append(f"  Extends: {node.extends.name}")
                    
                    if node.implements:
                        impl_names = [impl.name for impl in node.implements]
                        analysis.append(f"  Implements: {', '.join(impl_names)}")
                    
                    if node.annotations:
                        ann_names = [ann.name for ann in node.annotations]
                        analysis.append(f"  Annotations: {', '.join(ann_names)}")
        
        analysis.append("\nImports:")
        analysis.extend([f"  {imp.path}" for imp in tree.imports])
        
        return "\n".join(analysis)
    except Exception as e:
        return f"Error analyzing class: {str(e)}"


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


java_tools = [
    find_java_files,
    create_java_class_state,
    get_java_classes,
    get_java_methods,
    get_java_fields,
    get_java_imports,
    get_java_annotations,
    get_java_package,
    analyze_java_class,
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
