from typing import Any, Dict, TypedDict

Mapping = Dict[str, str]
"""A dictionary like this one: `{'section.key': 'dest'}`.
      `dest` is the property name of the `args` object."""


class KeySpec(TypedDict, total=False):
    description: str
    default: Any
    not_empty: bool


Spec = Dict[str, Dict[str, KeySpec]]
"""A dictionary like this example:

.. code:: python

    spec = {
        'section_1': {
            'key_1': {
                'description': 'Lorem ipsum',
                'default': 123,
                'not_empty': True,
            }
        }
    }
"""


Dictionary = Dict[str, Dict[str, Any]]
