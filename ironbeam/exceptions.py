"""
IronBeam SDK Exceptions

Custom exception classes for the IronBeam Python SDK.
"""

class APIError(Exception):
    """Base exception class for IronBeam API errors."""
    
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
    
    def __str__(self):
        if self.status_code:
            return f"APIError (HTTP {self.status_code}): {self.message}"
        return f"APIError: {self.message}"


class AuthenticationError(APIError):
    """Raised when authentication fails (401 Unauthorized)."""
    
    def __init__(self, message: str = "Authentication failed", status_code: int = 401, response_text: str = None):
        super().__init__(message, status_code, response_text)


class InvalidRequestError(APIError):
    """Raised when the request is invalid (400 Bad Request)."""
    
    def __init__(self, message: str = "Invalid request", status_code: int = 400, response_text: str = None):
        super().__init__(message, status_code, response_text)


class RateLimitError(APIError):
    """Raised when rate limit is exceeded (429 Too Many Requests)."""
    
    def __init__(self, message: str = "Rate limit exceeded", status_code: int = 429, response_text: str = None):
        super().__init__(message, status_code, response_text)


class ServerError(APIError):
    """Raised when the server returns a 5xx error."""
    
    def __init__(self, message: str = "Server error", status_code: int = 500, response_text: str = None):
        super().__init__(message, status_code, response_text)


class ConnectionError(APIError):
    """Raised when connection to the API fails."""
    
    def __init__(self, message: str = "Connection failed"):
        super().__init__(message)


class TimeoutError(APIError):
    """Raised when a request times out."""
    
    def __init__(self, message: str = "Request timed out"):
        super().__init__(message)


class StreamingError(APIError):
    """Raised when streaming operations fail."""
    
    def __init__(self, message: str = "Streaming error"):
        super().__init__(message)


class OrderError(APIError):
    """Raised when order operations fail."""
    
    def __init__(self, message: str = "Order operation failed"):
        super().__init__(message)


class PositionError(APIError):
    """Raised when position operations fail."""
    
    def __init__(self, message: str = "Position operation failed"):
        super().__init__(message)