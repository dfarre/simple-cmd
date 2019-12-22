import cmath
import sys

from simple_cmd import decorators


class DimensionMismatchError(Exception):
    """"""


@decorators.ErrorsCommand(DimensionMismatchError, ZeroDivisionError, help={
    'name': 'Give this name to the result', 'polar': '<Extra help for the CLI>'
}, description='Computes a+(v|w)/b', epilog='<Epilog text>')
def scalar_product(a: float, b=1.0, *v: complex, w: (list, complex), name='result',
                   polar: 'Return in polar form'=False):
    if len(v) != len(w):
        raise DimensionMismatchError('Vectors should have the same dimension')

    if a == 3.14:
        raise ValueError('Fake unhandled error')

    result = a + sum(x*y.conjugate() for x, y in zip(v, w))/b
    out = cmath.polar(result) if polar else result
    sys.stdout.write(f'{name} = {a} + {v}x{w}/{b} = {out}\n')


if __name__ == '__main__':
    sys.exit(scalar_product())
