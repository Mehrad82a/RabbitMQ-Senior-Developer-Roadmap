"""
Scenario 03: Durable Queue + Transient Message

Configuration:
    queue_durable = True
    message_persistent = False

Expected state before RabbitMQ restart:
    - Publisher confirmation is successful.
    - Queue exists.
    - Message count is 1.

Expected state after RabbitMQ restart:
    - Queue still exists.
    - Message does not exist.
    - Message count is 0.

Reason:
    RabbitMQ restores the durable queue after restart because its
    metadata is persisted. However, the transient message is published
    with delivery_mode=1 and is not recovered after broker restart.

Expected comparison result:
    queue_survives_restart = True
    message_survives_restart = False

Note:
    This is an integration test. It publishes a real message, restarts
    the RabbitMQ container, and inspects the actual queue state after
    RabbitMQ becomes ready again.
"""


from uuid import uuid4

from app.core.logger import logger
from tests.helpers.rabbitmq.scenario import RabbitMQScenarioController


def test_durable_queue_and_transient_message(rabbitmq_scenario: RabbitMQScenarioController) -> None:
    queue_name = (
        'p07.test.durable.transient.'
        f'{uuid4().hex}'
    )

    logger.info(
        '[Scenario03] Starting test: '
        'Durable Queue + Transient Message'
    )

    broker_confirmed = rabbitmq_scenario.publish_message(
        queue_name=queue_name,
        queue_durable=True,
        message_persistent=False,
        body='Scenario 03 test message',
    )

    state_before_restart = rabbitmq_scenario.inspect_queue(
        queue_name=queue_name,
    )

    logger.info(
        f'[Scenario03] Before RabbitMQ restart: '
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
        f'[Scenario03] After RabbitMQ restart: '
        f'queue=<{queue_name}> '
        f'exists=<{state_after_restart.exists}> '
        f'message_count=<{state_after_restart.message_count}>'
    )

    assert state_after_restart.exists is True
    assert state_after_restart.message_count == 0

    logger.info(
        '[Scenario03] Test passed: '
        'durable queue survived and transient message was removed.'
    )