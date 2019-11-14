import unittest
from unittest.mock import patch

from argparse import Namespace

from env_argparse import EnvArgumentParse


class ParserError(Exception):
    pass


class _EnvArgumentParse(EnvArgumentParse):
    def error(self, msg):
        self._test_err_msg = msg
        raise ParserError(msg)

    def exit(self):
        return


class TestEnvArgParser(unittest.TestCase):
    def test_adds_env_automatically(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--test-arg')
        args = parser.parse_args(args=[], env={'TEST_ARG': '!!!'})
        self.assertEqual(args, Namespace(test_arg='!!!'))

    def test_auto_env_vars_can_be_disabled(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--test-arg')
        args = parser.parse_args(args=[], env=None)
        self.assertEqual(args, Namespace(test_arg=None))

    def test_can_override_default_env_var(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--test-arg', env_var='ARG_TEST', default=3)
        args = parser.parse_args(args=[], env={'ARG_TEST': '!!!'})
        self.assertEqual(args, Namespace(test_arg='!!!'))

    def test_adds_prefixed_env_automatically(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--test-arg')
        args = parser.parse_args(args=[], env={'XXX_TEST_ARG': '!!!'},
                                 prefix='XXX_')
        self.assertEqual(args, Namespace(test_arg='!!!'))

    def test_setting_env_var_works_with_required_attribute(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--test-arg', env_var='TEST_ARG', required=True)
        args = parser.parse_args(args=[], env={'TEST_ARG': '!!!'})
        self.assertEqual(args, Namespace(test_arg='!!!'))

    def test_returns_error_if_env_var_is_missing_and_has_no_default(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--test-arg', required=True)
        parser.add_argument('--test-other-arg')
        parser.add_argument('--test-another-arg', default=5)

        with self.assertRaises(Exception):
            parser.parse_args(args=[], env={})

        self.assertEqual(parser._test_err_msg,
                         'The following arguments are missing:'
                         ' --test-arg/env:TEST_ARG,'
                         ' --test-other-arg/env:TEST_OTHER_ARG')

    def test_parses_from_os_environ_by_default(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--test-arg', env_var='TEST_ARG')
        with patch.dict('os.environ', {'TEST_ARG': '!!!'}):
            args = parser.parse_args(args=[])
        self.assertEqual(args, Namespace(test_arg='!!!'))

    def test_argument_with_type(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--test-arg', type=int)

        args = parser.parse_args(args=['--test-arg', '1'])
        self.assertEqual(args, Namespace(test_arg=1))

        with self.assertRaises(ParserError) as ctx:
            parser.parse_args(args=['--test-arg', 'NOTANUMBER'], env={})
        self.assertEqual(str(ctx.exception),
                         "argument --test-arg: invalid int value:"
                         " 'NOTANUMBER'")

        args = parser.parse_args(args=[], env={'TEST_ARG': '1'})
        self.assertEqual(args, Namespace(test_arg=1))

        with self.assertRaises(ParserError) as ctx:
            parser.parse_args(args=[], env={'TEST_ARG': 'NOTANUMBER'})
        self.assertEqual(str(ctx.exception),
                         "argument --test-arg: invalid int value:"
                         " 'NOTANUMBER'")

    def test_argument_with_type_and_choices(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--test-arg', type=int, choices=(1, 2, 3))

        args = parser.parse_args(args=['--test-arg', '1'], env={})
        self.assertEqual(args, Namespace(test_arg=1))

        with self.assertRaises(ParserError) as ctx:
            parser.parse_args(args=['--test-arg', '42'], env={})
        self.assertEqual(str(ctx.exception),
                         'argument --test-arg: invalid choice: 42 '
                         '(choose from 1, 2, 3)')

        args = parser.parse_args(args=[], env={'TEST_ARG': '1'})
        self.assertEqual(args, Namespace(test_arg=1))

        with self.assertRaises(ParserError) as ctx:
            parser.parse_args(args=[], env={'TEST_ARG': '42'})
        self.assertEqual(str(ctx.exception),
                         'argument --test-arg: invalid choice: 42 '
                         '(choose from 1, 2, 3)')

    def test_argument_with_choices(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--test-arg', choices=('foo', 'bar'))

        args = parser.parse_args(args=['--test-arg', 'foo'], env={})
        self.assertEqual(args, Namespace(test_arg='foo'))

        with self.assertRaises(ParserError):
            parser.parse_args(args=['--test-arg', '!foo'], env={})

        args = parser.parse_args(args=[], env={'TEST_ARG': 'foo'})
        self.assertEqual(args, Namespace(test_arg='foo'))

        with self.assertRaises(ParserError):
            parser.parse_args(args=[], env={'TEST_ARG': '!foo'})

    def test_action_store(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--foo',
                            action='store',
                            env_var='XFOO',
                            default='...')

        args = parser.parse_args(args=['--foo', '!!!'], env={})
        self.assertEqual(args, Namespace(foo='!!!'))

        args = parser.parse_args(args=[], env={'XFOO': '!!!'})
        self.assertEqual(args, Namespace(foo='!!!'))

        args = parser.parse_args(args=[], env={})
        self.assertEqual(args, Namespace(foo='...'))

        args = parser.parse_args(args=['--foo', '!!!'], env={'XFOO': '???'})
        self.assertEqual(args, Namespace(foo='!!!'))

    def test_action_const(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--foo',
                            env_var='XFOO',
                            action='store_const',
                            const='!!!',
                            default='...')

        args = parser.parse_args(args=['--foo'], env={})
        self.assertEqual(args, Namespace(foo='!!!'))

        args = parser.parse_args(args=[], env={'XFOO': '1'})
        self.assertEqual(args, Namespace(foo='!!!'))

        args = parser.parse_args(args=[], env={})
        self.assertEqual(args, Namespace(foo='...'))

        args = parser.parse_args(args=['--foo'], env={'XFOO': ''})
        self.assertEqual(args, Namespace(foo='!!!'))

    def test_action_store_true(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--foo',
                            env_var='XFOO',
                            action='store_true')

        args = parser.parse_args(args=['--foo'], env={})
        self.assertEqual(args, Namespace(foo=True))

        args = parser.parse_args(args=[], env={'XFOO': '1'})
        self.assertEqual(args, Namespace(foo=True))

        args = parser.parse_args(args=[], env={})
        self.assertEqual(args, Namespace(foo=False))

        args = parser.parse_args(args=['--foo'], env={'XFOO': ''})
        self.assertEqual(args, Namespace(foo=True))

    def test_action_store_false(self):
        parser = _EnvArgumentParse()
        parser.add_argument('--foo',
                            env_var='XFOO',
                            default=True,
                            action='store_false')

        args = parser.parse_args(args=['--foo'], env={})
        self.assertEqual(args, Namespace(foo=False))

        args = parser.parse_args(args=[], env={'XFOO': '1'})
        self.assertEqual(args, Namespace(foo=False))

        args = parser.parse_args(args=[], env={})
        self.assertEqual(args, Namespace(foo=True))

        args = parser.parse_args(args=['--foo'], env={'XFOO': ''})
        self.assertEqual(args, Namespace(foo=False))

    def test_action_count(self):
        parser = _EnvArgumentParse()
        parser.add_argument('-v', '--verbosity',
                            env_var='VERBOSITY',
                            action='count',
                            default=0)

        args = parser.parse_args(args=['-vvv'], env={})
        self.assertEqual(args, Namespace(verbosity=3))

        args = parser.parse_args(args=[], env={'VERBOSITY': 2})
        self.assertEqual(args, Namespace(verbosity=2))

        args = parser.parse_args(args=[], env={})
        self.assertEqual(args, Namespace(verbosity=0))

        args = parser.parse_args(args=['-vvv'], env={'VERBOSITY': 2})
        self.assertEqual(args, Namespace(verbosity=3))

    @unittest.skip('NotImplemented')
    def test_action_append(self):
        parser = _EnvArgumentParse()
        parser.add_argument('-t', '--things',
                            action='append',
                            env_var='THINGS',
                            default='???')
        args = parser.parse_args(args=['-t', 'first', '-t', 'second'], env={})
        self.assertEqual(args, Namespace(things=['first', 'second']))

        args = parser.parse_args(args=[], env={'THINGS': 'first,second'})
        self.assertEqual(args, Namespace(things='first,second'))

        args = parser.parse_args(args=[], env={})
        self.assertEqual(args, Namespace(things='???'))

        args = parser.parse_args(args=['-t', 'first', '-t', 'second'],
                                 env={'THINGS': 'first,second'})
        self.assertEqual(args, Namespace(things=['first', 'second']))


if __name__ == '__main__':
    unittest.main()
