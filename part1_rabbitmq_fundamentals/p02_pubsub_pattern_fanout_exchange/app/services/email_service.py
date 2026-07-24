import time
from app.core.logger import logger


def process_email_event(event: dict) -> dict:
    logger.info(f'[Email Worker] received event: {event}')

    time.sleep(3)  # For task simulation

    result = {
        'event_id': event.get('event_id'),
        'worker': 'email',
        'status': 'Completed',
        'event_payload': event,
    }

    logger.info(f'[Email Worker] Event processed successfully: {result}')
    return result


