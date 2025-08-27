class APIError(Exception):
    """Base class for API errors."""
    pass

class AuthenticationError(APIError):
    """Raised for authentication errors."""
    pass

class InvalidRequestError(APIError):
    """Raised for invalid requests."""
    pass
