class EmployeeNotFoundError(Exception):
    """Raised when an employee cannot be found."""

class InvalidSalaryError(Exception):
    """Raised when an employee has an invalid salary."""

class ComplianceViolationError(Exception):
    """Raised when data fails compliance validation."""
