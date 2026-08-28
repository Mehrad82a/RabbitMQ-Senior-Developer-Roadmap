from abc import ABC, abstractmethod
from collections.abc import Mapping




class BaseHandler(ABC):

    """
    Base class for all message handlers.

    Every message handler must implement the process() method.
    This keeps the worker layer independent from the business logic.

    """

    @abstractmethod
    def process(self, task: Mapping[str, object]) -> None:
        pass



