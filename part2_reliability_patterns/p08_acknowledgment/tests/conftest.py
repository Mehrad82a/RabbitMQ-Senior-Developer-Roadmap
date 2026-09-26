import json
from collections.abc import Callable, Mapping
from unittest.mock import MagicMock, create_autospec
from uuid import uuid4

import pytest
import pika
from pika.adapters.blocking_connection import BlockingChannel

from app.services.contracts import TaskProcessor
from app.services.task_handler import TaskHandler
from tests.fakes.task_processors import (
    PermanentlyFailingTaskProcessor,
    SuccessfulTaskProcessor,
    TemporarilyFailingTaskProcessor,
)


@pytest.fixture
def task_factory() -> Callable[..., dict[str, object]]
    """
    Build a valid task payload with optional field overrides.
    """

    def factory(**overrides: object) -> dict[str, object]:
        task: dict[str, object] = {
            'task_id': str(uuid4()),
            'task_name': 'generate_invoice',
            'created_at': '2026-01-01T00:00:00+00:00',
        }
        task.update(overrides)
        return task

    return factory


@pytest.fixture
def successful_processor() -> SuccessfulTaskProcessor:
    """
    Return a processor that completes successfully.
    """

    return SuccessfulTaskProcessor()


@pytest.fixture
def transient_processor() -> TemporarilyFailingTaskProcessor:
    """
    Return a processor that simulates a temporary dependency failure.
    """

    return TemporarilyFailingTaskProcessor()


@pytest.fixture
def permanent_processor() -> PermanentlyFailingTaskProcessor:
    """
    Return a processor that simulates a permanent business failure.
    """

    return PermanentlyFailingTaskProcessor()




@pytest.fixture
def handler_factory() -> Callable[[TaskProcessor], TaskHandler]:
    """
    Build a TaskHandler with an injected processor.
    """

    def factory(processor: TaskProcessor) -> TaskHandler:
        return TaskHandler(
            processor=processor,
            handler_name='TestTaskHandler',
        )

    return factory





@pytest.fixture
def channel_mock() -> MagicMock:
    """
    Return a strict mock implementing BlockingChannel methods.
    """
    return create_autospec(
        BlockingChannel,
        instance=True,
    )




@pytest.fixture
def delivery_method_factory() -> Callable[..., pika.spec.Basic.Deliver]:
    """
    Build RabbitMQ delivery metadata for consumer callback tests.
    """

    def factory(
        *,
        delivery_tag: int = 1,
        redelivered: bool = False,
    ) -> pika.spec.Basic.Deliver:
        return pika.spec.Basic.Deliver(
            consumer_tag='test-consumer',
            delivery_tag=delivery_tag,
            redelivered=redelivered,
            exchange='',
            routing_key='test.queue',
        )

    return factory




@pytest.fixture
def message_body_factory() -> Callable[[Mapping[str, object]], bytes]:
    """
    Serialize a task payload to the same JSON format used by RabbitMQ.
    """
    def factory(task: Mapping[str, object]) -> bytes:
        return json.dumps(
            dict(task),
            ensure_ascii=False,
            separators=(',', ':'),
        ).encode('utf-8')

    return factory




@pytest.fixture
def message_properties() -> pika.BasicProperties:
    """
    Return message properties used by consumer callback tests.
    """

    return pika.BasicProperties(
        content_type='application/json',
        content_encoding='utf-8',
        delivery_mode=2,
        type='ack_experiment_task',
    )

