import time
from typing import Any

from app.core.logger import logger
from app.services.handlers.base_handler import BaseHandler



class CreatedHandler(BaseHandler):

    @property
    def worker_name(self) -> str:
        return 'Created Worker'


    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Process an Error event
        """
        logger.info(f"[{self.worker_name}] Processing event: {data.get('message')}")

        # Simulate processing
        time.sleep(3)

        result = {
            'event_id': data.get('event_id'),
            'routing_key': data.get('routing_key'),
            'worker': self.worker_name,
            'status': 'processed',
            'payload': data
        }

        logger.info(f'[{self.worker_name}] Event processed successfully')

        return result
