class ConflictError(Exception):
    """Raised when a request conflicts with existing data (maps to HTTP 409)."""