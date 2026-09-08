"""
Scenario 02: Non-durable Queue + Persistent Message

Configuration:
    queue_durable = False
    message_persistent = True

Expected state before RabbitMQ restart:
    - Publisher confirmation is successful.
    - Queue exists.
    - Message count is 1.

Expected state after RabbitMQ restart:
    - Queue does not exist.
    - Message does not exist.

Reason:
    A persistent message cannot survive when its queue is non-durable.
    RabbitMQ removes the non-durable queue during restart, including
    all messages stored in it.
"""

from uuid import uuid4

from app.core.logger import logger
from tests.helpers.rabbitmq.scenario import RabbitMQScenarioController


def test_non_durable_queue_and_persistent_message(rabbitmq_scenario: RabbitMQScenarioController) -> None:
    queue_name = (
        'p07.test.non_durable.persistent.'
        f'{uuid4().hex}'
    )

    logger.info(
        '[Scenario02] Starting test: '
        'Non-durable Queue + Persistent Message'
    )

    broker_confirmed = rabbitmq_scenario.publish_message(
        queue_name=queue_name,
        queue_durable=False,
        message_persistent=True,
        body='Scenario 02 test message'
    )

    state_before_restart = rabbitmq_scenario.inspect_queue(
        queue_name=queue_name,
    )

    logger.info(
        f'[Scenario02] Before RabbitMQ restart: '
        f'queue=<{queue_name}> '
        f'exists=<{state_before_restart.exists}> '
        f'message_count=<{state_before_restart.message_count}>',
    )

    assert broker_confirmed is True
    assert state_before_restart.exists is True
    assert state_before_restart.message_count == 1

    rabbitmq_scenario.restart_rabbitmq()


    state_after_restart = rabbitmq_scenario.inspect_queue(
        queue_name=queue_name,
    )

    logger.info(
        f'[Scenario02] After RabbitMQ restart: '
        f'queue=<{queue_name}> '
        f'exists=<{state_after_restart.exists}> '
        f'message_count=<{state_after_restart.message_count}>',
    )

    assert state_after_restart.exists is False
    assert state_after_restart.message_count == 0

    logger.info(
        '[Scenario02] Test passed: '
        'non-durable queue and its persistent message were removed.'
    )
