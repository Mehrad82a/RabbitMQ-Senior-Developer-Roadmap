"""
Unit tests for Producer.

These tests verify Producer behavior with mocked RabbitMQ dependencies.
"""


from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.producer.producer import Producer, ProducerPublishError


@pytest.fixture
def producer_config() -> SimpleNamespace:
    return SimpleNamespace(
        task_exchange='tasks.exchange',
        task_routing_key='tasks.process',
    )


@pytest.fixture
def rabbitmq() -> MagicMock:
    connection = MagicMock()
    connection.connect.return_value = MagicMock()

    return connection




@pytest.fixture
def topology() -> MagicMock:
    return MagicMock()




def test_publish_declares_topology_and_publishes_persistent_task(
        task_factory,
        producer_config: SimpleNamespace,
        rabbitmq: MagicMock,
        topology: MagicMock,
) -> None:

    channel = rabbitmq.connect.return_value
    producer = Producer(
        config=producer_config,
        rabbitmq=rabbitmq,
        topology=topology,
    )

    producer.publish(task=task_factory())

    topology.declare.assert_called_once_with(channel)
    channel.confirm_delivery.assert_called_once()

    channel.basic_publish.assert_called_once()

    publish_kwargs = channel.basic_publish.call_args.kwargs

    assert publish_kwargs['exchange'] == 'tasks.exchange'
    assert publish_kwargs['routing_key'] == 'tasks.process'
    assert publish_kwargs['mandatory'] is True
    assert publish_kwargs['body'] == (
        b'{"task_id":"task-123","task_name":"generate-report",'
        b'"created_at":"2026-10-18T10:00:00+00:00"}'
    )

    properties = publish_kwargs['properties']

    assert properties.content_type == 'application/json'
    assert properties.content_encoding == 'utf-8'
    assert properties.delivery_mode == 2
    assert properties.type == 'task'
    assert properties.message_id == 'task-123'

    rabbitmq.close.assert_called_once()



def test_publish_wraps_broker_failure(
        task_factory,
        producer_config: SimpleNamespace,
        rabbitmq: MagicMock,
        topology: MagicMock,
) -> None:

    rabbitmq.connect.side_effect = OSError('Broker is unavailable')

    producer = Producer(
        config=producer_config,
        rabbitmq=rabbitmq,
        topology=topology,
    )

    with pytest.raises(
        ProducerPublishError,
        match='could not be published',
    ):
        producer.publish(task=task_factory())

    rabbitmq.close.assert_called_once()




def test_publish_rejects_task_without_valid_id(
    producer_config: SimpleNamespace,
    rabbitmq: MagicMock,
    topology: MagicMock,
) -> None:
    producer = Producer(
        config=producer_config,
        rabbitmq=rabbitmq,
        topology=topology,
    )

    with pytest.raises(
        ValueError,
        match='non-empty string task_id',
    ):
        producer.publish(
            task={
                'task_name': 'generate-report',
            }
        )

    rabbitmq.connect.assert_not_called()



def test_publish_rejects_non_serializable_task_value(
    task_factory,
    producer_config: SimpleNamespace,
    rabbitmq: MagicMock,
    topology: MagicMock,
) -> None:
    producer = Producer(
        config=producer_config,
        rabbitmq=rabbitmq,
        topology=topology,
    )

    with pytest.raises(
        ProducerPublishError,
        match='cannot be serialized',
    ):
        producer.publish(
            task=task_factory(extra_value=object()),
        )

    rabbitmq.connect.assert_not_called()