class ConflictError(Exception):
    """Raised when a request conflicts with existing data (maps to HTTP 409)."""
    
class AuthenticationError(Exception):
    """Raised when credentials or a token are missing, invalid or expired (maps to HTTP 401)."""