from datetime import datetime, timezone
from uuid import uuid4


from app.core.config import settings
from app.core.logger import logger
from app.producer.producer import Producer, ProducerPublishError
from app.services.exceptions import TaskPublishError
from app.services.outcomes import ProcessingOutcome






class TaskService:
    """
    Builds task payloads and hands them to the producer
    """

    ACK_MODES: dict[str, str] = {
        'auto': 'auto_ack_queue',
        'manual': 'manual_ack_queue',
    }

    def __init__(self, producer: Producer | None = None) -> None:
        self._producer = producer or Producer()


    def send_task(self, *, mode: str, task_name: str, processing_outcome: ProcessingOutcome) -> dict[str, object]:
        queue_name = self._resolve_queue_name(mode)

        task = self._build_task(
            task_name=task_name,
            processing_outcome=processing_outcome
        )

        try:
            self._producer.publish(
                task=task,
                queue_name=queue_name,
            )

        except ProducerPublishError as exc:
            raise TaskPublishError('The task could not be published') from exc

        logger.info(
            f"Task sent: task_id=<{task['task_id']}> | "
            f"mode=<{mode}> | "
            f"queue=<{queue_name}>"
        )

        return {
            **task,
            'mode': mode,
            'queue_name': queue_name,
            'status': 'queued',
        }




    @classmethod
    def _resolve_queue_name(cls, mode: str) -> str:
        settings_field = cls.ACK_MODES.get(mode)

        if settings_field is None:
            raise ValueError(f'Unsupported acknowledgment mode: <{mode}>')

        return getattr(settings, settings_field)




    @staticmethod
    def _build_task(*, task_name: str, processing_outcome: ProcessingOutcome) -> dict[str, object]:
        cleaned_task_name = task_name.strip()

        if not cleaned_task_name:
            raise ValueError('Task name cannot be empty')

        return {
            'task_id':  str(uuid4()),
            'task_name': cleaned_task_name,
            'processing_outcome': ProcessingOutcome(processing_outcome).value,
            'created_at': datetime.now(timezone.utc).isoformat(),
        }




