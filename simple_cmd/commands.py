import abc
import argparse
import sys


class ArgumentParser(argparse.ArgumentParser):
    def add_argument_group(self, title, *args, **kwargs):
        if title == 'optional arguments':
            title = 'keyword arguments'

        return super().add_argument_group(title, *args, **kwargs)


class Command(metaclass=abc.ABCMeta):
    arguments, description, epilog = (), '', ''

    def __init__(self):
        self.parser = ArgumentParser(description=self.description, epilog=self.epilog)
        self.positional_args, self.asterisk_arg = [], None

        for args, kwargs in self.arguments:
            action = self.parser.add_argument(*args, **kwargs)

            if not action.option_strings:
                if action.nargs in ['*', '+']:
                    self.asterisk_arg = action.dest
                else:
                    self.positional_args.append(action.dest)

    def __call__(self):
        kw = dict(self.parser.parse_args()._get_kwargs())
        args = [kw.pop(n) for n in self.positional_args] + kw.pop(self.asterisk_arg, [])

        return self.call(*args, **kw)

    @abc.abstractmethod
    def call(self, *args, **kwargs):
        """The command function, should return the exit status"""


class ErrorsCommand(Command, metaclass=abc.ABCMeta):
    exceptions = ()

    @abc.abstractmethod
    def try_call(self, *args, **kwargs):
        """May raise `self.exceptions`. The `n`th exception type produces exit status `n`"""

    def call(self, *args, **kwargs):
        try:
            self.try_call(*args, **kwargs)
            return 0
        except self.exceptions as error:
            sys.stderr.write(f'{error.__class__.__name__}: {error}\n')
            return self.exceptions.index(error.__class__) + 3  # Exit 2 -> argparse error
