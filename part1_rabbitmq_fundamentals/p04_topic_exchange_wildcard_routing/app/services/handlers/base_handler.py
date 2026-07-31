from abc import ABC, abstractmethod
from typing import Any





class BaseHandler(ABC):
    """
    Base class for all message handlers.

    Every message handler must implement the process() method.
    This keeps the worker layer independent from the business logic.

    """

    @property
    @abstractmethod
    def worker_name(self) -> str:
        """
        Name of the worker.

        Example:
            user
            order
            error
        """
        pass


    @abstractmethod
    def process(self, data: dict[str, Any]) -> dict[str, Any]:
        pass


