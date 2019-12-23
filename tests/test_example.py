import subprocess
import unittest


class CommandsE2ETestCase(unittest.TestCase):
    module = ''

    def call(self, *args):
        return subprocess.run(('python3', '-m', self.module) + args,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class FunctionCommandTests(CommandsE2ETestCase):
    module = 'tests.example'

    def test_help(self):
        process = self.call('--help')

        assert process.returncode == 0
        assert process.stdout.decode() == """
usage: example.py [-h] --rcoord RCOORD [RCOORD ...] [--result RESULT]
                  [--polar]
                  a [b] lcoord [lcoord ...]

Computes a+(v|w)/b

positional arguments:
  a                     float
  b                     float. Default: 1.0
  lcoord                complex

keyword arguments:
  -h, --help            show this help message and exit
  --rcoord RCOORD [RCOORD ...], -r RCOORD [RCOORD ...]
                        complex
  --result RESULT, -n RESULT
                        str. Default: result. Name to give to the result
  --polar, -p           Return in polar form. <Extra help for the CLI>

<Epilog text>
""".lstrip()

    def test_ok(self):
        process = self.call('1', '1', '3', '4', '-r', '3', '-4', '--polar', '-n', 'R')

        assert process.returncode == 0
        assert process.stderr.decode() == ''
        assert process.stdout.decode() == (
            'R = 1.0 + ((3+0j), (4+0j))x[(3+0j), (-4+0j)]/1.0 = (6.0, 3.141592653589793)\n')

    def test_raises__unhandled(self):
        process = self.call('3.14', '-9', '3', '4', '-r', '3', '-4')
        stderr = process.stderr.decode()

        assert process.returncode == 1
        assert stderr.startswith('Traceback (most recent call last):\n')
        assert stderr.endswith('ValueError: Fake unhandled error\n')
        assert process.stdout.decode() == ''

    def test_raises__parser_error(self):
        process = self.call('1', '0', '3', '4i', '-r', '3', '-4')

        assert process.returncode == 2
        assert process.stderr.decode() == """
usage: example.py [-h] --rcoord RCOORD [RCOORD ...] [--result RESULT]
                  [--polar]
                  a [b] lcoord [lcoord ...]
example.py: error: argument lcoord: invalid complex value: '4i'
""".lstrip()
        assert process.stdout.decode() == ''

    def test_raises__dimension_mismatch(self):
        process = self.call('1', '0', '-3', '2j', '-r', '3')

        assert process.returncode == 3
        assert process.stderr.decode() == (
            'DimensionMismatchError: Vectors should have the same dimension\n')
        assert process.stdout.decode() == ''

    def test_raises__zero_division(self):
        process = self.call('1', '0', '3', '4', '-r', '3', '-4')

        assert process.returncode == 4
        assert process.stderr.decode() == 'ZeroDivisionError: complex division by zero\n'
        assert process.stdout.decode() == ''
