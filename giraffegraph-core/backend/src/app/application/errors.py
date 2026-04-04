class ApplicationError(Exception):
    """Base application error."""


class NotFoundError(ApplicationError):
    """Raised when a requested entity cannot be found."""


class ConflictError(ApplicationError):
    """Raised when an operation conflicts with current state."""


class RuleViolationError(ApplicationError):
    """Raised when domain or workflow rules are violated."""


class ExternalServiceError(ApplicationError):
    """Raised when an external dependency fails."""
