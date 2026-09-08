"""
Scenario 01: Non-durable Queue + Transient Message

Configuration:
    queue_durable = False
    message_persistent = False

Expected state before RabbitMQ restart:
    - Publisher confirmation is successful.
    - Queue exists.
    - Message count is 1.

Expected state after RabbitMQ restart:
    - Queue does not exist.
    - Message does not exist.

Reason:
    A non-durable queue does not survive a RabbitMQ restart.
    Because the queue is removed, every message stored in it is also
    removed. In this scenario, the message itself is transient as well.

Expected comparison result:
    queue_survives_restart = False
    message_survives_restart = False

Note:
    This is an integration test. It publishes a real message, restarts
    the RabbitMQ container, and inspects the actual queue state after
    RabbitMQ becomes ready again.
"""

from uuid import uuid4

from app.core.logger import logger
from tests.helpers.rabbitmq.scenario import RabbitMQScenarioController



def test_non_durable_queue_and_transient(rabbitmq_scenario: RabbitMQScenarioController) -> None:
    queue_name = (
        'p07.test.non_durable.transient.'
        f'{uuid4().hex}'
    )

    logger.info(
        '[Scenario01] Starting test: '
        'Non-durable Queue + Transient Message'
    )

    broker_confirmed = rabbitmq_scenario.publish_message(
        queue_name=queue_name,
        queue_durable=False,
        message_persistent=False,
        body='Scenario 01 test message'
    )

    state_before_restart = rabbitmq_scenario.inspect_queue(
        queue_name=queue_name,
    )

    logger.info(
        f'[Scenario01] Before RabbitMQ restart: '
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
        f'[Scenario01] After RabbitMQ restart: '
        f'queue=<{queue_name}> '
        f'exists=<{state_after_restart.exists}> '
        f'message_count=<{state_after_restart.message_count}>',
    )

    assert state_after_restart.exists is False
    assert state_after_restart.message_count == 0

    logger.info(
        '[Scenario01] Test passed: '
        'non-durable queue and transient message were removed.'
    )


