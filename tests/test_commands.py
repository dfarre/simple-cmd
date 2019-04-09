import subprocess
import unittest
import unittest.mock as mock

from . import example


class CommandsUnitTests(unittest.TestCase):
    command = example.DivideArray(test_mode=True)

    @mock.patch('sys.stdout.write')
    def test_ok(self, stdout_mock):
        assert self.command(num=[3, 9], divide=3) == 0
        assert stdout_mock.call_args_list == [mock.call('[1.0, 3.0]\n'), mock.call(
            "kwargs={'num': [3, 9], 'divide': 3} Exit 0\n")]

    @mock.patch('sys.stdout.write')
    @mock.patch('sys.stderr.write')
    def test_raised(self, stderr_mock, stdout_mock):
        assert self.command(num=[3], divide=0) == 1
        stderr_mock.assert_called_once_with('ZeroDivisionError: division by zero\n')
        stdout_mock.assert_called_once_with("kwargs={'num': [3], 'divide': 0} Exit 1\n")


class CommandsE2ETests(unittest.TestCase):
    def call(self, args):
        return subprocess.run(['python', '-m', 'tests.example'] + args,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_args_handling(self):
        process = self.call(['5', '7'])

        assert process.returncode == 0
        assert process.stderr.decode() == ''
        assert process.stdout.decode() == (
            "[5.0, 7.0]\nkwargs={'divide': 1, 'num': [5, 7]} Exit 0\n")

    def test_raises(self):
        process = self.call(['2', '4', '-d', '0'])

        assert process.returncode == 1
        assert process.stderr.decode() == 'ZeroDivisionError: division by zero\n'
        assert process.stdout.decode() == "kwargs={'divide': 0, 'num': [2, 4]} Exit 1\n"

    def test_no_arg(self):
        process = self.call([])

        assert process.returncode == 2
        assert process.stderr.decode() == (
            'usage: example.py [-h] [--divide DIVIDE] num [num ...]\n'
            'example.py: error: the following arguments are required: num\n')
        assert process.stdout.decode() == ''
