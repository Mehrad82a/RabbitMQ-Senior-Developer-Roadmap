from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import Settings, settings
from app.core.logger import get_logger
from app.producer.producer import Producer, ProducerPublishError
from app.services.exceptions import TaskPublishError


logger = get_logger(__name__)



class TaskService:
    """
    Build a task and give it to the Producer.
    """

    def __init__(
            self,
            *,
            producer: Producer | None = None,
            config: Settings | None = None,
    ) -> None:

        self._settings = config if config is not None else settings
        self._producer = producer if producer is not None else Producer(config=self._settings)



    def send_task(self, *, task_name: str) -> dict[str, str]:
        task = self._build_task(task_name=task_name)

        try:
            self._producer.publish(task=task)

        except ProducerPublishError as exc:
            raise TaskPublishError(
                'The task could not be published.'
            ) from exc

        logger.info(
            '[TaskService] Task queued: '
            f'task_id=<{task["task_id"]}> | '
            f'queue=<{self._settings.task_queue}>'
        )


        return {
            **task,
            'queue_name': self._settings.task_queue,
            'status': 'queued',
        }



    @staticmethod
    def _build_task(*, task_name: str) -> dict[str, str]:
        cleaned_name = task_name.strip()

        if not cleaned_name:
            raise ValueError('Task name cannot be empty')


        return {
            'task_id': str(uuid4()),
            'task_name': cleaned_name,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }


