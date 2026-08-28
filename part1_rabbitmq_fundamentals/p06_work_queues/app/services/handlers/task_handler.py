import time
from collections.abc import Mapping
from typing import Any

from app.core.logger import logger
from app.services.handlers.base_handler import BaseHandler




class TaskHandler(BaseHandler):

    def __init__(self, handler_name: str) -> None:
        if not handler_name.strip():
            raise ValueError('Handler name cannot be empty')

        self._handler_name = handler_name.strip()


    def process(self, task: Mapping[str, object]) -> dict[str, object]:
        task_id = self._get_task_id(task)
        task_name = self._get_task_name(task)
        duration_seconds = self._get_duration_seconds(task)

        logger.info(f"[{self._handler_name}] Processing task:<{task.get('task_id')}>")

        # Simulate processing
        time.sleep(duration_seconds)

        result = {
            'task_id': task_id,
            'task_name': task_name,
            'handler': self._handler_name,
            'status': 'processed',
            'payload': task
        }

        logger.info(f"[{self._handler_name}] Finished Processing task:<{task.get('task_id')}>")


        return result




    @staticmethod
    def _get_task_id(
            task: Mapping[str, object],
    ) -> str:
        task_id = task.get('task_id')

        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError('Task must contain a valid task_id')

        return task_id


    @staticmethod
    def _get_task_name(
            task: Mapping[str, object],
    ) -> str:
        task_name = task.get('task_name')

        if not isinstance(task_name, str) or not task_name.strip():
            raise ValueError('Task must contain a valid task_name')

        return task_name


    @staticmethod
    def _get_duration_seconds(task: Mapping[str, object]) -> int:
        duration_seconds = task.get('duration_seconds')

        if (
                not isinstance(duration_seconds, int)
                or isinstance(duration_seconds, bool)
                or not 1 <= duration_seconds <= 30
        ):
            raise ValueError(
                'Task duration_seconds must be an integer between 1 and 30'
            )

        return duration_seconds


