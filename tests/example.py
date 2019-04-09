import sys

from simple_cmd import commands


class DivideArray(commands.ErrorsCommand):
    arguments = ((('num',), dict(nargs='+', type=int, help='int list')),
                 (('--divide', '-d'), dict(default=1, type=int)))
    exceptions = (ZeroDivisionError,)

    def try_call(self, **kwargs):
        result = [n/kwargs['divide'] for n in kwargs.pop('num')]
        sys.stdout.write(f'{result}\n')

    def finally_call(self, **kwargs):
        sys.stdout.write(f'kwargs={kwargs} Exit {self.last_exit}\n')


if __name__ == '__main__':
    sys.exit(DivideArray()())
