from typing import Optional, List
from langchain_core.messages import BaseMessage


def parse_code_from_response(content: str, language: str = "java") -> str:
    """
    Extract code block from LLM response.
    
    Args:
        content: The raw response content from LLM
        language: The programming language (default: "java")
    
    Returns:
        Cleaned code string without markdown formatting
    """
    if not content:
        return content
    
    cleaned = content.strip()
    
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 1)[1].strip()
        
        if cleaned.startswith(language):
            cleaned = cleaned[len(language):].strip()
        
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 1)[0].strip()
        else:
            cleaned = cleaned.rstrip("`").strip()
    
    return cleaned


def extract_list_from_response(content: str, prefix_chars: List[str] = None) -> List[str]:
    """
    Extract a list of items from LLM response.
    
    Args:
        content: The raw response content from LLM
        prefix_chars: List of characters that indicate list items (default: "-", "*", "•")
    
    Returns:
        List of extracted items
    """
    if prefix_chars is None:
        prefix_chars = ["-", "*", "•", "1.", "2.", "3.", "4.", "5."]
    
    if not content or content.lower() in ["no issues found", "no issues", "looks good", "no comments"]:
        return []
    
    items = []
    lines = content.split("\n")
    
    for line in lines:
        cleaned = line.strip()
        
        if not cleaned:
            continue
        
        if cleaned.lower() in ["```", "here are the review comments:", "comments:", "-"]:
            continue
        
        if cleaned[0] in prefix_chars:
            item = cleaned.lstrip("-*•123456789. ").strip()
            if item:
                items.append(item)
        elif cleaned:
            items.append(cleaned)
    
    return items


def build_test_generation_prompt(
    class_name: str,
    class_content: str,
    methods: List[dict],
    fields: List[dict],
    framework: str = "junit5"
) -> str:
    """
    Build a comprehensive prompt for test generation.
    
    Args:
        class_name: Name of the target class
        class_content: Source code of the target class
        methods: List of method information
        fields: List of field information
        framework: Test framework to use (default: "junit5")
    
    Returns:
        Formatted prompt string
    """
    methods_str = _format_methods_for_prompt(methods)
    fields_str = _format_fields_for_prompt(fields)
    
    if framework == "junit5":
        return f"""Generate a JUnit 5 + Spring Boot test class for the following Java class:

Class Name: {class_name}

Fields:
{fields_str}

Methods:
{methods_str}

Requirements:
1. Use JUnit 5 (Jupiter) annotations
2. Include @SpringBootTest if testing Spring components
3. Use @Mock and @InjectMocks from Mockito for dependency injection
4. Write test methods for each public method with meaningful test cases
5. Include both positive and negative test cases where applicable
6. Use AssertJ assertions for better readability
7. Add @DisplayName annotations for descriptive test names
8. Follow AAA pattern (Arrange, Act, Assert)
9. Include proper setUp/tearDown methods if needed

Generate only Java test code without any explanations or markdown formatting."""
    
    return f"""Generate a test class for {class_name} using {framework} framework:

Class Name: {class_name}

Fields:
{fields_str}

Methods:
{methods_str}

Generate only the test code without explanations."""


def _format_methods_for_prompt(methods: List[dict]) -> str:
    if not methods:
        return "No methods found"
    
    formatted = []
    for method in methods:
        modifiers = ", ".join(method.get("modifiers", []))
        return_type = method.get("return_type", "void")
        params = ", ".join([f"{p['type']} {p['name']}" for p in method.get("parameters", [])])
        formatted.append(f"  {modifiers} {return_type} {method['name']}({params})")
    
    return "\n".join(formatted)


def _format_fields_for_prompt(fields: List[dict]) -> str:
    if not fields:
        return "No fields found"
    
    formatted = []
    for field in fields:
        modifiers = ", ".join(field.get("modifiers", []))
        field_type = field.get("type", "Object")
        formatted.append(f"  {modifiers} {field_type} {field['name']}")
    
    return "\n".join(formatted)


def build_test_fix_prompt(
    test_content: str,
    errors: List[str],
    stack_traces: List[str],
    test_name: str,
    target_class: str
) -> str:
    """
    Build a prompt for fixing failing tests.
    
    Args:
        test_content: Current test code
        errors: List of error messages
        stack_traces: List of stack traces
        test_name: Name of the test class
        target_class: Name of the class being tested
    
    Returns:
        Formatted prompt string
    """
    errors_str = "\n".join([f"- {error}" for error in errors])
    stack_traces_str = "\n\n".join(stack_traces[:3])
    
    return f"""Fix the following failing test class based on the errors and stack traces:

Test Class Name: {test_name}
Target Class: {target_class}

Current Test Code:
{test_content}

Errors Encountered:
{errors_str}

Stack Traces:
{stack_traces_str}

Instructions:
1. Analyze the errors and stack traces to understand the failures
2. Fix the test code to resolve all issues
3. Ensure the fixes are minimal and focused on the actual problems
4. Maintain the existing test structure and best practices
5. Provide only the corrected Java test code without any explanations or markdown formatting"""


def build_code_review_prompt(test_name: str, test_content: str) -> str:
    """
    Build a prompt for code review.
    
    Args:
        test_name: Name of the test class
        test_content: Test code to review
    
    Returns:
        Formatted prompt string
    """
    return f"""Review the following test class:

Test Class Name: {test_name}

Test Code:
{test_content}

Review the test code for:
1. Code quality and readability
2. Proper use of JUnit 5 and Spring Boot annotations
3. Test coverage and completeness
4. Mock usage and dependency injection
5. Assertion quality and accuracy
6. Naming conventions
7. Potential bugs or anti-patterns
8. Performance considerations
9. Security best practices
10. Maintainability

Provide your review as a list of specific comments. If the code follows best practices and has no issues, return an empty list.
Format each comment as a clear, actionable statement."""
