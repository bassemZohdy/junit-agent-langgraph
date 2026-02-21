import javalang
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from langchain_core.tools import tool
from ..exceptions.handler import FileOperationError, ValidationError, create_error_response
from ..utils.validation import validate_file_exists, validate_class_name, validate_not_empty


@tool
def generate_getters_setters(java_file: str, class_name: str) -> str:
    """Generate getters and setters for all fields in a Java class."""
    try:
        validate_file_exists(java_file)
        validate_class_name(class_name)
        
        content = Path(java_file).read_text(encoding="utf-8")
        tree = javalang.parse.parse(content)
        
        target_class = None
        for path_info, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration) and node.name == class_name:
                target_class = node
                break
        
        if not target_class:
            return f"Error: Class '{class_name}' not found in file"
        
        if not target_class.fields:
            return f"Error: Class '{class_name}' has no fields"
        
        generated_code = []
        indent = "    "
        
        for field in target_class.fields:
            if not field.name or not field.type:
                continue
            
            field_type_name = get_type_name(field.type)
            field_name = field.name
            
            getter_name = f"get{field_name[0].upper()}{field_name[1:]}"
            setter_name = f"set{field_name[0].upper()}{field_name[1:]}"
            
            generated_code.append(f"{indent}public {field_type_name} {getter_name() {{")
            generated_code.append(f"{indent}{indent}return this.{field_name};")
            generated_code.append(f"{indent}}}")
            generated_code.append("")
            
            generated_code.append(f"{indent}public void {setter_name}({field_type_name} {field_name}) {{")
            generated_code.append(f"{indent}{indent}this.{field_name} = {field_name};")
            generated_code.append(f"{indent}}}")
            generated_code.append("")
        
        return "\n".join(generated_code)
    except Exception as e:
        response = create_error_response(e)
        return f"Error generating getters/setters: {response['errors'][0]}"


@tool
def generate_constructor(java_file: str, class_name: str, include_all_fields: bool = True) -> str:
    """Generate a constructor for a Java class."""
    try:
        validate_file_exists(java_file)
        validate_class_name(class_name)
        
        content = Path(java_file).read_text(encoding="utf-8")
        tree = javalang.parse.parse(content)
        
        target_class = None
        for path_info, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration) and node.name == class_name:
                target_class = node
                break
        
        if not target_class:
            return f"Error: Class '{class_name}' not found in file"
        
        if not target_class.fields:
            return f"Error: Class '{class_name}' has no fields"
        
        indent = "    "
        
        if include_all_fields:
            params = []
            assignments = []
            
            for field in target_class.fields:
                if not field.name or not field.type:
                    continue
                
                field_type_name = get_type_name(field.type)
                field_name = field.name
                
                params.append(f"{field_type_name} {field_name}")
                assignments.append(f"{indent}{indent}this.{field_name} = {field_name};")
            
            params_str = ", ".join(params)
            assignments_str = "\n".join(assignments)
            
            constructor_code = [
                f"{indent}public {class_name}({params_str}) {{",
                assignments_str,
                f"{indent}}}"
            ]
        else:
            constructor_code = [
                f"{indent}public {class_name}() {{",
                f"{indent}}}"
            ]
        
        return "\n".join(constructor_code)
    except Exception as e:
        response = create_error_response(e)
        return f"Error generating constructor: {response['errors'][0]}"


@tool
def generate_tostring_equals_hashcode(java_file: str, class_name: str) -> str:
    """Generate toString, equals, and hashCode methods for a Java class."""
    try:
        validate_file_exists(java_file)
        validate_class_name(class_name)
        
        content = Path(java_file).read_text(encoding="utf-8")
        tree = javalang.parse.parse(content)
        
        target_class = None
        for path_info, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration) and node.name == class_name:
                target_class = node
                break
        
        if not target_class:
            return f"Error: Class '{class_name}' not found in file"
        
        if not target_class.fields:
            return f"Error: Class '{class_name}' has no fields"
        
        indent = "    "
        generated_code = []
        
        generated_code.append(f"{indent}@Override")
        generated_code.append(f"{indent}public String toString() {{")
        generated_code.append(f"{indent}{indent}return \"{class_name}{{\" +")
        
        field_parts = []
        for i, field in enumerate(target_class.fields):
            if not field.name:
                continue
            if i > 0:
                field_parts.append(f" \", \" +")
            field_parts.append(f"{field.name}=\" + this.{field.name}")
        
        generated_code.append(f"{indent}{indent}{indent}\" + \", \".join(field_parts) + '}}'")
        generated_code.append(f"{indent}}}")
        generated_code.append("")
        
        generated_code.append(f"{indent}@Override")
        generated_code.append(f"{indent}public boolean equals(Object o) {{")
        generated_code.append(f"{indent}{indent}if (this == o) return true;")
        generated_code.append(f"{indent}{indent}if (o == null || getClass() != o.getClass()) return false;")
        generated_code.append(f"{indent}{indent}{class_name} that = ({class_name}) o;")
        generated_code.append("")
        
        conditions = []
        for field in target_class.fields:
            if not field.name:
                continue
            field_name = field.name
            conditions.append(f"{indent}{indent}Objects.equals({field_name}, that.{field_name})")
        
        if conditions:
            generated_code.append(f"{indent}{indent}return {' && '.join(conditions)};")
        else:
            generated_code.append(f"{indent}{indent}return true;")
        
        generated_code.append(f"{indent}}}")
        generated_code.append("")
        
        generated_code.append(f"{indent}@Override")
        generated_code.append(f"{indent}public int hashCode() {{")
        generated_code.append(f"{indent}{indent}return Objects.hash(")
        
        hash_fields = []
        for field in target_class.fields:
            if field.name:
                hash_fields.append(f"{field.name}")
        
        generated_code.append(f"{indent}{indent}{indent}}};")
        generated_code.append(f"{indent}}}")
        generated_code.append("")
        
        return "\n".join(generated_code)
    except Exception as e:
        response = create_error_response(e)
        return f"Error generating methods: {response['errors'][0]}"


@tool
def generate_builder_pattern(java_file: str, class_name: str) -> str:
    """Generate a builder pattern for a Java class."""
    try:
        validate_file_exists(java_file)
        validate_class_name(class_name)
        
        content = Path(java_file).read_text(encoding="utf-8")
        tree = javalang.parse.parse(content)
        
        target_class = None
        for path_info, node in tree:
            if isinstance(node, javalang.tree.ClassDeclaration) and node.name == class_name:
                target_class = node
                break
        
        if not target_class:
            return f"Error: Class '{class_name}' not found in file"
        
        if not target_class.fields:
            return f"Error: Class '{class_name}' has no fields"
        
        builder_name = f"{class_name}Builder"
        indent = "    "
        builder_code = []
        
        builder_code.append(f"{indent}public static class {builder_name} {{")
        builder_code.append("")
        
        for field in target_class.fields:
            if not field.name or not field.type:
                continue
            
            field_type_name = get_type_name(field.type)
            field_name = field.name
            builder_field_name = f"_{field_name}"
            
            builder_code.append(f"{indent}{indent}private {field_type_name} {builder_field_name};")
            builder_code.append("")
        
        builder_code.append(f"{indent}{indent}public {builder_name}Builder {field.name}({field_type_name} {field.name}) {{")
        
        for field in target_class.fields:
            if not field.name:
                continue
            field_name = field.name
            builder_field_name = f"_{field_name}"
            builder_code.append(f"{indent}{indent}{indent}this.{builder_field_name} = {field_name};")
        
        builder_code.append(f"{indent}{indent}return this;")
        builder_code.append(f"{indent}}}")
        builder_code.append("")
        
        for field in target_class.fields:
            if not field.name or not field.type:
                continue
            
            field_type_name = get_type_name(field.type)
            field_name = field.name
            builder_field_name = f"_{field_name}"
            
            method_name = f"{field.name}"
            builder_code.append(f"{indent}{indent}public {builder_name}Builder {method_name}({field_type_name} {field_name}) {{")
            builder_code.append(f"{indent}{indent}{indent}this.{builder_field_name} = {field_name};")
            builder_code.append(f"{indent}{indent}{indent}return this;")
            builder_code.append(f"{indent}{indent}}}")
            builder_code.append("")
        
        builder_code.append(f"{indent}{indent}public {class_name} build() {{")
        builder_code.append(f"{indent}{indent}{indent}return new {class_name}(")
        
        build_params = []
        for field in target_class.fields:
            if not field.name:
                continue
            field_name = field.name
            builder_field_name = f"_{field_name}"
            build_params.append(f"{builder_field_name}")
        
        builder_code.append(f"{indent}{indent}{indent}\", \".join(build_params)});")
        builder_code.append(f"{indent}{indent}}}")
        builder_code.append("")
        
        builder_code.append(f"{indent}}}")
        builder_code.append("")
        
        builder_code.append(f"{indent}public {class_name} toBuilder() {{")
        builder_code.append(f"{indent}{indent}return new {builder_name}();")
        builder_code.append(f"{indent}}}")
        
        return "\n".join(builder_code)
    except Exception as e:
        response = create_error_response(e)
        return f"Error generating builder pattern: {response['errors'][0]}"


def get_type_name(type_node) -> str:
    """Extract type name from javalang type node."""
    if isinstance(type_node, str):
        return type_node
    elif isinstance(type_node, javalang.tree.Type):
        return str(type_node.name)
    elif hasattr(type_node, 'name'):
        return type_node.name
    else:
        return "Object"


code_generation_tools = [
    generate_getters_setters,
    generate_constructor,
    generate_tostring_equals_hashcode,
    generate_builder_pattern
]
