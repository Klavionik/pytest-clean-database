from typing import Any
import abc


class Connection(abc.ABC):
    @abc.abstractmethod
    def execute(self, query: str, *args: Any, **kwargs: Any) -> Any:
        pass
