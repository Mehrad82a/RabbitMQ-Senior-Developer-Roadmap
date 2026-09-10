import time
from collections.abc import Mapping

from app.core.logger import logger
from app.services.exceptions import TransientProcessingError, PermanentProcessingError
from app.services.outcomes import ProcessingOutcome






class TaskHandler:
    """
    Simulates the business logic a consumer runs before acknowledging.

    Failure taxonomy exposed to consumers:
        SUCCESS            -> returns a result dict
        TRANSIENT_FAILURE  -> TransientProcessingError (retryable)
        PERMANENT_FAILURE  -> PermanentProcessingError (not retryable)
        invalid payload    -> PermanentProcessingError (poison message)
    """

    def __init__(self, handler_name: str = 'TaskHandler', processing_seconds: float = 1.0) -> None:
        if not handler_name.strip():
            raise ValueError('Handler name cannot be empty')

        if processing_seconds < 0:
            raise ValueError('Processing seconds cannot be negative')

        self._handler_name = handler_name.strip()
        self._processing_seconds = processing_seconds



    def process(self, task: Mapping[str, object]) -> dict[str, object]:
        task_id = self._get_required_string(task, field_name='task_id')
        task_name = self._get_required_string(task, field_name='task_name')
        outcome = self._get_outcome(task)

        logger.info(
            f'[{self._handler_name}] Processing task: <{task_id}> | '
            f'task_name:<{task_name}> | processing_outcome=<{outcome.value}>'
        )

        # Simulate real work
        time.sleep(self._processing_seconds)


        if outcome is ProcessingOutcome.TRANSIENT_FAILURE:
            raise TransientProcessingError(
                f'[{self._handler_name}] Temporary processing failure for task <{task_id}>'
            )


        if outcome is ProcessingOutcome.PERMANENT_FAILURE:
            raise PermanentProcessingError(
                f'[{self._handler_name}] Permanent processing failure for task <{task_id}>'
            )


        result = {
            'task_id': task_id,
            'task_name': task_name,
            'processing_outcome': outcome.value,
            'handler': self._handler_name,
            'status': 'processed',
        }

        logger.info(f'[{self._handler_name}] Finished processing task: <{task_id}>')

        return result






    @staticmethod
    def _get_required_string(
        task: Mapping[str, object], *, field_name: str) -> str:
        value = task.get(field_name)

        if not isinstance(value, str) or not value.strip():
            raise PermanentProcessingError(
                f'Task must contain a valid {field_name}.'
            )

        return value.strip()




    @classmethod
    def _get_outcome(cls, task: Mapping[str, object]) -> ProcessingOutcome:
        raw_outcome = cls._get_required_string(task, field_name='processing_outcome')

        try:
            return ProcessingOutcome(raw_outcome)


        except ValueError as exc:
            raise PermanentProcessingError(
                f'Unsupported processing_outcome: <{raw_outcome}>.'
            ) from exc










