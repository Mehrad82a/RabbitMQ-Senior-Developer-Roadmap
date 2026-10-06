"""
Unit Test Group: Default Task Processor

Component under test:
    DefaultTaskProcessor

Responsibilities:
    - Validate the required task fields.
    - Normalize task_id and task_name.
    - Execute the default business logic.
    - Return a successful processing result.
    - Reject invalid processing configuration.

Scenarios:
    1. A valid task is processed successfully.
    2. Leading and trailing whitespace is removed from required fields.
    3. Missing, blank, or non-string required fields are rejected.
    4. A negative processing duration is rejected.

Expected behavior:
    - Valid tasks return status='processed'.
    - task_id and task_name are normalized before being returned.
    - Invalid task data raises InvalidTaskError.
    - Invalid processor configuration raises ValueError.

Note:
    These are unit tests. They do not connect to RabbitMQ and use
    processing_seconds=0 to avoid real delays during the test suite.
"""

from collections.abc import Callable
from typing import Any

import pytest

from app.services.exceptions import InvalidTaskError
from app.services.task_processor import DefaultTaskProcessor


def test_execute_returns_processed_result_for_valid_task(
        task_factory: Callable[..., dict[str, object]],

) -> None:
    task = task_factory()
    processor = DefaultTaskProcessor(processing_seconds=0)

    result = processor.execute(task)

    assert result == {
        'task_id': task['task_id'],
        'task_name': task['task_name'],
        'processor': 'DefaultTaskProcessor',
        'status': 'processed',
    }



def test_execute_normalizes_required_task_fields(
        task_factory: Callable[..., dict[str, object]],
) -> None:
    task = task_factory(
        task_id='  task-123  ',
        task_name='  generate_invoice  ',
    )

    processor = DefaultTaskProcessor(processing_seconds=0)

    result = processor.execute(task)

    assert result['task_id'] == 'task-123'
    assert result['task_name'] == 'generate_invoice'



@pytest.mark.parametrize(
    ('field_name', 'invalid_value'),
    [
        ('task_id', None),
        ('task_id', ''),
        ('task_id', '   '),
        ('task_id', 123),
        ('task_name', None),
        ('task_name', ''),
        ('task_name', '   '),
        ('task_name', 123),
    ],
)
def test_execute_rejects_invalid_required_fields(
        task_factory: Callable[..., dict[str, object]],
        field_name: str,
        invalid_value: object,
) -> None:
    task = task_factory(
        **{field_name: invalid_value},
    )

    processor = DefaultTaskProcessor(processing_seconds=0)

    with pytest.raises(
        InvalidTaskError,
        match=field_name,
    ):
        processor.execute(task)





def test_constructor_rejects_negative_processing_duration() -> None:
    with pytest.raises(
        ValueError,
        match='Processing seconds cannot be negative',
    ):
        DefaultTaskProcessor(processing_seconds=-1)





