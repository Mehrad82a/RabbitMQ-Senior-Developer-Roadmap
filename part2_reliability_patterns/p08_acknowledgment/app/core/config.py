from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # =========================================
    # RabbitMQ
    # =========================================
    rabbitmq_host: str = Field(default='rabbitmq', alias='RABBITMQ_HOST')
    rabbitmq_port: int = Field(default=5672, alias='RABBITMQ_PORT')
    rabbitmq_user: str = Field(alias='RABBITMQ_USER')
    rabbitmq_pass: str = Field(alias='RABBITMQ_PASS')

    heartbeat: int = Field(default=600, alias='HEARTBEAT')
    blocked_connection_timeout: int = Field(default=300, alias='BLOCKED_CONNECTION_TIMEOUT')
    connection_attempts: int = Field(default=10, alias='CONNECTION_ATTEMPTS')
    retry_delay: int = Field(default=5, alias='RETRY_DELAY')
    socket_timeout: int = Field(default=10, alias='SOCKET_TIMEOUT')


    # =========================================
    # Acknowledgment Experiment Queues
    # =========================================
    auto_ack_queue: str = Field(
        default='ack.auto.queue',
        alias='AUTO_ACK_QUEUE',
    )
    manual_ack_queue: str = Field(
        default='ack.manual.queue',
        alias='MANUAL_ACK_QUEUE',
    )


    # =========================================
    # Worker
    # =========================================
    consumer_mode: str = Field(default='manual', alias='CONSUMER_MODE')


    # =========================================
    # Pydantic Settings
    # =========================================
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )


settings = Settings()