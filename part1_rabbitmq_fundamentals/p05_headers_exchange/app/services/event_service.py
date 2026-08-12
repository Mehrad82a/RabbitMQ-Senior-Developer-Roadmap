import uuid
from datetime import datetime

from app.core.logger import logger
from app.producer.producer import publish



class EventService:


    @staticmethod
    def send_event(event: dict):

        try:
            event_id = str(uuid.uuid4())

            event_payload = {
                'event_id': event_id,
                'event_data': event,
                'created_at': datetime.utcnow().isoformat(),
            }
            print('stage 2')
            publish(event_payload)
            logger.info(f'Event sent successfully: {event_payload}')



        except Exception as e:
            raise RuntimeError(f'Failed to send event. Error: {e}')




