.. image:: http://img.shields.io/pypi/v/conf2levels.svg
    :target: https://pypi.org/project/conf2levels
    :alt: This package on the Python Package Index

.. image:: https://github.com/Josef-Friedrich/conf2levels/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/Josef-Friedrich/conf2levels/actions/workflows/tests.yml
    :alt: Tests

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


.. code:: python

    CONF_DEFAULTS = {
        'email': {
            'subject_prefix': 'command_watcher',
        },
        'nsca': {
            'port': 5667,
        },
    }

    CONFIG_READER_SPEC: Spec = {
        'email': {
            'from_addr': {
                'description': 'The email address of the sender.',
            },
            'to_addr': {
                'description': 'The email address of the recipient.',
                'not_empty': True,
            },
            'to_addr_critical': {
                'description': 'The email address of the recipient to send '
                              'critical messages to.',
                'default': None,
            },
            'smtp_login': {
                'description': 'The SMTP login name.',
                'not_empty': True,
            },
            'smtp_password': {
                'description': 'The SMTP password.',
                'not_empty': True,
            },
            'smtp_server': {
                'description': 'The URL of the SMTP server, for example: '
                              '`smtp.example.com:587`.',
                'not_empty': True,
            },
        },
        'icinga': {
            'url': {
                'description': 'The HTTP URL. /v1/actions/process-check-result '
                              'is appended.',
                'not_empty': True,
            },
            'user': {
                'description': 'The user for the HTTP authentification.',
                'not_empty': True,
            },
            'password': {
                'description': 'The password for the HTTP authentification.',
                'not_empty': True,
            },
        },
        'beep': {
            'activated': {
                'description': 'Activate the beep channel to report auditive '
                              'messages.',
                'default': False,
            }
        }
    }

    config_reader = ConfigReader(
        spec=CONFIG_READER_SPEC,
        ini=config_file,
        dictionary=CONF_DEFAULTS,
    )
