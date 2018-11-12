#!/usr/bin/env python
import unittest
try:
    import mock
except:
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
    def setUp(self):
        self.remove_test_files()
        self.datadir = os.path.dirname(os.path.abspath(__file__)) + '/data/'
    def tearDown(self):
        self.remove_test_files()
    def test_execute_command(self):
        command = {'command':'/bin/sh', 'args': ['sh', '-c', 'touch test_output'], 'env': os.environ}
        pid = os.fork()
        if pid == 0:
            straceexec.execute_command(command)
        os.waitpid(pid, 0)
        self.assertTrue(os.path.exists('test_output'))
    def test_execute_command_env(self):
        env = os.environ
        env['TEST_SUFFIX'] = 'foo'
        command = {'command':'/bin/sh', 'args': ['sh', '-c', 'touch test_output$TEST_SUFFIX'], 'env': env}
        pid = os.fork()
        if pid == 0:
            straceexec.execute_command(command)
        os.waitpid(pid, 0)
        self.assertTrue(os.path.exists('test_outputfoo'))
    def test_execute_command_print_only(self):
        command = {'command':'/bin/sh', 'args': ['sh', '-c', 'touch test_output'], 'env': os.environ, 'print_only': True}
        # for now we ignore the actual output and just ensure that it doesn't run the command
        null_file = open("/dev/null", "w")
        with mock.patch('sys.stdout', null_file) as fake_out:
            try:
                straceexec.execute_command(command)
            except SystemExit as e:
                pass
        null_file.close()
        self.assertFalse(os.path.exists('test_output'))
    def test_strace_parse(self):
        input_file=open(self.datadir + 'strace-1.log', 'r')
        commands = straceexec.collect_commands(input_file)
        input_file.close()
        json_file = open(self.datadir + 'strace-1.json', 'r')
        commands_expected = json.loads(json_file.read())
        json_file.close()
        self.assertTrue(commands == commands_expected)
    def test_get_selection(self):
        json_file = open(self.datadir + 'strace-1.json', 'r')
        commands = json.loads(json_file.read())
        json_file.close()
        try:
            raw_input
            input_str='__builtin__.raw_input'
        except:
            input_str='builtins.input'

        with mock.patch(input_str, return_value='4'):
            command = straceexec.get_selection(commands)
            json_result = open(self.datadir + 'strace-1-cmd4.json', 'r')
            expected = json.loads(json_result.read())
            json_result.close()
            self.assertTrue(command == expected)

if __name__ == '__main__':
    unittest.main()
