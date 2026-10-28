"""
Unit tests for TaskConsumer.

The handler and RabbitMQ channel are mocked. These tests verify the Consumer's
ACK, NACK, and Reject decisions without a running RabbitMQ broker.
"""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest

from app.consumers.task_consumer import TaskConsumer
from app.services.exceptions import (
    PermanentProcessingError,
    TransientProcessingError,
)



@pytest.fixture
def consumer_config() -> SimpleNamespace:
    return SimpleNamespace(
        task_queue='tasks.queue',
        prefetch_count=1,
    )


@pytest.fixture
def channel() -> MagicMock:
    mock_channel = MagicMock()
    mock_channel.is_open = True
    mock_channel.is_consuming = True

    return mock_channel


@pytest.fixture
def rabbitmq(channel: MagicMock) -> MagicMock:
    connection = MagicMock()
    connection.connect.return_value = channel

    return connection


@pytest.fixture
def topology() -> MagicMock:
    return MagicMock()


@pytest.fixture
def handler() -> MagicMock:
    return MagicMock()



@pytest.fixture
def consumer(
        consumer_config: SimpleNamespace,
        rabbitmq: MagicMock,
        topology: MagicMock,
        handler: MagicMock,
) -> TaskConsumer:

    return TaskConsumer(
        config=consumer_config,
        rabbitmq=rabbitmq,
        topology=topology,
        handler=handler,
    )



def build_delivery(
        *,
        delivery_tag: int = 1,
        redelivered: bool = False,
) -> SimpleNamespace:

    return SimpleNamespace(
        delivery_tag=delivery_tag,
        redelivered=redelivered,
    )


def build_properties(
        *,
        message_id: str = 'message-123',
) -> SimpleNamespace:

    return SimpleNamespace(
        message_id=message_id,
    )



def test_callback_acknowledges_successful_task(
        consumer: TaskConsumer,
        channel: MagicMock,
        handler: MagicMock,
        task_factory,
) -> None:

    task = task_factory()
    handler.process.return_value = {
        'status': 'processed',
    }

    consumer._callback(
        channel,
        build_delivery(),
        build_properties(),
        json.dumps(task).encode('utf-8'),
    )

    handler.process.assert_called_once_with(task)
    channel.basic_ack.assert_called_once_with(delivery_tag=1)
    channel.basic_nack.assert_not_called()
    channel.basic_reject.assert_not_called()



def test_callback_requeues_first_transient_failure(
    consumer: TaskConsumer,
    channel: MagicMock,
    handler: MagicMock,
    task_factory,
) -> None:

    handler.process.side_effect = TransientProcessingError('Temporary error')

    consumer._callback(
        channel,
        build_delivery(redelivered=False),
        build_properties(),
        json.dumps(task_factory()).encode('utf-8'),
    )

    channel.basic_nack.assert_called_once_with(
        delivery_tag=1,
        requeue=True,
    )

    channel.basic_ack.assert_not_called()
    channel.basic_reject.assert_not_called()



def test_callback_rejects_transient_failure_after_redelivery(
    consumer: TaskConsumer,
    channel: MagicMock,
    handler: MagicMock,
    task_factory,
) -> None:

    handler.process.side_effect = TransientProcessingError('Temporary error')

    consumer._callback(
        channel,
        build_delivery(redelivered=True),
        build_properties(),
        json.dumps(task_factory()).encode('utf-8'),
    )

    channel.basic_reject.assert_called_once_with(
        delivery_tag=1,
        requeue=False,
    )

    channel.basic_ack.assert_not_called()
    channel.basic_nack.assert_not_called()



def test_callback_rejects_permanent_failure(
        consumer: TaskConsumer,
        channel: MagicMock,
        handler: MagicMock,
        task_factory,
) -> None:

    handler.process.side_effect = PermanentProcessingError('Invalid task')

    consumer._callback(
        channel,
        build_delivery(),
        build_properties(),
        json.dumps(task_factory()).encode('utf-8'),
    )

    channel.basic_reject.assert_called_once_with(
        delivery_tag=1,
        requeue=False,
    )

    channel.basic_ack.assert_not_called()
    channel.basic_nack.assert_not_called()



def test_callback_rejects_invalid_message(
        consumer: TaskConsumer,
        channel: MagicMock,
        handler: MagicMock,
) -> None:

    consumer._callback(
        channel,
        build_delivery(),
        build_properties(),
        b'not-valid-json',
    )

    handler.process.assert_not_called()
    channel.basic_reject.assert_called_once_with(
        delivery_tag=1,
        requeue=False,
    )



def test_callback_rejects_unexpected_processing_failure(
    consumer: TaskConsumer,
    channel: MagicMock,
    handler: MagicMock,
    task_factory,
) -> None:

    handler.process.side_effect = RuntimeError('Unexpected failure')

    consumer._callback(
        channel,
        build_delivery(),
        build_properties(),
        json.dumps(task_factory()).encode('utf-8'),
    )

    channel.basic_reject.assert_called_once_with(
        delivery_tag=1,
        requeue=False,
    )




def test_start_configures_consumer_and_closes_connection(
    consumer: TaskConsumer,
    channel: MagicMock,
    rabbitmq: MagicMock,
    topology: MagicMock,
    consumer_config: SimpleNamespace,
) -> None:

    consumer.start()

    topology.declare.assert_called_once_with(channel)
    channel.basic_qos.assert_called_once_with(
        prefetch_count=consumer_config.prefetch_count,
    )

    channel.basic_consume.assert_called_once()

    consume_kwargs = channel.basic_consume.call_args.kwargs

    assert consume_kwargs['queue'] == 'tasks.queue'
    assert consume_kwargs['auto_ack'] is False
    assert consume_kwargs['on_message_callback'] == consumer._callback

    channel.start_consuming.assert_called_once()
    rabbitmq.close.assert_called_once()




def test_stop_stops_an_active_channel(
    consumer: TaskConsumer,
    channel: MagicMock,
) -> None:
    consumer._channel = channel

    consumer.stop()

    channel.stop_consuming.assert_called_once()

