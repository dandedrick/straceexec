import setuptools

setuptools.setup(
        name='straceexec',
        version='1.0.0',
        py_modules=['straceexec'],
        entry_points={
            'console_scripts' : [
                'straceexec = straceexec:main_func',
                ]
            },
        test_suite='tests',
        author='Dan Dedrick',
        author_email='dan.dedrick@gmail.com',
        description='A tool for executing commands based on strace output',
        packages=setuptools.find_packages()
        )
