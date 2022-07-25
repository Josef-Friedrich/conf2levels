import re


class ConfigValueError(Exception):
    """Configuration value can’t be found."""


class IniReaderError(Exception):
    """Ini file not valid."""


def validate_key(key: str) -> bool:
    """:param key: Validate the name of a section or a key."""
    if re.match(r"^[a-zA-Z0-9_]+$", key):
        return True
    raise ValueError(
        "The key “{}” contains invalid characters (allowed: a-zA-Z0-9_).".format(key)
    )
