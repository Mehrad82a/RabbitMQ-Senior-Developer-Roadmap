from collections.abc import Mapping

from app.services.exceptions import InvalidTaskError



class SuccessfulTaskProcessor:
    """
    Simulates successful business processing.
    """

    def execute(
            self,
            task: Mapping[str, object],
    ) -> dict[str, object]:

        return {
            'task_id': task.get('task_id'),
            'task_name': task.get('task_name'),
            'processor': self.__class__.__name__,
            'status': 'processed',
        }




class TemporarilyFailingTaskProcessor:
    """
    Simulates a temporary infrastructure failure.
    """

    def execute(
            self,
            task: Mapping[str, object],
    ) -> dict[str, object]:

        task_id = task.get('task_id')

        raise TimeoutError(f'Temporary dependency failure for task <{task_id}>.')




class PermanentlyFailingTaskProcessor:
    """
    Simulates a permanent business validation failure.
    """

    def execute(
        self,
        task: Mapping[str, object],
    ) -> dict[str, object]:

        task_id = task.get('task_id', 'unknown')

        raise InvalidTaskError(f'Task <{task_id}> violates a business rule.')