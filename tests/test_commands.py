import subprocess
import unittest


class CommandsE2ETestCase(unittest.TestCase):
    module = ''

    def call(self, *args):
        return subprocess.run(('python3', '-m', self.module) + args,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class ClassCommandTests(CommandsE2ETestCase):
    module = 'tests.class_example'

    def test_args_handling(self):
        process = self.call('5', '7')

        assert process.returncode == 0
        assert process.stderr.decode() == ''
        assert process.stdout.decode() == '[5.0, 7.0]\n'

    def test_raises(self):
        process = self.call('2', '4', '-d', '0')

        assert process.returncode == 3
        assert process.stderr.decode() == 'ZeroDivisionError: division by zero\n'
        assert process.stdout.decode() == ''

    def test_no_arg(self):
        process = self.call()

        assert process.returncode == 2
        assert process.stderr.decode() == (
            'usage: class_example.py [-h] [--divide DIVIDE] num [num ...]\n'
            'class_example.py: error: the following arguments are required: num\n')
        assert process.stdout.decode() == ''


class FunctionCommandTests(CommandsE2ETestCase):
    module = 'tests.function_example'

    def test_help(self):
        process = self.call('--help')

        assert process.returncode == 0
        assert process.stdout.decode() == """
usage: function_example.py [-h] --rcoord RCOORD [RCOORD ...] [--name NAME]
                           [--polar]
                           a [b] [lcoord [lcoord ...]]

Computes a+(v|w)/b

positional arguments:
  a                     float
  b                     float. Default: 1.0
  lcoord                complex

keyword arguments:
  -h, --help            show this help message and exit
  --rcoord RCOORD [RCOORD ...], -r RCOORD [RCOORD ...]
                        complex
  --name NAME, -n NAME  str. Default: result. Give this name to the result
  --polar, -p           Return in polar form. <Extra help for the CLI>

<Epilog text>
""".lstrip()

    def test_ok(self):
        process = self.call('1', '1', '3', '4', '-r', '3', '-4', '--polar', '--name', 'R')

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
usage: function_example.py [-h] --rcoord RCOORD [RCOORD ...] [--name NAME]
                           [--polar]
                           a [b] [lcoord [lcoord ...]]
function_example.py: error: argument lcoord: invalid complex value: '4i'
""".lstrip()
        assert process.stdout.decode() == ''

    def test_raises__dimension_mismatch(self):
        process = self.call('1', '0', '-r', '3')

        assert process.returncode == 3
        assert process.stderr.decode() == (
            'DimensionMismatchError: Vectors should have the same dimension\n')
        assert process.stdout.decode() == ''

    def test_raises__zero_division(self):
        process = self.call('1', '0', '3', '4', '-r', '3', '-4')

        assert process.returncode == 4
        assert process.stderr.decode() == 'ZeroDivisionError: complex division by zero\n'
        assert process.stdout.decode() == ''
