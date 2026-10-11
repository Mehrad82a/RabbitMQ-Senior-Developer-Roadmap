

from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # =========================================
    # RabbitMQ
    # =========================================
    rabbitmq_host: str = Field(alias='RABBITMQ_HOST', default='rabbitmq')
    rabbitmq_port: int = Field(alias='RABBITMQ_PORT', default=5672)
    rabbitmq_user: str = Field(alias='RABBITMQ_USER')
    rabbitmq_pass: str = Field(alias='RABBITMQ_PASS')

    rabbitmq_virtual_host: str = Field(alias='RABBITMQ_VIRTUAL_HOST', default='/', min_length=1)


    heartbeat: int = Field(alias='HEARTBEAT', default=600, ge=0)
    blocked_connection_timeout: int = Field(alias='BLOCKED_CONNECTION_TIMEOUT', default=300, gt=0)
    connection_attempts: int = Field(alias='CONNECTION_ATTEMPTS', default=10, ge=1)
    retry_delay: int = Field(alias='RETRY_DELAY', default=5, ge=0)
    socket_timeout: int = Field(alias='SOCKET_TIMEOUT', default=10, gt=0)


    # =========================================
    # Main Task Topology
    # Replaces the Auto/Manual experiment queues.
    # =========================================

    task_exchange: str = Field(alias='TASK_EXCHANGE', default='tasks.exchange', min_length=1)
    task_queue: str = Field(alias='TASK_QUEUE', default='tasks.queue', min_length=1)
    task_routing_key: str = Field(alias='TASK_ROUTING_KEY', default='tasks.process', min_length=1)


    # =========================================
    # Dead-Letter Topology
    # =========================================

    dead_letter_exchange: str = Field(alias='DEAD_LETTER_EXCHANGE', default='tasks.dlx', min_length=1)
    dead_letter_queue: str = Field(alias='DEAD_LETTER_QUEUE', default='tasks.dlq', min_length=1)
    dead_letter_routing_key: str = Field(alias='DEAD_LETTER_ROUTING_KEY', default='tasks.failed', min_length=1)


    # =========================================
    # Consumer
    # =========================================
    prefetch_count: int = Field(
        default=1,
        alias='PREFETCH_COUNT',
        ge=1,
    )

    # =========================================
    # Test RabbitMQ
    # =========================================
    rabbitmq_test_host: str = Field(alias='RABBITMQ_TEST_HOST', default='localhost', min_length=1)
    rabbitmq_test_port: int = Field(alias='RABBITMQ_TEST_PORT', default=5672, ge=1, le=65535)



    # =========================================
    # Pydantic Settings
    # =========================================
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / '.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )


settings = Settings()