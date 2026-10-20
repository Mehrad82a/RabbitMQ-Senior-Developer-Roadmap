"""
Unit tests for RabbitMQTopology.

RabbitMQ calls are mocked because this file verifies declaration commands,
not the broker's real dead-letter behavior.
"""


import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, call

from app.core.topology import RabbitMQTopology




@pytest.fixture
def topology_config() -> SimpleNamespace:
    return SimpleNamespace(
        task_exchange='tasks.exchange',
        task_queue='tasks.queue',
        task_routing_key='tasks.process',
        dead_letter_exchange='tasks.dlx',
        dead_letter_queue='tasks.dlq',
        dead_letter_routing_key='tasks.failed',
    )


def test_declare_creates_dead_letter_and_task_topology(
        topology_config: SimpleNamespace,
) -> None:

    channel = MagicMock()
    channel.is_open = True

    topology = RabbitMQTopology(config=topology_config)

    topology.declare(channel)

    assert channel.exchange_declare.call_args_list == [
        call(
            exchange='tasks.dlx',
            exchange_type='direct',
            durable=True,
        ),
        call(
            exchange='tasks.exchange',
            exchange_type='direct',
            durable=True,
        )
    ]

    assert channel.queue_declare.call_args_list == [
        call(
            queue='tasks.dlq',
            durable=True,
            exclusive=False,
            auto_delete=False,
        ),
        call(
            queue='tasks.queue',
            durable=True,
            exclusive=False,
            auto_delete=False,
        )
    ]

    assert channel.queue_bind.call_args_list == [
        call(
            queue='tasks.dlq',
            exchange='tasks.dlx',
            routing_key='tasks.failed',
        ),
        call(
            queue='tasks.queue',
            exchange='tasks.exchange',
            routing_key='tasks.process',
        )
    ]




def test_declare_rejects_closed_channel(
        topology_config: SimpleNamespace,
) -> None:

    channel = MagicMock()
    channel.is_open = False

    topology = RabbitMQTopology(config=topology_config)

    with pytest.raises(
        RuntimeError,
        match='open RabbitMQ channel'
    ):
        topology.declare(channel)




def test_constructor_rejects_same_main_and_dead_letter_queue(
        topology_config: SimpleNamespace,
) -> None:

    topology_config.dead_letter_queue = topology_config.task_queue

    with pytest.raises(
        ValueError,
        match='must be different'
    ):
        RabbitMQTopology(config=topology_config)



