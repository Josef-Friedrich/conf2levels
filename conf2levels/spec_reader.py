from typing import Any

from .reader_base import ReaderBase
from .types import Spec


class SpecReader(ReaderBase):
    """Read the default values from the `spec` (specification) dictionary."""

    _spec: Spec

    def __init__(self, spec: Spec):
        self._spec = spec

    def get(self, section: str, key: str) -> Any:
        """
        Get a configuration value stored under a section and a key.

        :param section: Name of the section.
        :param key: Name of the key.

        :raises ConfigValueError: Configuration value couldn’t be found.

        :return: The configuration value stored under a section and a key.
        """
        try:
            return self._spec[section][key]["default"]
        except KeyError:
            self._exception(
                "Configuration value could not be found "
                "(section “{}” key “{}”).".format(section, key)
            )
