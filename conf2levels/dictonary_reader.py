from typing import Any

from .reader_base import ReaderBase
from .types import Dictionary


class DictionaryReader(ReaderBase):
    """Useful for default values."""

    def __init__(self, dictionary: Dictionary):
        self._dictionary = dictionary

    def get(self, section: str, key: str) -> Any:
        """
        Get a configuration value stored under a section and a key.

        :param section: Name of the section.
        :param key: Name of the key.

        :raises ConfigValueError: Configuration value couldn’t be found.

        :return: The configuration value stored under a section and a key.
        """
        try:
            return self._dictionary[section][key]
        except KeyError:
            self._exception(
                "In the dictionary is no value at dict[{}][{}]".format(section, key)
            )
