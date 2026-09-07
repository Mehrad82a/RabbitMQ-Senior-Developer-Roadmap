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
        f'queue=<{queue_name}> exists=<{state_before_restart.exists}> message_count=<{state_before_restart.message_count}>',
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
        f'queue=<{queue_name}> exists=<{state_after_restart.exists}> message_count=<{state_after_restart.message_count}>',
    )

    assert state_after_restart.exists is False
    assert state_after_restart.message_count == 0

    logger.info(
        '[Scenario01] Test passed: '
        'non-durable queue and transient message were removed.'
    )


