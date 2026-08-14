import time
from typing import Any


from app.core.logger import logger
from app.services.handlers.base_handler import BaseHandler



class FinanceHandler(BaseHandler):

    @property
    def handler_name(self) -> str:
        return 'Finance Handler'


    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Process a regular finance event
        """
        logger.info(f"[{self.handler_name}] Processing finance event: <id: {data.get('event_id')}")

        # Simulate processing
        time.sleep(3)

        result = {
            'event_id': data.get('event_id'),
            'handler': self.handler_name,
            'status': 'processed',
            'payload': data
        }

        logger.info(f'[{self.handler_name}] Event processed successfully')

        return result





