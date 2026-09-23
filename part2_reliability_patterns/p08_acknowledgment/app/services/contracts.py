from collections.abc import Mapping
from typing import Protocol


class TaskProcess(Protocol):
    """
    Contract for task-specific business logic.

    This allows TaskHandler to receive either implementation
    through dependency injection.
    """
    def execute(self, task: Mapping[str, object]) -> dict[str, object]:
        """
        Execute the task business logic and return the processing result.
        """



