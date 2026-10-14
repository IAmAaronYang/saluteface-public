class SalutefaceError(Exception):
    """Base error for research pipeline failures."""

class InvalidSequence(SalutefaceError, ValueError):
    """Raised when a sequence is malformed or out of bounds."""

class InvalidDataset(SalutefaceError, ValueError):
    """Raised when a dataset does not satisfy the declared contract."""
