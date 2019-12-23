import inspect
import string

from simple_cmd import commands


class ErrorsCommand:
    """
    For a simple, fast definition of a CLI entrypoint from a function,
    the exceptions to handle, extra help text for arguments, argument shorthands,
    and extra kwargs for the `ArgumentParser` constructor
    """

    def __init__(self, *exceptions, help=None, shorthands=None, overrides=None,
                 **parser_kwargs):
        self.exceptions = exceptions
        self.help = help or {}
        self.shorthands = shorthands or {}
        self.overrides = overrides or {}
        self.parser_kwargs = parser_kwargs

    def __call__(self, function):
        parameters = inspect.signature(function).parameters
        taken_strings = set(parameters) | set(self.shorthands.values())
        arguments = ((self.get_argument_strings(name, param, taken_strings),
                      self.get_argument_kwargs(name, param))
                     for name, param in parameters.items())

        return commands.Command(function, *arguments, exceptions=self.exceptions,
                                **self.parser_kwargs)

    def get_argument_strings(self, name, param, taken_strings):
        if param.kind == param.KEYWORD_ONLY:
            args = ['--' + name.replace('_', '-')]
            shorthand = self.shorthands.get(name) or self.get_short_form(name, taken_strings)

            if shorthand is not None:
                args.append(f'-{shorthand}')
        else:
            args = [name]

        return args

    def get_argument_kwargs(self, name, param):
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
            if param.default is False and param.kind == param.KEYWORD_ONLY:
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

        if name in self.overrides:
            kwargs.update(self.overrides[name])

        return kwargs

    @staticmethod
    def get_short_form(name, taken_strings):
        words = [w.lower() for w in name.split('_') if w]

        for candidate in (''.join([w[0] for w in words[:i]]) for i in range(1, len(words)+1)):
            if candidate not in taken_strings:
                shorthand = candidate
                break
        else:
            available_ascii = sorted(
                set(string.ascii_lowercase) - taken_strings, reverse=True)
            shorthand = available_ascii.pop() if available_ascii else None

        if shorthand is not None:
            taken_strings.add(shorthand)
            return shorthand

    @staticmethod
    def is_list(annotation):
        return (isinstance(annotation, tuple) and len(annotation) == 2 and
                all(isinstance(a, type) for a in annotation) and
                issubclass(annotation[0], list))
