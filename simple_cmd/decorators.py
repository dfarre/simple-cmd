import inspect
import string

from simple_cmd import commands


class ErrorsCommand:
    """
    For a simple, fast definition of a CLI entrypoint, from a function,
    the exceptions to handle, and help text
    """

    def __init__(self, *exceptions, help=None, description='', epilog=''):
        self.exceptions = exceptions
        self.help = help or {}
        self.description, self.epilog = description, epilog

    def __call__(self, function):
        parameters = inspect.signature(function).parameters
        option_letters = set()

        class Command(commands.ErrorsCommand):
            arguments = tuple(
                self.argparse_argument_spec(name, param, option_letters)
                for name, param in parameters.items())
            exceptions = self.exceptions
            description = self.description
            epilog = self.epilog

            def try_call(self, *args, **kwargs):
                function(*args, **kwargs)

        return Command()

    def argparse_argument_spec(self, name, param, option_letters):
        kwargs = {'help': [self.help.get(name)] if self.help.get(name) else []}

        if param.kind == param.KEYWORD_ONLY:
            args = ['--' + name.replace('_', '-')]
            letter = self.get_option_letter(name, option_letters)

            if letter is not None:
                args.append(f'-{letter}')
        else:
            args = [name]

        if param.annotation != param.empty:
            if param.kind != param.VAR_POSITIONAL and self.is_list(param.annotation):
                kwargs['nargs'] = '+'
                kwargs['type'] = param.annotation[1]
            elif callable(param.annotation):
                kwargs['type'] = param.annotation
            else:
                kwargs['help'].append(str(param.annotation))

        if param.kind == param.KEYWORD_ONLY:
            kwargs['required'] = param.default == param.empty
        elif param.kind == param.VAR_POSITIONAL:
            kwargs['nargs'] = '*'
        elif param.default != param.empty:
            kwargs.setdefault('nargs', '?')

        if param.default != param.empty:
            if param.default is False:
                kwargs['action'] = 'store_true'
            else:
                kwargs['default'] = param.default

                if param.default is not None:
                    kwargs.setdefault('type', type(param.default))

                    if param.default:
                        kwargs['help'].append(f'Default: {param.default}')

        if not kwargs.get('action') == 'store_true':
            kwargs.setdefault('type', str)

        if kwargs.get('type'):
            kwargs['help'].append(kwargs['type'].__name__)

        kwargs['help'] = '. '.join(reversed(kwargs['help']))

        return args, kwargs

    @staticmethod
    def get_option_letter(name, option_letters):
        available_ascii = set(string.ascii_lowercase) - option_letters
        available_initials = {w[0].lower() for w in name.split('_') if w} & available_ascii
        available_letters = available_initials or available_initials

        if available_letters:
            letter = available_letters.pop()
            option_letters.add(letter)

            return letter

    @staticmethod
    def is_list(annotation):
        return (isinstance(annotation, tuple) and len(annotation) == 2 and
                all(isinstance(a, type) for a in annotation) and
                issubclass(annotation[0], list))
