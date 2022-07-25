from abc import ABCMeta, abstractmethod
from typing import Any

from .exceptions import ConfigValueError


class ReaderBase(object, metaclass=ABCMeta):
    """Base class for all readers"""

    def _exception(self, msg: str) -> None:
        """:raises: ConfigValueError"""
        raise ConfigValueError(msg)

    @abstractmethod
    def get(self, section: str, key: str) -> Any:
        raise NotImplementedError("A reader class must have a `get` method.")
