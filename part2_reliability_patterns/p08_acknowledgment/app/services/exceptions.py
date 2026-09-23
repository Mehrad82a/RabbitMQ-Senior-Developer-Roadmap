class InvalidTaskError(Exception):
    """
    Raised when task data violates a business rule or is incomplete.
    """


class TransientProcessingError(Exception):
    """
    Raised when a task fails temporarily.
    """



class PermanentProcessingError(Exception):
    """
    Raised when a task can never be processed successfully.
    """



class TaskPublishError(Exception):
    """
    Raised when a task cannot be handed over to RabbitMQ.
    """