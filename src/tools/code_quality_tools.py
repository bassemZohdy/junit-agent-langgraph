import re
import javalang
from typing import List, Dict, Optional
from pathlib import Path
from langchain_core.tools import tool
from ..exceptions.handler import FileOperationError, ValidationError, create_error_response
from ..utils.validation import validate_file_exists, validate_class_name


class CodeSmell:
    """Represents a detected code smell."""
    name: str
    description: str
    line_number: Optional[int]
    severity: str


class SecurityIssue:
    """Represents a detected security issue."""
    name: str
    description: str
    line_number: Optional[int]
    severity: str


@tool
def detect_code_smells(java_file: str, class_name: str) -> str:
    """Detect code smells in a Java class."""
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
        
        smells = []
        
        smells.extend(_check_long_method(target_class))
        smells.extend(_check_long_parameter_list(target_class))
        smells.extend(_check_large_class(target_class))
        smells.extend(_check_few_methods_per_class(target_class))
        smells.extend(_check_commented_out_code(content))
        smells.extend(_check_magic_numbers(target_class))
        
        if not smells:
            return "No code smells detected"
        
        result = ["Code Smells Detected:"]
        for i, smell in enumerate(smells, 1):
            result.append(f"{i}. {smell.name} - {smell.description}")
            if smell.line_number:
                result.append(f"   Line: {smell.line_number}")
            result.append(f"   Severity: {smell.severity}")
        
        return "\n".join(result)
    except Exception as e:
        response = create_error_response(e)
        return f"Error detecting code smells: {response['errors'][0]}"


@tool
def detect_security_issues(java_file: str, class_name: str) -> str:
    """Detect potential security issues in Java code."""
    try:
        validate_file_exists(java_file)
        validate_class_name(class_name)
        
        content = Path(java_file).read_text(encoding="utf-8")
        
        issues = []
        
        issues.extend(_check_sql_injection(content))
        issues.extend(_check_command_injection(content))
        issues.extend(_check_weak_encryption(content))
        issues.extend(_check_hardcoded_secrets(content))
        issues.extend(_check_insecure_random(content))
        
        if not issues:
            return "No security issues detected"
        
        result = ["Security Issues Detected:"]
        for i, issue in enumerate(issues, 1):
            result.append(f"{i}. {issue.name} - {issue.description}")
            if issue.line_number:
                result.append(f"   Line: {issue.line_number}")
            result.append(f"   Severity: {issue.severity}")
        
        return "\n".join(result)
    except Exception as e:
        response = create_error_response(e)
        return f"Error detecting security issues: {response['errors'][0]}"


@tool
def check_naming_conventions(java_file: str, class_name: str) -> str:
    """Check naming conventions for Java class."""
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
        
        violations = []
        
        if not class_name[0].isupper():
            violations.append({
                "name": "Class Name",
                "description": f"Class name '{class_name}' should start with uppercase letter",
                "severity": "low"
            })
        
        for field in target_class.fields:
            if field.name:
                if field.name[0].isupper() and not field.name.isupper():
                    violations.append({
                        "name": "Field Name",
                        "description": f"Field '{field.name}' should start with lowercase letter",
                        "line_number": getattr(field, 'position', None),
                        "severity": "low"
                    })
        
        for method in target_class.methods:
            if method.name:
                if method.name[0].isupper() and not method.name.isupper():
                    violations.append({
                        "name": "Method Name",
                        "description": f"Method '{method.name}' should start with lowercase letter",
                        "line_number": getattr(method, 'position', None),
                        "severity": "low"
                    })
        
        if not violations:
            return "No naming convention violations"
        
        result = ["Naming Convention Violations:"]
        for i, violation in enumerate(violations, 1):
            result.append(f"{i}. {violation['name']} - {violation['description']}")
            if violation.get('line_number'):
                result.append(f"   Line: {violation['line_number']}")
            result.append(f"   Severity: {violation['severity']}")
        
        return "\n".join(result)
    except Exception as e:
        response = create_error_response(e)
        return f"Error checking naming conventions: {response['errors'][0]}"


def _check_long_method(class_node) -> List[CodeSmell]:
    smells = []
    for method in class_node.methods:
        if hasattr(method, 'position'):
            body_lines = _count_lines(method)
            if body_lines > 50:
                smells.append(CodeSmell(
                    name="Long Method",
                    description=f"Method '{method.name}' has {body_lines} lines (threshold: 50)",
                    line_number=method.position,
                    severity="medium"
                ))
    return smells


def _check_long_parameter_list(class_node) -> List[CodeSmell]:
    smells = []
    for method in class_node.methods:
        if method.parameters and len(method.parameters) > 7:
            smells.append(CodeSmell(
                name="Long Parameter List",
                description=f"Method '{method.name}' has {len(method.parameters)} parameters (threshold: 7)",
                line_number=getattr(method, 'position', None),
                severity="medium"
            ))
    return smells


def _check_large_class(class_node) -> List[CodeSmell]:
    smells = []
    total_lines = _count_lines(class_node)
    if total_lines > 500:
        smells.append(CodeSmell(
            name="Large Class",
            description=f"Class '{class_node.name}' has {total_lines} lines (threshold: 500)",
            line_number=getattr(class_node, 'position', None),
            severity="high"
        ))
    return smells


def _check_few_methods_per_class(class_node) -> List[CodeSmell]:
    if class_node.fields and class_node.fields:
        field_count = len(class_node.fields)
        method_count = len(class_node.methods)
        if field_count > method_count:
            smells.append(CodeSmell(
                name="God Class Anti-Pattern",
                description=f"Class has {field_count} fields but only {method_count} methods",
                line_number=getattr(class_node, 'position', None),
                severity="high"
            ))
    return []


def _check_commented_out_code(content: str) -> List[CodeSmell]:
    lines = content.split('\n')
    smells = []
    
    for i, line in enumerate(lines, 1):
        if re.match(r'^\s*//', line) or re.match(r'^\s*/\*', line):
            smells.append(CodeSmell(
                name="Commented Out Code",
                description="Commented out code detected",
                line_number=i,
                severity="low"
            ))
    return smells


def _check_magic_numbers(class_node) -> List[CodeSmell]:
    smells = []
    
    for method in class_node.methods:
        if hasattr(method, 'position'):
            literal_pattern = re.compile(r'\b\d+\b')
            body = str(method)
            matches = literal_pattern.findall(body)
            
            number_counts = {}
            for num in matches:
                if num in number_counts:
                    number_counts[num] += 1
                else:
                    number_counts[num] = 1
            
            for num, count in number_counts.items():
                if count > 2:
                    smells.append(CodeSmell(
                        name="Magic Number",
                        description=f"Number '{num}' appears {count} times in method '{method.name}'",
                        line_number=method.position,
                        severity="low"
                    ))
    return smells


def _check_sql_injection(content: str) -> List[SecurityIssue]:
    issues = []
    
    patterns = [
        (r'Statement\.execute\s*\(', 'SQL Injection via Statement.execute()'),
        (r'PreparedStatement\.', 'SQL Injection via PreparedStatement'),
        (r'createQuery\s*\(', 'SQL Injection via createQuery()'),
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        for pattern, desc in patterns:
            if re.search(pattern, line):
                issues.append(SecurityIssue(
                    name="SQL Injection Risk",
                    description=desc,
                    line_number=i,
                    severity="high"
                ))
    return issues


def _check_command_injection(content: str) -> List[SecurityIssue]:
    issues = []
    
    patterns = [
        (r'Runtime\.getRuntime\(\)\.exec\s*\(', 'Command Injection via Runtime.exec()'),
        (r'ProcessBuilder\s*\(', 'Command Injection via ProcessBuilder'),
        (r'exec\s*\(', 'Command Injection via exec()'),
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        for pattern, desc in patterns:
            if re.search(pattern, line):
                issues.append(SecurityIssue(
                    name="Command Injection Risk",
                    description=desc,
                    line_number=i,
                    severity="high"
                ))
    return issues


def _check_weak_encryption(content: str) -> List[SecurityIssue]:
    issues = []
    
    weak_patterns = [
        (r'DES/(ECB|CBC/PKCS5Padding)', 'Weak Encryption (DES)'),
        (r'MD5|SHA1|SHA-256(?!\(\w))', 'Weak Hash Algorithm (MD5, SHA1)'),
        (r'BouncyCastle|Crypto', 'Use of potentially weak cryptography library'),
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        for pattern, desc in weak_patterns:
            if re.search(pattern, line):
                issues.append(SecurityIssue(
                    name="Weak Cryptography",
                    description=desc,
                    line_number=i,
                    severity="medium"
                ))
    return issues


def _check_hardcoded_secrets(content: str) -> List[SecurityIssue]:
    issues = []
    
    patterns = [
        (r'password\s*=\s*["\']\w+', 'Hardcoded Password'),
        (r'api[_-]?key\s*=\s*["\']\w+', 'Hardcoded API Key'),
        (r'secret\s*=\s*["\']\w+', 'Hardcoded Secret'),
        (r'access[_-]?token\s*=\s*["\']\w+', 'Hardcoded Access Token'),
        (r'AKIA[A-Z0-9]{16}', 'AWS Access Key'),
        (r'sk-[a-zA-Z0-9]{32,48}', 'OpenAI API Key'),
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        for pattern, desc in patterns:
            if re.search(pattern, line):
                issues.append(SecurityIssue(
                    name="Hardcoded Secret",
                    description=desc,
                    line_number=i,
                    severity="critical"
                ))
    return issues


def _check_insecure_random(content: str) -> List[SecurityIssue]:
    issues = []
    
    insecure_patterns = [
        (r'Random\(\)', 'Insecure Random (non-cryptographic)'),
        (r'Math\.random\(\)', 'Insecure Random (non-cryptographic)'),
        (r'java\.util\.Random', 'Insecure Random (non-cryptographic)'),
    ]
    
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        for pattern, desc in insecure_patterns:
            if re.search(pattern, line):
                issues.append(SecurityIssue(
                    name="Insecure Random",
                    description=desc,
                    line_number=i,
                    severity="medium"
                ))
    return issues


def _count_lines(node) -> int:
    if hasattr(node, 'position'):
        start_line = node.position
        end_line = start_line + str(node).count('\n')
        return end_line - start_line + 1
    return 0


code_quality_tools = [
    detect_code_smells,
    detect_security_issues,
    check_naming_conventions
]
