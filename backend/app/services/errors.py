"""Domain-level service errors."""


class MotherboardAnalysisError(RuntimeError):
    """Raised when image analysis cannot produce a valid result."""

