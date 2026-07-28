import time
from typing import Any


from app.core.logger import logger
from app.services.handlers.base_handler import BaseHandler



class InfoHandler(BaseHandler):

    @property
    def worker_name(self) -> str:
        return 'Info Worker'


    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Process an INFO log message.
        """

        logger.info(f"[{self.worker_name}] Processing message: {data.get('message')}")

        # Simulate processing
        time.sleep(3)

        result = {
            'message_id': data.get('message_id'),
            'level': 'info',
            'worker': self.worker_name,
            'status': 'processed',
            'payload': data,
        }

        logger.info(f'[{self.worker_name}] Message processed successfully')

        return result






