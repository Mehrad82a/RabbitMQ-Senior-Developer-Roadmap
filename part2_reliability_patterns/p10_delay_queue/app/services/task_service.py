from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import Settings, settings
from app.core.logger import get_logger
from app.producer.producer import Producer, ProducerPublishError
from app.services.exceptions import TaskPublishError


logger = get_logger(__name__)


class TaskService:
    """
    Build a task and give it to the Producer for immediate or delayed delivery.
    """

    def __init__(
            self,
            *,
            producer: Producer | None = None,
            config: Settings | None = None,
    ) -> None:

        self._settings = config if config is not None else settings
        self._producer = producer if producer is not None else Producer(config=self._settings)


    def send_task(
            self,
            *,
            task_name: str,
            delay_seconds: int = 0,
    ) -> dict[str, object]:
        task = self._build_task(task_name=task_name)
        validated_delay = self._validate_delay_seconds(delay_seconds)

        try:
            self._producer.publish(
                task=task,
                delay_seconds=validated_delay,
            )

        except ProducerPublishError as exc:
            raise TaskPublishError(
                'The task could not be published.'
            ) from exc

        queue_name = (
            self._settings.task_queue
            if validated_delay == 0
            else self._settings.delay_queue
        )
        status = 'queued' if validated_delay == 0 else 'scheduled'

        logger.info(
            '[TaskService] Task accepted: '
            f'task_id=<{task["task_id"]}> | '
            f'queue=<{queue_name}> | '
            f'delay_seconds=<{validated_delay}> | '
            f'status=<{status}>'
        )

        return {
            **task,
            'delay_seconds': validated_delay,
            'queue_name': queue_name,
            'status': status,
        }


    def _validate_delay_seconds(self, delay_seconds: int) -> int:
        if isinstance(delay_seconds, bool) or not isinstance(delay_seconds, int):
            raise ValueError('Delay seconds must be an integer.')

        if delay_seconds < 0:
            raise ValueError('Delay seconds cannot be negative.')

        max_delay = self._settings.max_delay_seconds
        if delay_seconds > max_delay:
            raise ValueError(
                f'Delay seconds cannot exceed {max_delay} seconds.'
            )

        return delay_seconds


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


