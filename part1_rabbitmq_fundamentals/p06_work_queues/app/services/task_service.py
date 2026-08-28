from datetime import datetime, timezone
from uuid import uuid4

from app.core.logger import logger
from app.core.config import settings
from app.producer.producer import Producer



class TaskPublishError(Exception):
    """Raised when a task cannot be published to RabbitMQ."""




class TaskService:

    def __init__(self, producer: Producer | None = None) -> None:
        self._producer = producer or Producer(queue_name=settings.work_queue_name)


    def enqueue_task(self, task_name:str, duration_seconds: int) -> dict[str, str | int]:
        normalized_task_name = task_name.strip()

        self._validate_task(
            task_name=normalized_task_name,
            duration_seconds=duration_seconds,
        )

        task = self._create_task(
            task_name=normalized_task_name,
            duration_seconds=duration_seconds,
        )

        try:
            self._producer.publish(task)

        except Exception as e:
            logger.exception(
                'Failed to enqueue task: task_id=%s task_name=%s',
                task.get('task_id'),
                task.get('task_name'),
            )

            raise TaskPublishError(
                f"Failed to enqueue task '{task['task_id']}'."
            ) from e


        logger.info(
            'Task queued: task_id=%s task_name=%s duration_seconds=%s',
            task.get('task_id'),
            task.get('task_name'),
            task.get('duration_seconds'),
        )

        return task



    @staticmethod
    def _create_task(task_name: str, duration_seconds: int) -> dict[str, str | int]:

        payload = {
            'task_id': str(uuid4()),
            'task_name': task_name,
            'duration_seconds': duration_seconds,
            'status': 'queued',
            'created_at': datetime.now(timezone.utc).isoformat(),
        }

        return payload


    @staticmethod
    def _validate_task(task_name: str, duration_seconds: int) -> None:

        if not task_name:
            raise ValueError('Task name cannot be empty.')

        if len(task_name) > 100:
            raise ValueError(
                'Task name cannot contain more than 100 characters.'
            )

        if not 1 <= duration_seconds <= 30:
            raise ValueError(
                'Task duration must be between 1 and 30 seconds.'
            )

