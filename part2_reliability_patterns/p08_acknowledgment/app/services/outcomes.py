from enum import Enum



class ProcessingOutcome(str, Enum):
    """
    Declares how the handler should behave for a task.
    """

    SUCCESS = 'success'
    TRANSIENT_FAILURE = 'transient_failure'
    PERMANENT_FAILURE = 'permanent_failure'





