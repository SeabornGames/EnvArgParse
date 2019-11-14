EnvArgParser
============

This subclasses python's argparse to automatically add the environmental
variables to the list of the args.


add_argument
------------
The method add_argument adds the ``env_var`` option to change the default name
of the environmental variable from the uppercase verion of the option string
to this value.


parse_args
----------
The method parse_args adds the ``prefix`` and ``env`` variable.

The ``prefix`` appends this name to the ``env_var`` when searching for the name
in the environment variables.

The ``env`` is a dict whic defaults to the environmental variables which is
used to lookup values to append to the args list.  If this value is None then no
values will be append to the args.

Install
-------
Ensure you have python 3.6 or better.

To create a private virtual environment use the following command:
>> python3.6 -m venv --clear ./venv
>> ./venv/bin/pip install .


