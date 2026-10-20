"""
Unit tests for TaskHandler.

The handler converts low-level processing errors into failures the Consumer
can use to choose ACK, NACK, or Reject behavior.
"""


import pytest
from collections.abc import Callable

from app.services.exceptions import (
    PermanentProcessingError,
    TransientProcessingError,
)
from app.services.task_handler import TaskHandler
from tests.fakes.task_processors import (
    PermanentlyFailingTaskProcessor,
    SuccessfulTaskProcessor,
    TemporaryFailingTaskProcessor,
)





def test_process_returns_result_from_successful_processor(
        task_factory: Callable[..., dict[str, object]]
) -> None:

    handler =  TaskHandler(
        processor=SuccessfulTaskProcessor(),
        handler_name='UnitTestHandler',
    )

    result = handler.process(task_factory())

    assert result == {
        'task_id': 'task-123',
        'task_name': 'generate-report',
        'processor': 'SuccessfulTaskProcessor',
        'status': 'processed',
    }




def test_process_converts_timeout_to_transient_processing_error(
        task_factory: Callable[..., dict[str, object]]
) -> None:

    handler = TaskHandler(
        processor=TemporaryFailingTaskProcessor()
    )

    with pytest.raises(
        TransientProcessingError,
        match='Temporary processing failure',
    ):
        handler.process(task_factory())



def test_process_converts_invalid_task_to_permanent_processing_error(
        task_factory: Callable[..., dict[str, object]]
) -> None:

    handler = TaskHandler(
        processor=PermanentlyFailingTaskProcessor(),
    )

    with pytest.raises(
        PermanentProcessingError,
        match='contains invalid data',
    ):
        handler.process(task_factory())




def test_constructor_rejects_blank_handler_name() -> None:
    with pytest.raises(
        ValueError,
        match='Handler name cannot be empty'
    ):
        TaskHandler(handler_name='   ')


