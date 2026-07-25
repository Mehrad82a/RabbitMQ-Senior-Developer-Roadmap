import time, uuid
from app.core.logger import logger
from app.producer.producer import publish


class MessageService:

    @staticmethod
    def send_message(level: str, message:str) -> dict:
        message_id = str(uuid.uuid4())
        message_payload = {
            'message_id': message_id,
            'level': level,
            'message': message,
            'created_at': time.time(),
        }

        published = publish(level=level, message=message)

        if not published:
            raise RuntimeError('Failed to send message')

        logger.info(f'Message sent successfully: {message_payload}')


