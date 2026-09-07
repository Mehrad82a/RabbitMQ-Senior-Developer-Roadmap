import os
from pathlib import Path



PROJECT_ROOT = Path(__file__).resolve().parent[2]
ENV_FILE = PROJECT_ROOT / '.env'


RABBITMQ_SERVICE_NAME = 'rabbitmq'
WORKER_SERVICE_NAME = 'worker'

RABBITMQ_START_TIMEOUT_SECONDS = 60
RABBITMQ_RETRY_DELAY_SECONDS = 2


def read_env_file() -> dict[str, str]:
    if not ENV_FILE.exists():
        raise RuntimeError(f'Environment file does not exist: {ENV_FILE}')


    values: dict[str, str] = {}

    for raw_line in ENV_FILE.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()

        if not line or line.startswith('#'):
            continue

        key, seperator, value = line.partition('=')

        if not seperator:
            continue

        values[key.strip()] = value.strip()

    return values



ENV_VALUES = read_env_file()


def get_env_value(key: str, *, default: str | None = None) -> str:
    value = (os.getenv(key) or ENV_VALUES.get(key) or default)

    if value is None:
        raise RuntimeError(f'Required environment variable {key} is missing')

    return value



def get_integer_env_value(key: str, *, default: str | None = None) -> int:
    value = get_env_value(key, default=default)

    try:
        return int(value)

    except ValueError as exc:
        raise RuntimeError(f'Environment variable must be an integer: {value}') from exc



RABBITMQ_HOST = get_env_value('RABBITMQ_TEST_HOST', default='localhost')
RABBITMQ_PORT = get_env_value('RABBITMQ_PORT', default='5672')

RABBITMQ_USER = get_env_value('RABBITMQ_USER')
RABBITMQ_PASS = get_env_value('RABBITMQ_PASS')
