import cmath
import sys

from simple_cmd import decorators


class DimensionMismatchError(Exception):
    """"""


@decorators.ErrorsCommand(DimensionMismatchError, ZeroDivisionError, help={
    'result': 'Name to give to the result', 'polar': '<Extra help for the CLI>'},
    shorthands={'result': 'n'}, overrides={'lcoord': {'nargs': '+'}},
    description='Computes a+(v|w)/b', epilog='<Epilog text>')
def scalar_product(a: float, b=1.0, *lcoord: complex, rcoord: (list, complex), result='result',
                   polar: 'Return in polar form' = False):
    if len(lcoord) != len(rcoord):
        raise DimensionMismatchError('Vectors should have the same dimension')

    if a == 3.14:
        raise ValueError('Fake unhandled error')

    value = a + sum(x*y.conjugate() for x, y in zip(lcoord, rcoord))/b
    out = cmath.polar(value) if polar else value
    sys.stdout.write(f'{result} = {a} + {lcoord}x{rcoord}/{b} = {out}\n')


if __name__ == '__main__':
    sys.exit(scalar_product())
