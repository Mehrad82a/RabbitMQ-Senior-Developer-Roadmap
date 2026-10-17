"""
Unit Test Group: DefaultTaskProcessor

Component under test:
    DefaultTaskProcessor

Responsibilities:
    - Validate required task fields.
    - Normalize task_id and task_name.
    - Process a valid task successfully.
    - Reject invalid configuration.

These tests do not connect to RabbitMQ.
"""



import pytest
from collections.abc import Callable

from app.services.exceptions import InvalidTaskError
from app.services.task_processor import DefaultTaskProcessor




def test_execute_returns_processed_result_for_valid_task(
        task_factory: Callable[..., dict[str, object]],
) -> None:

    task = task_factory()
    processor = DefaultTaskProcessor(processing_seconds=3)

    result = processor.execute(task)

    assert result == {
        'task_id': 'task-123',
        'task_name': 'generate-report',
        'processor': 'DefaultTaskProcessor',
        'status': 'processed',
    }




def test_execute_normalizes_required_task_fields(
        task_factory: Callable[..., dict[str, object]],
) -> None:

    task = task_factory(
        task_id='    task-123   ',
        task_name='  generate-report  ',
    )

    processor = DefaultTaskProcessor(processing_seconds=3)

    result = processor.execute(task)


    assert result['task_id'] == 'task-123'
    assert result['task_name'] == 'generate-report'





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

    processor = DefaultTaskProcessor(processing_seconds=3)

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


