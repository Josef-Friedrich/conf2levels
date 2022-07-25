import os
from typing import Any, Optional

from .reader_base import ReaderBase


class EnvironReader(ReaderBase):
    """Read configuration values from environment variables. The name
    of the environment variables have to be in the form `prefix__section__key`.
    Note the two following underscores.

    :param prefix: A enviroment prefix"""

    def __init__(self, prefix: Optional[str] = None):
        self._prefix = prefix

    def get(self, section: str, key: str) -> Any:
        """
        Get a configuration value stored under a section and a key.

        :param section: Name of the section.
        :param key: Name of the key.

        :raises ConfigValueError: Configuration value couldn’t be found.

        :return: The configuration value stored under a section and a key.
        """
        if self._prefix:
            key = "{}__{}__{}".format(self._prefix, section, key)
        else:
            key = "{}__{}".format(section, key)
        if key in os.environ:
            return os.environ[key]
        self._exception("Environment variable not found: {}".format(key))
