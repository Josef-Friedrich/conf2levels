import os
from configparser import ConfigParser
from typing import Any

from .exceptions import IniReaderError
from .reader_base import ReaderBase


class IniReader(ReaderBase):
    """Read configuration files from text files in the INI format.

    :param path: The path of the INI file.
    """

    def __init__(self, path: str):
        self._config = ConfigParser()
        if not path or not os.path.exists(path):
            raise IniReaderError(
                "Ini configuration path “{}” couldn’t be opened.".format(path)
            )
        self._config.read_file(open(path))

    def get(self, section: str, key: str) -> Any:
        """
        Get a configuration value stored under a section and a key.

        :param section: Name of the section.
        :param key: Name of the key.

        :raises ConfigValueError: Configuration value couldn’t be found.

        :return: The configuration value stored under a section and a key.
        """
        try:
            return self._config[section][key]
        except KeyError:
            self._exception(
                "Configuration value could not be found "
                "(section “{}” key “{}”).".format(section, key)
            )
