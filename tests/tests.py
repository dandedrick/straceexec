#!/usr/bin/env python
import unittest
try:
    import mock
except Exception:
    from unittest import mock
import straceexec
import glob
import os
import json


class TestStrace(unittest.TestCase):
    def remove_test_files(self):
        files = glob.glob('test_output*')
        for output_file in files:
            os.unlink(output_file)
        try:
            os.unlink("command.sh")
        except OSError:
            pass

    def setUp(self):
        self.remove_test_files()
        self.datadir = os.path.dirname(os.path.abspath(__file__)) + '/data/'

    def tearDown(self):
        self.remove_test_files()

    def test_execute_command(self):
        command = {'command': '/bin/sh',
                   'args': ['sh', '-c', 'touch test_output'],
                   'env': os.environ,
                   'mode': 'execute'}
        pid = os.fork()
        if pid == 0:
            straceexec.execute_command(command)
        os.waitpid(pid, 0)
        self.assertTrue(os.path.exists('test_output'))

    def test_execute_command_env(self):
        env = os.environ
        env['TEST_SUFFIX'] = 'foo'
        command = {'command': '/bin/sh',
                   'args': ['sh', '-c', 'touch test_output$TEST_SUFFIX'],
                   'env': env,
                   'mode': 'execute'}
        pid = os.fork()
        if pid == 0:
            straceexec.execute_command(command)
        os.waitpid(pid, 0)
        self.assertTrue(os.path.exists('test_outputfoo'))

    def test_execute_command_print_only(self):
        command = {'command': '/bin/sh',
                   'args': ['sh', '-c', 'touch test_output'],
                   'env': os.environ, 'mode': 'print_only'}
        # for now we ignore the actual output and just ensure that it doesn't
        # run the command
        with open("/dev/null", "w") as null_file:
            with mock.patch('sys.stdout', null_file):
                try:
                    straceexec.execute_command(command)
                except SystemExit:
                    pass
        self.assertFalse(os.path.exists('test_output'))

    def test_execute_command_write_script(self):
        command = {'command': '/bin/sh',
                   'args': ['sh', '-c', 'touch test_output'],
                   'env': os.environ, 'mode': 'write_script'}
        try:
            straceexec.execute_command(command)
        except SystemExit:
            pass
        self.assertFalse(os.path.exists('test_output'))
        self.assertTrue(os.path.exists('command.sh'))
        os.system("chmod a+x ./command.sh && ./command.sh")
        self.assertTrue(os.path.exists('test_output'))

    def test_strace_parse(self):
        with open(self.datadir + 'strace-1.log', 'r') as input_file:
            commands = straceexec.collect_commands(input_file)
        with open(self.datadir + 'strace-1.json', 'r') as json_file:
            commands_expected = json.loads(json_file.read())
        self.assertEqual(commands, commands_expected)

    def test_get_selection_simple(self):
        with open(self.datadir + 'strace-1.json', 'r') as json_file:
            commands = json.loads(json_file.read())
        input_str = 'six.moves.input'

        with mock.patch(input_str, return_value='4'):
            command = straceexec.get_selection(commands)
            with open(self.datadir + 'strace-1-cmd4.json', 'r') as json_result:
                expected = json.loads(json_result.read())
            self.assertEqual(command, expected)

    def test_get_selection_noenv(self):
        with open(self.datadir + 'strace-1.json', 'r') as json_file:
            commands = json.loads(json_file.read())
        input_str = 'six.moves.input'

        if "STRACE_TEST_ENV" in os.environ:
            del os.environ["STRACE_TEST_ENV"]

        with mock.patch(input_str, return_value="2n"):
            command = straceexec.get_selection(commands)
        with open(self.datadir + 'strace-1-cmd2n.json', 'r') as json_result:
            expected = json.loads(json_result.read())

        # os.environ is not good for comparison or conversion to json so we
        # have to convert it into a dict here.
        expected["env"] = {}
        for key in os.environ:
            expected["env"][key] = os.environ[key]
        command_env = command["env"]
        command["env"] = {}
        for key in command_env:
            command["env"][key] = command_env[key]
        self.assertEqual(command, expected)
        self.assertNotIn("STRACE_TEST_ENV", command["env"])

    def test_get_selection_print(self):
        with open(self.datadir + 'strace-1.json', 'r') as json_file:
            commands = json.loads(json_file.read())
        input_str = 'six.moves.input'

        with mock.patch(input_str, return_value="1p"):
            command = straceexec.get_selection(commands)
        with open(self.datadir + 'strace-1-cmd1p.json') as json_result:
            expected = json.loads(json_result.read())
        self.assertEqual(command, expected)

    def test_get_selection_script(self):
        with open(self.datadir + 'strace-1.json', 'r') as json_file:
            commands = json.loads(json_file.read())
        input_str = 'six.moves.input'

        with mock.patch(input_str, return_value="0s"):
            command = straceexec.get_selection(commands)
        with open(self.datadir + 'strace-1-cmd0s.json') as json_result:
            expected = json.loads(json_result.read())
        with open("1", "w") as f:
            f.write(json.dumps(command))
        self.assertEqual(command, expected)


if __name__ == '__main__':
    unittest.main()
