import javalang
from typing import List


def extract_imports(tree: javalang.tree.CompilationUnit) -> List[str]:
    """Extract import statements from a parsed Java AST."""
    imports = []
    for path, node in tree:
        if isinstance(node, javalang.tree.Import):
            imports.append(node.path)
    return imports


def extract_dependencies(tree: javalang.tree.CompilationUnit, imports: List[str]) -> List[str]:
    """Extract external dependencies from a parsed Java AST."""
    dependencies = set()
    for path, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            for field in node.fields:
                type_str = str(field.type) if field.type else ""
                if type_str and "." in type_str:
                    dependencies.add(type_str)
            for method in node.methods:
                if method.return_type:
                    return_type_str = str(method.return_type)
                    if return_type_str and "." in return_type_str:
                        dependencies.add(return_type_str)
                for param in method.parameters:
                    param_type_str = str(param.type)
                    if param_type_str and "." in param_type_str:
                        dependencies.add(param_type_str)
    
    return list(dependencies)


def parse_java_file(content: str) -> javalang.tree.CompilationUnit:
    """Parse Java source code into an AST."""
    return javalang.parse.parse(content)


def extract_class_name_from_tree(tree: javalang.tree.CompilationUnit) -> str:
    """Extract the class name from a parsed Java AST."""
    for path, node in tree:
        if isinstance(node, javalang.tree.ClassDeclaration):
            return node.name
        if isinstance(node, javalang.tree.InterfaceDeclaration):
            return node.name
        if isinstance(node, javalang.tree.EnumDeclaration):
            return node.name
    return ""
