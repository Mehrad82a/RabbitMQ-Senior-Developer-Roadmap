from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import settings
from app.producer.producer import Producer, ProducerPublishError


class PersistencePublishError(Exception):
    """Raised when a persistence experiment message cannot be published."""


class PersistenceService:
    def __init__(self, producer: Producer | None = None) -> None:
        self._producer = producer or Producer()

    def enqueue_message(
        self,
        content: str, *, queue_durable: bool, message_persistent: bool, publisher_confirm: bool) -> dict[str, object]:

        message_id = uuid4()
        created_at = datetime.now(timezone.utc).isoformat()

        queue_name = self._resolve_queue_name(
            queue_durable=queue_durable,
            message_persistent=message_persistent,
        )

        message = {
            'message_id': str(message_id),
            'content': content,
            'queue_name': queue_name,
            'queue_durable': queue_durable,
            'message_persistent': message_persistent,
            'publisher_confirm': publisher_confirm,
            'created_at': created_at,
        }

        try:
            broker_confirmed = self._producer.publish(
                message=message,
                queue_name=queue_name,
                queue_durable=queue_durable,
                message_persistent=message_persistent,
                publisher_confirm=publisher_confirm,
            )

        except ProducerPublishError as exc:
            raise PersistencePublishError(
                'The persistence experiment message could not be published.'
            ) from exc

        return {
            'message_id': message_id,
            'content': content,
            'queue_name': queue_name,
            'queue_durable': queue_durable,
            'message_persistent': message_persistent,
            'publisher_confirm': publisher_confirm,
            'broker_confirmed': broker_confirmed,
            'status': 'published',
            'created_at': created_at,
        }

    @staticmethod
    def _resolve_queue_name(*, queue_durable: bool, message_persistent: bool) -> str:
        queue_names = {
            (False, False): settings.non_durable_transient_queue,
            (False, True): settings.non_durable_persistent_queue,
            (True, False): settings.durable_transient_queue,
            (True, True): settings.durable_persistent_queue,
        }

        return queue_names[(queue_durable, message_persistent)]