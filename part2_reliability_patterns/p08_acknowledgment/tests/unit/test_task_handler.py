"""
Unit Test Group: Task Handler

Component under test:
    TaskHandler

Responsibilities:
    - Execute the injected TaskProcessor.
    - Return successful processing results.
    - Convert InvalidTaskError into PermanentProcessingError.
    - Convert TimeoutError and ConnectionError into
      TransientProcessingError.
    - Preserve known processing exceptions.
    - Reject an empty handler name.

Scenarios:
    1. Successful processor returns its result.
    2. Invalid task data becomes a permanent processing failure.
    3. Temporary dependency errors become transient failures.
    4. Existing domain processing errors are propagated unchanged.
    5. Blank handler names are rejected.

Expected behavior:
    TaskHandler translates low-level processor failures into errors that
    RabbitMQ consumers can use to make acknowledgment decisions.

Note:
    These are unit tests. No RabbitMQ connection is created.
"""

from collections.abc import Callable, Mapping
import pytest

from app.services.contracts import TaskProcessor
from app.services.exceptions import (
    InvalidTaskError,
    PermanentProcessingError,
    TransientProcessingError,
)
from app.services.task_handler import TaskHandler
from tests.fakes.task_processors import (
    PermanentlyFailingTaskProcessor,
    SuccessfulTaskProcessor,
    TemporarilyFailingTaskProcessor,
)


class RaisingTaskProcessor:
    """
    Test processor that raises a predefined exception.
    """

    def __init__(self, error: Exception) -> None:
        self._error = error

    def execute(self, task: Mapping[str, object]) -> dict[str, object]:
        raise self._error


def test_process_returns_successful_processor_result(
        task_factory: Callable[..., dict[str, object]],
        successful_processor: SuccessfulTaskProcessor,
        handler_factory: Callable[[TaskProcessor], TaskHandler],
) -> None:
    task = task_factory()
    handler = handler_factory(successful_processor)

    result = handler.process(task)

    assert result == {
        'task_id': task['task_id'],
        'task_name': task['task_name'],
        'processor': 'SuccessfulTaskProcessor',
        'status': 'processed',
    }





def test_process_maps_invalid_task_to_permanent_failure(
        task_factory: Callable[..., dict[str, object]],
        permanent_processor: PermanentlyFailingTaskProcessor,
        handler_factory: Callable[[TaskProcessor], TaskHandler],
) -> None:
    task = task_factory()
    handler = handler_factory(permanent_processor)

    with pytest.raises(PermanentProcessingError) as exc_info:
        handler.process(task)

    assert isinstance(
        exc_info.value.__cause__,
        InvalidTaskError,
    )




def test_process_maps_timeout_to_transient_failure(
        task_factory: Callable[..., dict[str, object]],
        transient_processor: TemporarilyFailingTaskProcessor,
        handler_factory: Callable[[TaskProcessor], TaskHandler],

) -> None:
    task = task_factory()
    handler = handler_factory(transient_processor)

    with pytest.raises(TransientProcessingError) as exc_info:
        handler.process(task)

    assert isinstance(
        exc_info.value.__cause__,
        TimeoutError
    )




def test_process_maps_connection_error_to_transient_failure(
        task_factory: Callable[..., dict[str, object]],
) -> None:
    task = task_factory()
    processor = RaisingTaskProcessor(
        ConnectionError('Dependency connection failed.')
    )
    handler = TaskHandler(
        processor=processor,
        handler_name='TestTaskHandler',
    )

    with pytest.raises(TransientProcessingError) as exc_info:
        handler.process(task)

    assert isinstance(
        exc_info.value.__cause__,
        ConnectionError,
    )



@pytest.mark.parametrize(
    'error',
    [
        TransientProcessingError('Known transient failure.'),
        PermanentProcessingError('Known permanent failure.'),
    ],
)
def test_process_preserves_known_processing_errors(
        task_factory: Callable[..., dict[str, object]],
        error: Exception,
) -> None:
    task = task_factory()
    processor = RaisingTaskProcessor(error)
    handler = TaskHandler(
        processor=processor,
        handler_name='TestTaskHandler',
    )

    with pytest.raises(type(error)) as exc_info:
        handler.process(task)

    assert exc_info.value is error



@pytest.mark.parametrize(
    'handler_name',
    [
        '',
        '   ',
    ],
)
def test_constructor_rejects_blank_handler_name(
        successful_processor: SuccessfulTaskProcessor,
        handler_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match='Handler name cannot be empty',
    ):
        TaskHandler(
            processor=successful_processor,
            handler_name=handler_name,
        )



