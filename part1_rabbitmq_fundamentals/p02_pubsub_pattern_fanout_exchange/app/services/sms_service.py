import time
from app.core.logger import logger


def process_sms_event(event: dict) -> dict:
    logger.info(f'[SMS Worker] received event: {event}')

    time.sleep(3)  # For task simulation

    result = {
        'event_id': event.get('event_id'),
        'worker': 'sms',
        'status': 'Completed',
        'event_payload': event,
    }

    logger.info(f'[SMS Worker] Event processed successfully: {result}')
    return result


