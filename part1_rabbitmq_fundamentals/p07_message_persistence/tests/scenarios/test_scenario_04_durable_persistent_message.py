"""
Scenario 04: Durable Queue + Persistent Message

Configuration:
    queue_durable = True
    message_persistent = True

Expected state before RabbitMQ restart:
    - Publisher confirmation is successful.
    - Queue exists.
    - Message count is 1.

Expected state after RabbitMQ restart:
    - Queue still exists.
    - Message still exists.
    - Message count is 1.

Reason:
    RabbitMQ restores the durable queue after restart because its
    metadata is persisted. The persistent message is also recovered
    because it is published with delivery_mode=2.

Expected comparison result:
    queue_survives_restart = True
    message_survives_restart = True

Note:
    This is an integration test. It publishes a real message, restarts
    the RabbitMQ container, and inspects the actual queue state after
    RabbitMQ becomes ready again.
"""

from uuid import uuid4

from app.core.logger import logger
from tests.helpers.rabbitmq.scenario import RabbitMQScenarioController


def test_durable_queue_and_persistent_message(rabbitmq_scenario: RabbitMQScenarioController) -> None:
    queue_name = (
        'p07.test.durable.persistent.'
        f'{uuid4().hex}'
    )

    logger.info(
        '[Scenario04] Starting test: '
        'Durable Queue + Persistent Message'
    )

    broker_confirmed = rabbitmq_scenario.publish_message(
        queue_name=queue_name,
        queue_durable=True,
        message_persistent=True,
        body='Scenario 04 test message',
    )

    state_before_restart = rabbitmq_scenario.inspect_queue(
        queue_name=queue_name,
    )

    logger.info(
        f'[Scenario04] Before RabbitMQ restart: '
        f'queue=<{queue_name}> '
        f'exists=<{state_before_restart.exists}> '
        f'message_count=<{state_before_restart.message_count}>'
    )

    assert broker_confirmed is True
    assert state_before_restart.exists is True
    assert state_before_restart.message_count == 1

    rabbitmq_scenario.restart_rabbitmq()

    state_after_restart = rabbitmq_scenario.inspect_queue(
        queue_name=queue_name,
    )

    logger.info(
        f'[Scenario04] After RabbitMQ restart: '
        f'queue=<{queue_name}> '
        f'exists=<{state_after_restart.exists}> '
        f'message_count=<{state_after_restart.message_count}>'
    )

    assert state_after_restart.exists is True
    assert state_after_restart.message_count == 1

    logger.info(
        '[Scenario04] Test passed: '
        'durable queue and persistent message survived.'
    )