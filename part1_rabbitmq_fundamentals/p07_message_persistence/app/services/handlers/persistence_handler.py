from collections.abc import Mapping
from app.core.logger import logger




class PersistenceHandlingError(Exception):
    """Raised when a persistence message cannot be processed."""



class PersistenceHandler:
    def __init__(self, handler_name: str) -> None:
        if not handler_name.strip():
            raise ValueError('Handler name cannot be empty.')

        self._handler_name = handler_name.strip()

    def process(self, message:Mapping[str, object]) -> dict[str, object]:
        message_id = self._get_required_string(message, field_name='message_id')
        content = self._get_required_string(message, field_name='content')
        queue_name = self._get_required_string(message, field_name='queue_name')
        queue_durable = self._get_required_boolean(message, field_name='queue_durable')
        message_persistent = self._get_required_boolean(message, field_name='message_persistent')
        publisher_confirm = self._get_required_boolean(message, field_name='publisher_confirm')


        logger.info(f'[{self._handler_name}] Processing message:<{message_id}>')


        result = {
            'message_id': message_id,
            'content': content,
            'queue_name': queue_name,
            'queue_durable': queue_durable,
            'message_persistent': message_persistent,
            'publisher_confirm': publisher_confirm,
            'handler': self._handler_name,
            'status': 'processed',
        }

        logger.info(f'[{self._handler_name}] Finished processing message:<{message_id}>')

        return result



    @staticmethod
    def _get_required_string(
        message: Mapping[str, object], *, field_name: str) -> str:
        value = message.get(field_name)

        if not isinstance(value, str) or not value.strip():
            raise PersistenceHandlingError(
                f'Message must contain a valid {field_name}.'
            )

        return value.strip()



    @staticmethod
    def _get_required_boolean(message: Mapping[str, object], *, field_name: str) -> bool:
        value = message.get(field_name)

        if not isinstance(value, bool):
            raise PersistenceHandlingError(
                f'Message must contain a boolean {field_name}.'
            )

        return value






