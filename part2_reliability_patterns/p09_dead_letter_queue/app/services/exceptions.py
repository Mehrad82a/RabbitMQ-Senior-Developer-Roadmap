

class InvalidTaskError(Exception):
    """Raised when task data is missing or invalid."""


class TransientProcessingError(Exception):
    """Raised when processing may succeed on another attempt."""


class PermanentProcessingError(Exception):
    """Raised when retrying cannot make the task valid."""


class TaskPublishError(Exception):
    """Raised when a task cannot be handed over to RabbitMQ."""

