from collections.abc import Mapping
from app.services.exceptions import InvalidTaskError




class SuccessfulTaskProcessor:
    """A processor fake that always finishes successfully."""

    def execute(self, task: Mapping[str, object]) -> dict[str, object]:
        return {
            'task_id': task['task_id'],
            'task_name': task['task_name'],
            'processor': self.__class__.__name__,
            'status': 'processed',
        }



class TemporaryFailingTaskProcessor:
    """A processor fake that simulates a temporary external failure."""

    def execute(self, task: Mapping[str, object]) -> dict[str, object]:
        raise TimeoutError('The external service timed out.')




class PermanentlyFailingTaskProcessor:
    """A processor fake that simulates an unrecoverable business failure."""

    def execute(self, task: Mapping[str, object]) -> dict[str, object]:
        raise InvalidTaskError('The task cannot be processed.')