A configuration reader which reads values stored in two key levels.
The first key level is named ``section`` and the second level ``key``.

argparse arguments (`argparse`): (You have to specify a mapping)

.. code:: python

    mapping = {
        'section.key': 'args_attribute'
    }

A python dictionary (`dictonary`):

.. code:: python

    {
        'section':  {
            'key': 'value'
        }
    }

Environment variables (`environ`):

.. code:: shell

    export prefix__section__key=value

INI file (`ini`):

.. code:: ini

    [section]
    key = value
