import uuid
from datetime import datetime

from app.core.logger import logger
from app.producer.producer import publish


class EventService:

    @staticmethod
    def send_event(event: dict):
        event_id = str(uuid.uuid4())

        event_payload = {
            'event_id': event_id,
            'routing_key': event.get('routing_key'),
            'message': event.get('message'),
            'created_at': datetime.utcnow().isoformat(),

        }

        published = publish(event_payload)

        if not published:
            raise RuntimeError('Failed to send event')

        logger.info(f'Event sent successfully: {event_payload}')



