import argparse
import sys


class ArgumentParser(argparse.ArgumentParser):
    def add_argument_group(self, title, *args, **kwargs):
        if title == 'optional arguments':
            title = 'keyword arguments'

        return super().add_argument_group(title, *args, **kwargs)


class Command:
    def __init__(self, function, *arguments, exceptions=(), **parser_kwargs):
        self.function = function
        self.exceptions = exceptions
        self.parser = ArgumentParser(**parser_kwargs)
        self.positional_args, self.asterisk_arg = [], None

        for args, kwargs in arguments:
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

    def call(self, *args, **kwargs):
        try:
            self.function(*args, **kwargs)
            return 0
        except self.exceptions as error:
            sys.stderr.write(f'{error.__class__.__name__}: {error}\n')
            return self.find_exception_index(error) + 3  # Exit 2 -> argparse error

    def find_exception_index(self, captured_exc):
        for i, exc_type in enumerate(self.exceptions):
            if isinstance(captured_exc, exc_type):
                return i
