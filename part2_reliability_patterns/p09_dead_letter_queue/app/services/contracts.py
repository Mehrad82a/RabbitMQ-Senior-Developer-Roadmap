from collections.abc import Mapping
from typing import Protocol



class TaskProcessor(Protocol):
    """
    Contract for task processing implementations.
    """


    def execute(self, task: Mapping[str, object]) -> dict[str, object]:
        """
        Process a task and return its result.
        """
        ...




