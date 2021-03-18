# straceexec
[![Build Status](https://travis-ci.org/dandedrick/straceexec.svg?branch=master)](https://travis-ci.org/dandedrick/straceexec)
[![PyPI version](https://badge.fury.io/py/straceexec.svg)](https://badge.fury.io/py/straceexec)


straceexec is a python script that allows for playback and analysis of
execve commands from strace logs. This is useful for debugging commands
embedded several layers deep with significant automated setup. One specific
use case would be debugging specific commands from a build system that setup
many environment variables or have complex command line invocations.


## Usage
```
# strace -f -v -s 10000 -o strace.log ninja
# straceexec strace.log
0: ninja -:ENV:- LANG=en_US.UTF-8 USERNAME=ddedrick SHELL=/bin/bash output=default GDM_LANG=en_US.UTF EDITOR=vimx PATH=/u
1: /bin/sh -c /usr/lib64/ccache/cc -Dfoo_EXPORTS  -fPIC -MD -MT CMakeFiles/foo.dir/foo.c.o -MF CMakeFiles/foo.dir/foo.c.o
2: /usr/lib64/ccache/cc -Dfoo_EXPORTS -fPIC -MD -MT CMakeFiles/foo.dir/foo.c.o -MF CMakeFiles/foo.dir/foo.c.o.d -o CMakeF
3: /bin/sh -c : && /usr/lib64/ccache/cc -fPIC    -shared -Wl,-soname,libfoo.so.0 -o libfoo.so.0.3.0 CMakeFiles/foo.dir/fo
4: /usr/lib64/ccache/cc -fPIC -shared -Wl,-soname,libfoo.so.0 -o libfoo.so.0.3.0 CMakeFiles/foo.dir/foo.c.o -:ENV:- LANG=
5: /usr/bin/cc -fPIC -shared -Wl,-soname,libfoo.so.0 -o libfoo.so.0.3.0 CMakeFiles/foo.dir/foo.c.o -:ENV:- LANG=en_US.UTF
6: /usr/libexec/gcc/x86_64-redhat-linux/8/collect2 -plugin /usr/libexec/gcc/x86_64-redhat-linux/8/liblto_plugin.so -plugi
7: /usr/bin/ld -plugin /usr/libexec/gcc/x86_64-redhat-linux/8/liblto_plugin.so -plugin-opt=/usr/libexec/gcc/x86_64-redhat
8: /bin/sh -c /usr/bin/cmake -E cmake_symlink_library libfoo.so.0.3.0  libfoo.so.0 libfoo.so && : -:ENV:- LANG=en_US.UTF-
9: /usr/bin/cmake -E cmake_symlink_library libfoo.so.0.3.0 libfoo.so.0 libfoo.so -:ENV:- LANG=en_US.UTF-8 USERNAME=ddedri
Enter the number of the command you would like to execute
	Append an n to not copy the environment
	Append a p to print the full command and exit
	Append a g to run under gdb
Select: 1
```


strace output should be collected with -v to ensure that arguments are not
left off and -s with a sufficiently large size so that they are not
truncated.


By default the command will be run and will have the same environment setup
as is found in the strace output. Several options are available for
modifying this behavior. Appending an ```n``` will use the current
environment instead of the one present in the strace log. Appending a
```p``` will not exec the command but instead print it in full along with
its environment. Appending a ```g``` will start start up gdb with the
executable, arguments, and environment already setup. Appending an ```s``` will
generate a script named command.sh that will set the environment and run the
the command.


## Contributing
Contributions, issues, and feature requests are welcome. Feel free to open
pull requests or issues as needed.


## Author
Written by Dan Dedrick to simplify isolating, reproducing and tweaking build
system issues.


## License
straceexec is distributed under the MIT license. See the included LICENSE
file for details.
