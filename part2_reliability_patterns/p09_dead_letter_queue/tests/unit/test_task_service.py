"""
Unit tests for TaskService.

RabbitMQ is replaced by a mocked Producer.
"""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import UUID

import pytest

from app.producer.producer import ProducerPublishError
from app.services.exceptions import TaskPublishError
from app.services.task_service import TaskService




@pytest.fixture
def service_config() -> SimpleNamespace:
    return SimpleNamespace(
        task_queue='tasks.queue'
    )



def test_send_task_builds_and_publishes_task(
        service_config: SimpleNamespace,
) -> None:
    producer = MagicMock()
    service = TaskService(
        producer=producer,
        config=service_config,
    )

    result = service.send_task(task_name='  generate-report  ')

    producer.publish.assert_called_once()

    published_task = producer.publish.call_args.kwargs['task']

    assert UUID(published_task['task_id'])
    assert published_task['task_name'] == 'generate-report'
    assert datetime.fromisoformat(published_task['created_at'])

    assert result['task_id'] == published_task['task_id']
    assert result['task_name'] == 'generate-report'
    assert result['queue_name'] == 'tasks.queue'
    assert result['status'] == 'queued'




def test_send_task_wraps_producer_failure(
        service_config: SimpleNamespace,
) -> None:
    producer = MagicMock()
    producer.publish.side_effect = ProducerPublishError('Broker failure')

    service = TaskService(
        producer=producer,
        config=service_config,
    )

    with pytest.raises(
        TaskPublishError,
        match='could not be published',
    ):
        service.send_task(task_name='generate-report')



def test_send_task_rejects_blank_task_name(
        service_config: SimpleNamespace,
) -> None:
    producer = MagicMock()

    service = TaskService(
        producer=producer,
        config=service_config,
    )

    with pytest.raises(
        ValueError,
        match='Task name cannot be empty',
    ):
        service.send_task(task_name='   ')

    producer.publish.assert_not_called()



