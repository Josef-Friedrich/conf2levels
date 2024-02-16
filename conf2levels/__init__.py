import argparse
import ast
from importlib import metadata
from typing import Any, List, Tuple, TypedDict, Union

from typing_extensions import Unpack

from .argparse_reader import ArgparseReader
from .dictonary_reader import DictionaryReader
from .environ_reader import EnvironReader
from .exceptions import ConfigValueError, validate_key
from .ini_reader import IniReader
from .reader_base import ReaderBase
from .spec_reader import SpecReader
from .types import Dictionary, Mapping, Spec

__version__: str = metadata.version("conf2levels")


class ReaderSelector(ReaderBase):
    """Select for each get request which reader to use."""

    def __init__(self, *readers: ReaderBase):
        self.readers = readers
        """A list of readers."""

    @staticmethod
    def _validate_key(key: str) -> bool:
        return validate_key(key)

    def get(self, section: str, key: str) -> Any:
        """
        Get a configuration value stored under a section and a key.

        :param section: Name of the section.
        :param key: Name of the key.
        """
        self._validate_key(section)
        self._validate_key(key)
        for reader in self.readers:
            try:
                return reader.get(section, key)
            except ConfigValueError:
                pass
        raise ValueError(
            "Configuration value could not be found " "(section “{}” key “{}”).".format(
                section, key
            )
        )


def auto_type(value: Any) -> Any:
    """https://stackoverflow.com/a/7019325"""
    try:
        return ast.literal_eval(value)
    except ValueError:
        return value
    # ERROR: test_method_send_email_with_config_reader
    # (test_command_watcher.TestClassWatch)
    # AttributeError: 'SyntaxError' object has no attribute 'filename'
    except SyntaxError:
        return value


class DictionaryInterfaceKey:
    def __init__(self, reader: ReaderBase, section: str):
        self._reader = reader
        self._section = section

    def __getitem__(self, name: str) -> Any:
        return auto_type(self._reader.get(self._section, name))


class DictionaryInterface:
    def __init__(self, reader: ReaderBase):
        self._reader = reader

    def __getitem__(self, name: str) -> DictionaryInterfaceKey:
        return DictionaryInterfaceKey(self._reader, section=name)


class ClassInterfaceKey:
    def __init__(self, reader: ReaderBase, section: str):
        self._reader = reader
        self._section = section

    def __getattr__(self, name: str) -> Any:
        return auto_type(self._reader.get(self._section, name))


class ClassInterface:
    def __init__(self, reader: ReaderBase):
        self._reader = reader

    def __getattr__(self, name: str) -> ClassInterfaceKey:
        return ClassInterfaceKey(self._reader, section=name)


class ReadersKwarg(TypedDict, total=False):
    argparse: Union[Tuple[argparse.Namespace, Mapping], argparse.Namespace]
    """A tuple `(args, mapping)`.
      `args`: The parsed `argparse` object (Namespace).
      `mapping`: A dictionary like this one: `{'section.key': 'dest'}`. `dest`
      are the propertiy name of the `args` object.
      or only the `argparse` object (Namespace)."""

    dictionary: Dictionary
    """ A two dimensional nested dictionary
      `{'section': {'key': 'value'}}`"""

    environ: str
    """The prefix of the environment variables."""

    ini: str
    """The path of the INI file."""

    spec: Spec


def load_readers_by_keyword(**kwargs: Unpack[ReadersKwarg]) -> List[ReaderBase]:
    """Available readers: `argparse`, `dictionary`, `environ`, `ini`.

    The arguments of this class have to be specified as keyword arguments.
    Each keyword stands for a configuration reader class.
    The order of the keywords is important. The first keyword, more
    specifically the first reader class, overwrites the next ones.
    """
    readers: List[ReaderBase] = []
    for keyword, value in kwargs.items():
        if keyword == "argparse":
            if isinstance(value, tuple) or isinstance(value, list):
                readers.append(ArgparseReader(args=value[0], mapping=value[1]))
            elif value.__class__.__name__ == "Namespace":
                readers.append(ArgparseReader(args=value))
        elif keyword == "dictionary" and isinstance(value, dict):
            readers.append(DictionaryReader(dictionary=value))
        elif keyword == "environ" and isinstance(value, str):
            readers.append(EnvironReader(prefix=value))
        elif keyword == "ini" and isinstance(value, str):
            readers.append(IniReader(path=value))
        elif keyword == "spec":
            readers.append(SpecReader(spec=value))
    return readers


class ConfigReader:
    """Available readers: `argparse`, `dictionary`, `environ`, `ini`.

    The arguments of this class have to be specified as keyword arguments.
    Each keyword stands for a configuration reader class.
    The order of the keywords is important. The first keyword, more
    specifically the first reader class, overwrites the next ones.
    """

    spec: Spec
    reader: ReaderBase

    def __init__(self, spec: Spec = {}, **kwargs: Unpack[ReadersKwarg]):
        kwargs["spec"] = spec

        readers = load_readers_by_keyword(**kwargs)
        self.spec = spec
        """The specification dictionary. For more informations look at the
        class arguments of this class."""

        self.reader = ReaderSelector(*readers)
        """:py:class:`ReaderSelector`"""

    def get_class_interface(self) -> ClassInterface:
        return ClassInterface(self.reader)

    def get_dictionary_interface(self) -> DictionaryInterface:
        return DictionaryInterface(self.reader)

    def check_section(self, section: str, not_empty: bool = False) -> bool:
        """Check all keys of a section.

        :raises ValueError: If the value is not configured and can not be
          read by the readers.
        :raises ValueError: If `not_empty` is true and value is empty.
        :raises KeyError: By an unspecify section
        """
        for key, value_spec in self.spec[section].items():
            value = self.reader.get(section, key)
            if "not_empty" in value_spec and value_spec["not_empty"] and not value:
                raise ValueError(
                    "Spec check: section ”{}” key “{}” is empty.".format(section, key)
                )
        return True

    def spec_to_argparse(self, parser: argparse.ArgumentParser) -> None:
        for section, _ in self.spec.items():
            group = parser.add_argument_group(
                title=section, description="Generated by the config_reader."
            )
            for key, value in self.spec[section].items():
                argument = "--{}-{}".format(section, key).replace("_", "-")
                kwargs = {}
                if "description" in value:
                    kwargs["help"] = value["description"]
                if "default" in value:
                    kwargs["default"] = value["default"]
                group.add_argument(argument, **kwargs)
