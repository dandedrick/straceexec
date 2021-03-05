#!/usr/bin/env python
import os
import re
import sys
import six


def collect_commands(input_file):
    commands = []
    exec_line_re = re.compile(r'([0-9]+ |\[pid [0-9]+\] |)'
                              r' *execve\("([^"]*)", \[(.*)\], \[(.*)\]'
                              r'(\)| <unfinished \.\.\.>)*')
    for line in input_file:
        exec_match = exec_line_re.match(line)
        if exec_match:
            command = exec_match.group(2)
            # We have to do some manipulation to remove the '"'s and ','s
            # properly.  We don't want to split arguments that contain , and "
            # but we need to remove them to properly split and save away the
            # arguments.
            args = []
            first = True
            last_arg = None
            for arg in exec_match.group(3).split('", "'):
                arg = arg.encode().decode('unicode_escape')
                if first:
                    arg = arg[1:]
                    first = False
                if last_arg:
                    args.append(last_arg)
                last_arg = arg
            args.append(last_arg[:-1])
            env = {}
            first = True
            last_var = None
            for var in exec_match.group(4).split('", "'):
                var = var.encode().decode('unicode_escape')
                if first:
                    var = var[1:]
                    first = False
                if last_var:
                    (key, value) = last_var.split("=", 1)
                    env[key] = value
                last_var = var
            (key, value) = last_var[:-1].split("=", 1)
            env[key] = value
            commands.append({"command": command, "args": args, "env": env})
    return commands


def print_commands(commands):
    index = 0
    rows, columns = os.popen('stty size', 'r').read().split()
    columns = int(columns)
    for command in commands:
        env_string = ""
        for key, value in command['env'].items():
            env_string = env_string + " " + key + "=" + value
        line = "{}: {} -:ENV:-{}".format(index, " ".join(command["args"]),
                                         env_string)

        if columns < len(line):
            line = line[:columns]
        print(line)
        index = index + 1


def get_selection(commands):
    invalid_input = True
    index = len(commands)
    while invalid_input:
        input_prompt = """Enter the number of the command you would like to execute
\tAppend an n to not copy the environment
\tAppend a p to print the full command and exit
\tAppend a g to run under gdb
\tAppend an s to write a script to execute the command
Select: """
        selected = six.moves.input(input_prompt)
        match = re.match(r'([0-9]+)([npgs]?)', selected)
        if match:
            command_index = int(match.group(1))
            commands[command_index]["mode"] = "execute"
            if match.group(2) == "n":
                commands[command_index]["env"] = os.environ
            elif match.group(2) == "p":
                commands[command_index]["mode"] = "print_only"
            elif match.group(2) == "g":
                new_args = []
                new_args.append("gdb")
                new_args.append("-ex")
                set_gdb_args = 'set args'
                for arg in commands[command_index]["args"][1:]:
                    set_gdb_args = '{} "{}"'.format(set_gdb_args,
                                                    arg.replace('"', '\"'))
                new_args.append(set_gdb_args)
                for key, value in commands[command_index]['env'].items():
                    new_args.append("-ex")
                    new_args.append("set environment " + key + "=" + value)
                new_args.append(commands[command_index]["command"])
                commands[command_index]["command"] = "/usr/bin/gdb"
                commands[command_index]["args"] = new_args
                commands[command_index]["env"] = os.environ
            elif match.group(2) == "s":
                commands[command_index]["mode"] = "write_script"
            if command_index < index:
                invalid_input = False
            else:
                print("Invalid selection. The value must be less than " +
                      str(index) + ".")
        else:
            print("Invalid entry")
    return commands[command_index]


def print_command(command):
    print_args = ""
    first = True
    for arg in command["args"]:
        if first:
            print_args = arg
            first = False
        else:
            print_args = print_args + " '" + arg.replace("'", "\\'") + "'"
    env_string = ""
    for key, value in command['env'].items():
        env_string = env_string + key + "=" + value + "\n"

    print("\nPATH:\n{}\n\nARGS:\n{}\n\nENV:\n{}".format(command["command"],
                                                        print_args,
                                                        env_string))


def write_script(command):
    with open("command.sh", "w") as f:
        f.write("#!/bin/sh\n")
        f.write("env -i \\\n")
        for key, value in command['env'].items():
            f.write("'")
            f.write(key)
            f.write('=')
            f.write(value.replace("'", "'\"'\"'"))
            f.write("' \\\n")
        for arg in command["args"]:
            f.write("'")
            f.write(arg.replace("'", "'\"'\"'"))
            f.write("' ")
        f.write("\n")


def execute_command(command):
    if command["mode"] == 'print_only':
        print_command(command)
        sys.exit(0)
    elif command["mode"] == 'write_script':
        write_script(command)
        sys.exit(0)
    os.execve(command["command"], command["args"], command["env"])


def main_func():
    if len(sys.argv) > 1:
        input_file = open(sys.argv[1], "r")
    else:
        input_file = sys.stdin

    commands = collect_commands(input_file)
    print_commands(commands)
    run_command = get_selection(commands)
    execute_command(run_command)


if __name__ == "__main__":
    main_func()
