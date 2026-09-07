import pytest
from collections.abc import Generator

from app.core.logger import logger

from tests.helpers.docker_compose import (
    get_running_services,
    start_service,
    stop_service,
)
from tests.helpers.rabbitmq import (
    RabbitMQScenarioController,
    wait_for_rabbitmq,
)
from tests.helpers.settings import (
    RABBITMQ_SERVICE_NAME,
    WORKER_SERVICE_NAME,
)




@pytest.fixture(
    scope='session',
    autouse=True,
)
def rabbitmq_environment() -> Generator[None, None, None]:
    initially_running_services = get_running_services()

    rabbitmq_was_running = (
        RABBITMQ_SERVICE_NAME
        in initially_running_services
    )
    worker_was_running = (
        WORKER_SERVICE_NAME
        in initially_running_services
    )

    try:
        if worker_was_running:
            logger.info('\nStopping worker for persistence tests...')

            stop_service(WORKER_SERVICE_NAME)

        if not rabbitmq_was_running:
            logger.info('\nStarting RabbitMQ for persistence tests...')

            start_service(RABBITMQ_SERVICE_NAME)

        wait_for_rabbitmq()

        yield


    finally:
        running_services = get_running_services()

        if (
            worker_was_running
            and WORKER_SERVICE_NAME not in running_services
        ):
            if RABBITMQ_SERVICE_NAME not in running_services:
                start_service(RABBITMQ_SERVICE_NAME)
                wait_for_rabbitmq()

            logger.info('\nRestoring worker service...')

            start_service(WORKER_SERVICE_NAME)

        running_services = get_running_services()

        if (
            not rabbitmq_was_running
            and RABBITMQ_SERVICE_NAME in running_services
        ):
            logger.info('\nRestoring RabbitMQ service state...')

            stop_service(RABBITMQ_SERVICE_NAME)



@pytest.fixture
def rabbitmq_scenario(rabbitmq_environment: None) -> Generator[RabbitMQScenarioController, None, None]:
    controller = RabbitMQScenarioController()

    try:
        yield controller

    finally:
        controller.cleanup()