import unittest

from simple_cmd import decorators


class ShortFormTests(unittest.TestCase):
    def test(self):
        names = ['a', 'b', 'pre_suf', 'pre_sof', 'pre_sif_salt', 'woo', 'pre_sin']
        parameter_names = set(names)
        shorthands = [decorators.ErrorsCommand.get_short_form(name, parameter_names)
                      for name in names[2:]]

        assert shorthands == ['p', 'ps', 'pss', 'w', 'c']
