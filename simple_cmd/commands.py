import abc
import argparse
import sys


class Command(metaclass=abc.ABCMeta):
    arguments = ()

    def __init__(self, test_mode=False):
        if not test_mode:
            self.parser = argparse.ArgumentParser()

            for args, kwargs in self.arguments:
                self.parser.add_argument(*args, **kwargs)

        self.test_mode = test_mode
        self.last_exit = 0

    def __call__(self, **kwargs):
        items = (kwargs.items() if self.test_mode else
                 self.parser.parse_args()._get_kwargs())

        return self.call(**{key: value for key, value in items if value is not None})

    @abc.abstractmethod
    def call(self, **kwargs):
        """The command function"""


class ErrorsCommand(Command, metaclass=abc.ABCMeta):
    exceptions = ()

    @abc.abstractmethod
    def try_call(self, **kwargs):
        f"""May raise {self.exceptions}"""

    def finally_call(self, **kwargs):
        """Final clean up"""

    def call(self, **kwargs):
        try:
            self.try_call(**kwargs)
            return 0
        except self.exceptions as error:
            sys.stderr.write(f'{error.__class__.__name__}: {error}\n')
            self.last_exit = 1
            return 1
        finally:
            self.finally_call(**kwargs)
