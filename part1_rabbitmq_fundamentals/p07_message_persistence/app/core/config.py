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

    heartbeat: int = Field(default=600 ,alias='HEARTBEAT')
    blocked_connection_timeout: int = Field(default=300, alias='BLOCKED_CONNECTION_TIMEOUT')
    connection_attempts: int = Field(default=3, alias='CONNECTION_ATTEMPTS')
    retry_delay: int = Field(default=5, alias='RETRY_DELAY')
    socket_timeout: int = Field(default=10, alias='SOCKET_TIMEOUT')


    # Persistence experiment queues
    non_durable_transient_queue: str = Field(
        default='p07.non_durable.transient',
        alias='NON_DURABLE_TRANSIENT_QUEUE',
    )
    non_durable_persistent_queue: str = Field(
        default='p07.non_durable.persistent',
        alias='NON_DURABLE_PERSISTENT_QUEUE',
    )
    durable_transient_queue: str = Field(
        default='p07.durable.transient',
        alias='DURABLE_TRANSIENT_QUEUE',
    )
    durable_persistent_queue: str = Field(
        default='p07.durable.persistent',
        alias='DURABLE_PERSISTENT_QUEUE',
    )


    # =========================================
    # Pydantic Settings
    # =========================================
    model_config = SettingsConfigDict(
        env_file='',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )


settings = Settings()