import inspect

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
        class Command(commands.ErrorsCommand):
            arguments = tuple(
                self.argparse_argument_spec(name, param)
                for name, param in inspect.signature(function).parameters.items())
            exceptions = self.exceptions
            description = self.description
            epilog = self.epilog

            def try_call(self, *args, **kwargs):
                function(*args, **kwargs)

        return Command()

    def argparse_argument_spec(self, name, param):
        args = ('--' if param.kind == param.KEYWORD_ONLY else '') + name,
        kwargs = {'help': [self.help.get(name)] if self.help.get(name) else []}

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

        if kwargs.get('type'):
            kwargs['help'].append(kwargs['type'].__name__)

        kwargs['help'] = '. '.join(reversed(kwargs['help']))

        return args, kwargs

    @staticmethod
    def is_list(annotation):
        return (isinstance(annotation, tuple) and len(annotation) == 2 and
                all(isinstance(a, type) for a in annotation) and
                issubclass(annotation[0], list))
