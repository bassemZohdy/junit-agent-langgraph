import re
import os
import shlex
from pathlib import Path
from typing import Optional, List, Set, Any
from ..exceptions.handler import ValidationError


class SecurityUtils:
    """Utility functions for input sanitization and security."""
    
    DANGEROUS_PATTERNS = [
        r'\.\./.*',       # Path traversal
        r'\.\.\\.*',      # Windows path traversal
        r'/etc/passwd',   # System file access
        r'\\windows\\.*', # Windows system files
        r'<script.*?>',   # XSS attempt
        r'javascript:',   # JavaScript protocol
        r'on\w+\s*=',    # Event handlers
        r'\${.*}',        # Template injection
        r'%7B.*%7D',      # URL encoded template injection
    ]
    
    SHELL_INJECTION_PATTERNS = [
        r';\s*\w+',       # Command chaining
        r'\|\s*\w+',      # Pipes
        r'&&\s*\w+',      # AND operator
        r'\|\|\s*\w+',    # OR operator
        r'`.*`',          # Backticks
        r'\$\(.*\)',      # Command substitution
        r'>\s*[/\\]',     # Redirection to absolute path
        r'<\s*[/\\]',     # Input from absolute path
    ]
    
    SQL_INJECTION_PATTERNS = [
        r"'\s*(OR|AND)\s*",
        r'--\s*$',
        r'/\*.*\*/',
        r';\s*(DROP|DELETE|INSERT|UPDATE|EXEC)\s+',
        r'xp_cmdshell',
        r'sp_oacreate',
    ]
    
    @classmethod
    def sanitize_path(cls, path: str, allow_absolute: bool = False) -> str:
        """
        Sanitize a file path to prevent path traversal and other attacks.
        
        Args:
            path: The path to sanitize
            allow_absolute: Whether to allow absolute paths
        
        Returns:
            Sanitized path
        
        Raises:
            ValidationError: If path contains dangerous patterns
        """
        if not path or not path.strip():
            raise ValidationError("Path cannot be empty", "path")
        
        path = path.strip()
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                raise ValidationError(
                    f"Path contains potentially dangerous pattern: {pattern}",
                    "path"
                )
        
        if not allow_absolute:
            if path.startswith('/') or (len(path) > 1 and path[1:3] == ':\\'):
                raise ValidationError(
                    "Absolute paths are not allowed for security reasons",
                    "path"
                )
        
        if '..' in path:
            raise ValidationError(
                "Path traversal (..) is not allowed",
                "path"
            )
        
        try:
            path_obj = Path(path).resolve()
            return str(path_obj)
        except (OSError, ValueError) as e:
            raise ValidationError(f"Invalid path: {str(e)}", "path")
    
    @classmethod
    def sanitize_shell_command(cls, command: str, allow_args: bool = False) -> str:
        """
        Sanitize shell command to prevent injection attacks.
        
        Args:
            command: The command to sanitize
            allow_args: Whether to allow command arguments
        
        Returns:
            Sanitized command
        
        Raises:
            ValidationError: If command contains injection patterns
        """
        if not command or not command.strip():
            raise ValidationError("Command cannot be empty", "command")
        
        command = command.strip()
        
        for pattern in cls.SHELL_INJECTION_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                raise ValidationError(
                    f"Command contains potentially dangerous pattern: {pattern}",
                    "command"
                )
        
        if not allow_args:
            if len(command.split()) > 1:
                raise ValidationError(
                    "Command arguments are not allowed",
                    "command"
                )
        
        return shlex.quote(command)
    
    @classmethod
    def sanitize_shell_args(cls, args: List[str]) -> List[str]:
        """
        Sanitize shell arguments using proper quoting.
        
        Args:
            args: List of arguments to sanitize
        
        Returns:
            List of safely quoted arguments
        """
        sanitized = []
        for arg in args:
            if not isinstance(arg, str):
                raise ValidationError(f"Argument must be string, got {type(arg)}", "args")
            sanitized.append(shlex.quote(arg))
        return sanitized
    
    @classmethod
    def sanitize_sql_input(cls, input_str: str) -> str:
        """
        Sanitize SQL input to prevent injection attacks.
        
        Note: This is a basic sanitization. Always use parameterized queries.
        
        Args:
            input_str: The SQL input to sanitize
        
        Returns:
            Sanitized input
        
        Raises:
            ValidationError: If input contains SQL injection patterns
        """
        if not input_str:
            return input_str
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE):
                raise ValidationError(
                    f"Input contains SQL injection pattern: {pattern}",
                    "sql_input"
                )
        
        return input_str.replace("'", "''").replace("\\", "\\\\")
    
    @classmethod
    def sanitize_html_input(cls, input_str: str, allowed_tags: Optional[Set[str]] = None) -> str:
        """
        Sanitize HTML input to prevent XSS attacks.
        
        Args:
            input_str: The HTML input to sanitize
            allowed_tags: Set of allowed HTML tags (default: empty, removes all tags)
        
        Returns:
            Sanitized HTML
        """
        if not input_str:
            return input_str
        
        if allowed_tags is None:
            allowed_tags = set()
        
        def escape_html(text: str) -> str:
            return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
        
        def sanitize_tag(match):
            tag = match.group(1)
            if tag.lower() in allowed_tags:
                return f"<{tag}>"
            return ""
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, input_str, re.IGNORECASE):
                raise ValidationError(
                    f"Input contains potentially dangerous pattern: {pattern}",
                    "html_input"
                )
        
        result = re.sub(r'<\s*\/?\s*(\w+)[^>]*>', sanitize_tag, input_str)
        return result
    
    @classmethod
    def sanitize_filename(cls, filename: str, max_length: int = 255) -> str:
        """
        Sanitize a filename to prevent directory traversal and other issues.
        
        Args:
            filename: The filename to sanitize
            max_length: Maximum length for filename
        
        Returns:
            Sanitized filename
        
        Raises:
            ValidationError: If filename is invalid
        """
        if not filename or not filename.strip():
            raise ValidationError("Filename cannot be empty", "filename")
        
        filename = filename.strip()
        
        if len(filename) > max_length:
            raise ValidationError(
                f"Filename exceeds maximum length of {max_length}",
                "filename"
            )
        
        for char in '<>:"|?*\\/':
            if char in filename:
                raise ValidationError(
                    f"Filename contains invalid character: {char}",
                    "filename"
                )
        
        reserved_names = {
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        }
        
        name_without_ext = Path(filename).stem.upper()
        if name_without_ext in reserved_names:
            raise ValidationError(
                f"Filename '{filename}' is a reserved system name",
                "filename"
            )
        
        return filename
    
    @classmethod
    def validate_allowed_extensions(cls, filename: str, allowed_extensions: Set[str]) -> None:
        """
        Validate that a filename has an allowed extension.
        
        Args:
            filename: The filename to validate
            allowed_extensions: Set of allowed extensions (e.g., {'.java', '.xml'})
        
        Raises:
            ValidationError: If extension is not allowed
        """
        if not allowed_extensions:
            return
        
        path = Path(filename)
        extension = path.suffix.lower()
        
        if extension not in {ext.lower() for ext in allowed_extensions}:
            raise ValidationError(
                f"File extension '{extension}' is not allowed. "
                f"Allowed extensions: {', '.join(allowed_extensions)}",
                "filename"
            )
    
    @classmethod
    def sanitize_package_name(cls, package_name: str) -> str:
        """
        Sanitize and validate a Java package name.
        
        Args:
            package_name: The package name to sanitize
        
        Returns:
            Sanitized package name
        
        Raises:
            ValidationError: If package name is invalid
        """
        if not package_name or not package_name.strip():
            raise ValidationError("Package name cannot be empty", "package_name")
        
        package_name = package_name.strip().lower()
        
        pattern = r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$'
        if not re.match(pattern, package_name):
            raise ValidationError(
                f"Invalid package name '{package_name}'. "
                "Package names must follow reverse domain notation (e.g., com.example.package)",
                "package_name"
            )
        
        return package_name
    
    @classmethod
    def sanitize_class_name(cls, class_name: str) -> str:
        """
        Sanitize and validate a Java class name.
        
        Args:
            class_name: The class name to sanitize
        
        Returns:
            Sanitized class name
        
        Raises:
            ValidationError: If class name is invalid
        """
        if not class_name or not class_name.strip():
            raise ValidationError("Class name cannot be empty", "class_name")
        
        class_name = class_name.strip()
        
        pattern = r'^[A-Z][a-zA-Z0-9_]*$'
        if not re.match(pattern, class_name):
            raise ValidationError(
                f"Invalid class name '{class_name}'. "
                "Class names must start with uppercase letter and contain only alphanumeric characters and underscores",
                "class_name"
            )
        
        return class_name
    
    @classmethod
    def sanitize_method_name(cls, method_name: str) -> str:
        """
        Sanitize and validate a Java method name.
        
        Args:
            method_name: The method name to sanitize
        
        Returns:
            Sanitized method name
        
        Raises:
            ValidationError: If method name is invalid
        """
        if not method_name or not method_name.strip():
            raise ValidationError("Method name cannot be empty", "method_name")
        
        method_name = method_name.strip()
        
        pattern = r'^[a-z][a-zA-Z0-9_]*$'
        if not re.match(pattern, method_name):
            raise ValidationError(
                f"Invalid method name '{method_name}'. "
                "Method names must start with lowercase letter and contain only alphanumeric characters and underscores",
                "method_name"
            )
        
        return method_name
    
    @classmethod
    def sanitize_field_name(cls, field_name: str) -> str:
        """
        Sanitize and validate a Java field name.
        
        Args:
            field_name: The field name to sanitize
        
        Returns:
            Sanitized field name
        
        Raises:
            ValidationError: If field name is invalid
        """
        if not field_name or not field_name.strip():
            raise ValidationError("Field name cannot be empty", "field_name")
        
        field_name = field_name.strip()
        
        pattern = r'^[a-z][a-zA-Z0-9_]*$'
        if not re.match(pattern, field_name):
            raise ValidationError(
                f"Invalid field name '{field_name}'. "
                "Field names must start with lowercase letter and contain only alphanumeric characters and underscores",
                "field_name"
            )
        
        return field_name
    
    @classmethod
    def check_for_secrets(cls, input_str: str) -> List[str]:
        """
        Check input for potential secrets/passwords/API keys.
        
        Args:
            input_str: The input string to check
        
        Returns:
            List of potential secret patterns found
        """
        secret_patterns = [
            r'password\s*[:=]\s*["\']?[\w]+["\']?',
            r'api[_-]?key\s*[:=]\s*["\']?[\w-]+["\']?',
            r'secret[_-]?key\s*[:=]\s*["\']?[\w-]+["\']?',
            r'access[_-]?token\s*[:=]\s*["\']?[\w.-]+["\']?',
            r'private[_-]?key\s*[:=]\s*["\']?[\w.-]+["\']?',
            r'authorization[:\s]+Bearer\s+[\w.-]+',
            r'AKIA[0-9A-Z]{16}',
            r'github_pat_[0-9a-zA-Z_]{82}',
            r'sk-[0-9a-zA-Z]{48}',
        ]
        
        found = []
        for pattern in secret_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                found.append(pattern)
        
        return found
    
    @classmethod
    def validate_project_path(cls, project_path: str, allow_create: bool = False) -> Path:
        """
        Validate a project path for security.
        
        Args:
            project_path: The project path to validate
            allow_create: Whether to allow non-existent paths (for new projects)
        
        Returns:
            Resolved Path object
        
        Raises:
            ValidationError: If path is invalid
        """
        sanitized = cls.sanitize_path(project_path, allow_absolute=True)
        path = Path(sanitized).resolve()
        
        if not allow_create and not path.exists():
            raise ValidationError(
                f"Project path does not exist: {project_path}",
                "project_path"
            )
        
        if path.exists() and not path.is_dir():
            raise ValidationError(
                f"Project path is not a directory: {project_path}",
                "project_path"
            )
        
        return path
