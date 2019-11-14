import os
from argparse import (ArgumentParser, _StoreAction, _CountAction,
                      _StoreConstAction)


class EnvArgParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_argument(self, *args, env_var=None, **kwargs):
        action = super().add_argument(*args, **kwargs)
        names = [s for s in action.option_strings if s.startswith('--')]
        if names and env_var is None:
            env_var = names[0].replace('--', '').upper().replace('-', '_')
        action._env_var = env_var
        return action

    def parse_args(self, args, namespace=None, prefix='',
                   env=os.environ):
        for action in self._actions:
            if env is None or any([s in args for s in action.option_strings]):
                continue
            env_var = getattr(action, '_env_var')
            if not env_var or not env.get(f'{prefix}{env_var}'):
                continue
            value = str(env.get(f'{prefix}{env_var}'))
            if isinstance(action, _StoreAction) and action.nargs:
                args += [action.option_strings[0],
                         *value.replace(',', ' ').split()]
            elif isinstance(action, _StoreAction):
                args += [action.option_strings[0], value]
            elif isinstance(action, _CountAction):
                for arg in args:
                    if any([arg.startswith(s) for s in action.option_strings]):
                        value = 0
                args += [action.option_strings[0]] * int(value)
            elif isinstance(action, _StoreConstAction):
                args += [action.option_strings[0]]
            # XXX todo add _AppendAction _AppendConstAction,
        return super().parse_args(args, namespace=namespace)