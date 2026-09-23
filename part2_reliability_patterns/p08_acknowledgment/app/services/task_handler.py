from collections.abc import Mapping

from app.core.logger import get_logger
from app.services.contracts import TaskProcessor
from app.services.exceptions import (
    InvalidTaskError,
    PermanentProcessingError,
    TransientProcessingError,
)

from app.services.task_processor import DefaultTaskProcessor



logger = get_logger(__name__)


class TaskHandler:
    """
    Coordinates task processing and translates processor exceptions into
    failures understood by RabbitMQ consumers.

    Exception mapping:

        successful processing
            -> return result

        InvalidTaskError
            -> PermanentProcessingError

        TimeoutError or ConnectionError
            -> TransientProcessingError

        PermanentProcessingError
            -> propagate unchanged

        TransientProcessingError
            -> propagate unchanged
    """

    def __init__(
            self,
            *,
            processor: TaskProcessor | None = None,
            handler_name: str = 'TaskHandler'
    ) -> None:
        if not handler_name.strip():
            raise ValueError('Handler name cannot be empty')

        self._handler_name = f'{handler_name.strip()} Handler'
        self._processor = processor if processor is not None else DefaultTaskProcessor()


    def process(self, task: Mapping[str, object]) -> dict[str, object]:
        task_id = self._get_context_value(task, field_name='task_id')
        task_name = self._get_context_value(task, field_name='task_name')

        logger.info(
            f'[{self._handler_name}] Processing task: '
            f'task_id: <{task_id}> | '
            f'task_name:<{task_name}>'
        )

        try:
            result = self._processor.execute(task)

        except InvalidTaskError as exc:
            raise PermanentProcessingError(
                f'Task <{task_id}> contains invalid data.'
            ) from exc


        except (TimeoutError, ConnectionError) as exc:
            raise TransientProcessingError(
                f'Temporary processing failure for task <{task_id}>.'
            ) from exc


        except TransientProcessingError:
            raise

        except PermanentProcessingError:
            raise


        logger.info(f'[{self._handler_name}] Finished processing task: <{task_id}>')

        return result




    @staticmethod
    def _get_context_value(
            task: Mapping[str, object],
            *,
            field_name: str,
    ) -> str:
        """
        Return a safe value for logging without performing business validation.
        """

        value = task.get(field_name)

        if isinstance(value, str) and value.strip():
            return value.strip()

        return 'unknown'













