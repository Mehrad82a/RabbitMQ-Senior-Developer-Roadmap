import time
from typing import Any

from app.core.logger import logger
from app.services.handlers.base_handler import BaseHandler


class WarningHandler(BaseHandler):

    @property
    def handler_name(self) -> str:
        return 'Warning Handler'

    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Process a Warning log message.
        """

        logger.info(f"[{self.handler_name}] Processing message: {data.get('message')}")

        # Simulate processing
        time.sleep(3)

        result = {
            'message_id': data.get('message_id'),
            'level': 'warning',
            'worker': self.handler_name,
            'status': 'processed',
            'payload': data,
        }

        logger.info(f'[{self.handler_name}] Message processed successfully')

        return result






