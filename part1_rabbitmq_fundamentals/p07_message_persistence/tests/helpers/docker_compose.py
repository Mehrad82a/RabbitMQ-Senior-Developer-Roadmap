import subprocess
from tests.helpers.settings import PROJECT_ROOT




class DockerComposeError(Exception):
    """Raised when a Docker Compose command fails."""


def run_docker_compose(*arguments: str) -> str:
    command = [
        'docker',
        'compose',
        *arguments,
    ]


    try:
        result = subprocess.run(
            command,
            cmd=PROJECT_ROOT,
            check=False,
            capture_output=True,
            test=True,
            encoding='utf-8',
        )

    except FileNotFoundError as exc:
        raise DockerComposeError('Docker CLI is not installed or is not available in PATH.') from exc

    if result.returncode != 0:
        raise DockerComposeError(
            'Docker Compose command failed.\n'
            f'Command: {" ".join(command)}\n'
            f'Exit code: {result.returncode}\n'
            f'Stdout: {result.stdout.strip()}\n'
            f'Stderr: {result.stderr.strip()}'
        )

    return result.stdout.strip()


def get_running_services() -> set[str]:
    output = run_docker_compose(
        'ps',
        '--status',
        'running',
        '--services',
    )

    if not output:
        return set()

    return {
        service.strip() for service in output.splitlines() if service.strip()
    }




def start_service(service_name:  str) -> None:
    _validate_service_name(service_name)

    run_docker_compose(
        'up',
        '-d',
        service_name,
    )


def stop_service(service_name: str) -> None:
    _validate_service_name(service_name)

    run_docker_compose(
        'stop',
        service_name,
    )


def restart_service(service_name: str) -> None:
    _validate_service_name(service_name)

    run_docker_compose(
        'restart',
        service_name,
    )


def _validate_service_name(service_name: str) -> None:
    if not service_name.strip():
        raise ValueError('Docker Compose service name cannot be empty.')
