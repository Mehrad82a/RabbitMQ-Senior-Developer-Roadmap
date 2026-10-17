from collections.abc import Callable

import pytest



@pytest.fixture
def task_factory() -> Callable[..., dict[str, object]]:
    """
    Return a factory for creating valid task payloads.
    """

    def build_task(
        *,
        task_id: object = 'task-123',
        task_name: object = 'generate-report',
        created_at: object = '2026-10-17T10:00:00+00:00',
        **overrides: object,
    ) -> dict[str, object]:
        return {
            'task_id': task_id,
            'task_name': task_name,
            'created_at': created_at,
            **overrides,
        }

    return build_task