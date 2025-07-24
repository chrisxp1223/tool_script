"""Custom exception classes for PostCodeMon."""

from typing import Optional


class PostCodeMonError(Exception):
    """Base exception class for all PostCodeMon errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.error_code = error_code
        self.message = message


class ToolExecutionError(PostCodeMonError):
    """Raised when the wrapped Windows tool fails to execute properly."""
    
    def __init__(self, message: str, return_code: int, stderr: str = "", error_code: Optional[str] = None):
        super().__init__(message, error_code)
        self.return_code = return_code
        self.stderr = stderr


class ConfigurationError(PostCodeMonError):
    """Raised when there are configuration-related issues."""
    
    def __init__(self, message: str, config_path: Optional[str] = None, error_code: Optional[str] = None):
        super().__init__(message, error_code)
        self.config_path = config_path


class ToolNotFoundError(PostCodeMonError):
    """Raised when the target Windows tool cannot be located."""
    
    def __init__(self, tool_path: str, search_paths: Optional[list] = None):
        message = f"Tool not found: {tool_path}"
        if search_paths:
            message += f". Searched in: {', '.join(search_paths)}"
        super().__init__(message, "TOOL_NOT_FOUND")
        self.tool_path = tool_path
        self.search_paths = search_paths or []


class ValidationError(PostCodeMonError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[str] = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value


class TimeoutError(PostCodeMonError):
    """Raised when tool execution exceeds timeout limits."""
    
    def __init__(self, timeout_seconds: int, message: Optional[str] = None):
        if not message:
            message = f"Tool execution timed out after {timeout_seconds} seconds"
        super().__init__(message, "EXECUTION_TIMEOUT")
        self.timeout_seconds = timeout_seconds