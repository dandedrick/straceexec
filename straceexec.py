#!/usr/bin/env python
import os
import re
import sys

def collect_commands(input_file):
    commands = []
    exec_line_re = re.compile(r'([0-9]+ |\[pid [0-9]+\] |) *execve\("([^"]*)", \[(.*)\], \[(.*)\](\)| <unfinished \.\.\.>)*')
    for line in input_file:
        exec_match = exec_line_re.match(line)
        if exec_match:
            command = exec_match.group(2);
            # We have to do some manipulation to remove the '"'s and ','s properly.
            # We don't want to split arguments that contain , and " but we need
            # to remove them to properly split and save away the arguments.
            args = []
            first=True
            last_arg = None
            for arg in exec_match.group(3).split('", "'):
                arg = arg.encode().decode('unicode_escape')
                if first:
                    arg = arg[1:]
                    first = False
                if last_arg:
                    args.append(last_arg)
                last_arg = arg;
            args.append(last_arg[:-1])
            env = {}
            first=True
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
            commands.append({"command":command, "args":args, "env":env})
    return commands

def print_commands(commands):
    index = 0
    rows, columns = os.popen('stty size', 'r').read().split()
    columns = int(columns)
    for command in commands:
        env_string = ""
        for key, value in command['env'].items():
            env_string = env_string + " " + key + "=" + value
        line = str(index) + ": " + " ".join(command["args"]) + " -:ENV:-" + env_string;

        if columns < len(line):
            line = line[:columns]
        print(line)
        index = index + 1

def get_selection(commands):
    invalid_input = True
    index = len(commands)
    while invalid_input:
        input_prompt = "Enter the number of the command you would like to execute\n\tAppend an n to not copy the environment\n\tAppend a p to print the full command and exit\n\tAppend a g to run under gdb\nSelect: "
        try:
            # python2 support
            selected = raw_input(input_prompt)
        except:
            # python3 support
            selected = input(input_prompt)
        match = re.match(r'([0-9]+)([npg]?)', selected)
        if match:
            command_index = int(match.group(1))
            if match.group(2) == "n":
                commands[command_index]["environment"] = os.environ
            elif match.group(2) == "p":
                commands[command_index]["print_only"] = True
            elif match.group(2) == "g":
                new_args = []
                new_args.append("gdb")
                new_args.append("-ex")
                set_gdb_args = 'set args'
                for arg in commands[command_index]["args"][1:]:
                    set_gdb_args = set_gdb_args + ' "' + arg.replace('"', '\"') + '"'
                new_args.append(set_gdb_args)
                for key, value in commands[command_index]['env'].items():
                    new_args.append("-ex")
                    new_args.append("set environment " + key + "=" + value)
                new_args.append(commands[command_index]["command"])
                commands[command_index]["command"] = "/usr/bin/gdb"
                commands[command_index]["args"] = new_args
                commands[command_index]["env"] = os.environ
            if command_index < index:
                invalid_input = False
            else:
                print("Invalid selection. The value must be less than " + str(index) + ".")
        else:
            print("Invalid entry")
    return commands[command_index]

def print_command(command):
    print_args = ""
    first=True
    for arg in command["args"]:
        if first:
            print_args = arg
            first = False
        else:
            print_args = print_args + " '" + arg.replace("'", "\\'") + "'"
    env_string = ""
    for key, value in command['env'].items():
        env_string = env_string + key + "=" + value + "\n"

    print("\nPATH:\n" + command["command"] + "\n\nARGS:\n" + print_args + "\n\nENV:\n"  + env_string)

def execute_command(command):
    if 'print_only' in command:
        print_command(command)
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
