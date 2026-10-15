import time
from collections.abc import Mapping

from app.services.exceptions import InvalidTaskError



class DefaultTaskProcessor:
    """Validate and process a task."""

    def __init__(self, *, processing_seconds: float = 3.0) -> None:
        if processing_seconds < 0:
            raise ValueError('Processing seconds cannot be negative.')

        self._processing_seconds = processing_seconds


    def execute(self, task: Mapping[str, object]) -> dict[str, object]:
        task_id = self._get_required_string(task, field_name='task_id')
        task_name = self._get_required_string(task, field_name='task_name')

        if self._processing_seconds > 0:
            time.sleep(self._processing_seconds)

        return {
            'task_id': task_id,
            'task_name': task_name,
            'processor': self.__class__.__name__,
            'status': 'processed',
        }



    @staticmethod
    def _get_required_string(
            task: Mapping[str, object],
            *,
            field_name: str
    ) -> str:
        value = task.get(field_name)

        if not isinstance(value, str) or not value.strip():
            raise InvalidTaskError(f'Task must contain a valid {field_name}.')

        return value.strip()



