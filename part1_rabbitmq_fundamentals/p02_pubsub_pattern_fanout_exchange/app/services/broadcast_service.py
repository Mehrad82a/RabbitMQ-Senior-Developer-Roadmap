import time, uuid
from app.core.logger import logger
from app.producer.producer import publish_event


class BroadcastService:


    @staticmethod
    def broadcast_message(event_data: dict) -> dict:
        event_id = str(uuid.uuid4())
        event_payload = {
            'event_id': event_id,
            'payload': event_data,
            'created_at': time.time(),
            'status': 'broadcasted'
        }

        published = publish_event(event_payload)

        if not published:
            raise RuntimeError('Failed to broadcast event')

        logger.info(f'Event broadcast successfully: {event_payload}')



