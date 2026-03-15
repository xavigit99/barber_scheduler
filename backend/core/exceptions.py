class ApplicationError(Exception):
    """Base application error."""


class AuthenticationError(ApplicationError):
    """Raised when credentials are invalid or expired."""


class ConflictError(ApplicationError):
    """Raised when a write would violate a uniqueness rule."""


class NotFoundError(ApplicationError):
    """Raised when a requested resource does not exist."""


class ValidationError(ApplicationError):
    """Raised when a business validation fails."""
