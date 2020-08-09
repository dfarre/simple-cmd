import argparse
import sys


class ArgumentParser(argparse.ArgumentParser):
    def add_argument_group(self, title, *args, **kwargs):
        if title == 'optional arguments':
            title = 'keyword arguments'

        return super().add_argument_group(title, *args, **kwargs)


class Command:
    def __init__(self, function, *arguments, exceptions=(),
                 error_hook=lambda exc, *args, **kwargs: None, **parser_kwargs):
        self.function = function
        self.exceptions = exceptions
        self.error_hook = error_hook
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
        except self.exceptions as error:
            self.error_hook(error, *args, **kwargs)
            sys.stderr.write(f'{error.__class__.__name__}: {error}\n')

            return self.exceptions.index(error.__class__) + 3  # Exit 2 -> argparse error
        except Exception as exception:
            self.error_hook(exception, *args, **kwargs)

            raise exception
        else:
            return 0
