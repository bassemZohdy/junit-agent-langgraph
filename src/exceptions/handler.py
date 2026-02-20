from typing import Optional, List


class AgentError(Exception):
    """Base exception for all agent-related errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(AgentError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message, details)
        self.field = field


class LLMError(AgentError):
    """Raised when LLM interaction fails."""
    
    def __init__(self, message: str, retry_count: int = 0, details: Optional[dict] = None):
        super().__init__(message, details)
        self.retry_count = retry_count


class ToolError(AgentError):
    """Base exception for tool-related errors."""
    pass


class FileOperationError(ToolError):
    """Raised when file operations fail."""
    
    def __init__(self, message: str, file_path: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message, details)
        self.file_path = file_path


class MavenError(ToolError):
    """Raised when Maven operations fail."""
    
    def __init__(self, message: str, return_code: Optional[int] = None, details: Optional[dict] = None):
        super().__init__(message, details)
        self.return_code = return_code


class TestError(AgentError):
    """Raised when test operations fail."""
    
    def __init__(
        self,
        message: str,
        test_class: Optional[str] = None,
        errors: Optional[List[str]] = None,
        details: Optional[dict] = None
    ):
        super().__init__(message, details)
        self.test_class = test_class
        self.errors = errors or []


class CompilationError(ToolError):
    """Raised when compilation fails."""
    
    def __init__(
        self,
        message: str,
        compilation_errors: Optional[List[str]] = None,
        details: Optional[dict] = None
    ):
        super().__init__(message, details)
        self.compilation_errors = compilation_errors or []


class ParsingError(AgentError):
    """Raised when parsing Java files fails."""
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        details: Optional[dict] = None
    ):
        super().__init__(message, details)
        self.file_path = file_path


class RetryExhaustedError(AgentError):
    """Raised when max retries are exceeded."""
    
    def __init__(self, message: str, retry_count: int, max_retries: int, details: Optional[dict] = None):
        super().__init__(message, details)
        self.retry_count = retry_count
        self.max_retries = max_retries


def create_error_response(
    error: Exception,
    status: str = "error",
    include_traceback: bool = False
) -> dict:
    """
    Create a standardized error response dictionary.
    
    Args:
        error: The exception that occurred
        status: The status value to set (default: "error")
        include_traceback: Whether to include full traceback (default: False)
    
    Returns:
        Dictionary with error information
    """
    response = {
        "status": status,
        "errors": [str(error)],
        "success": False
    }
    
    if hasattr(error, 'details') and error.details:
        response["error_details"] = error.details
    
    if hasattr(error, 'retry_count'):
        response["retry_count"] = error.retry_count
    
    if hasattr(error, 'file_path'):
        response["file_path"] = error.file_path
    
    if hasattr(error, 'test_class'):
        response["test_class"] = error.test_class
    
    return response


def format_error_message(error: Exception, context: Optional[str] = None) -> str:
    """
    Format an error message with optional context.
    
    Args:
        error: The exception that occurred
        context: Optional context information
    
    Returns:
        Formatted error message
    """
    message = str(error)
    
    if context:
        message = f"{context}: {message}"
    
    if isinstance(error, AgentError) and error.details:
        details_str = ", ".join([f"{k}={v}" for k, v in error.details.items()])
        if details_str:
            message = f"{message} ({details_str})"
    
    return message
