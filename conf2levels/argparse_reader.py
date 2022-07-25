from argparse import Namespace
from typing import Any

from .reader_base import ReaderBase
from .types import Mapping


class ArgparseReader(ReaderBase):
    """This class tries to read configuration values from a `argparse`
    namespace object. This works fine if your section is one word long
    (`--section-key` = `args.section_key` = `section` + `key`) and not more
    than one word long (`--my-section-key` = `args.my_section_key` = `my` +
    `section_key`). By multi word section you have to specify a mapping
    (`{'my_section.key': 'my_section_key'}`). Without a mapping all sections
    and keys are convert into lowercase (`Section` = `section`).
    """

    _mapping: Mapping

    def __init__(self, args: Namespace, mapping: Mapping = {}):
        self._args = args
        self._mapping = mapping

    def get(self, section: str, key: str) -> Any:
        """
        Get a configuration value stored under a section and a key.

        :param section: Name of the section.
        :param key: Name of the key.

        :raises ConfigValueError: Configuration value couldn’t be found.

        :return: The configuration value stored under a section and a key.
        """
        mapping_key = "{}.{}".format(section, key)
        if mapping_key in self._mapping:
            argparse_dest = self._mapping[mapping_key]
        else:
            argparse_dest = "{}_{}".format(section, key).lower()

        if hasattr(self._args, argparse_dest):
            value = getattr(self._args, argparse_dest)
            if value is not None:
                return value

        self._exception(
            "Configuration value could not be found by "
            "Argparse (section “{}” key “{}”).".format(section, key)
        )
