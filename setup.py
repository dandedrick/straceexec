import setuptools
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()

setuptools.setup(
    name='straceexec',
    version='1.1.0',
    py_modules=['straceexec'],
    entry_points={
        'console_scripts': [
            'straceexec = straceexec:main_func',
            ]
        },
    test_suite='tests',
    author='Dan Dedrick',
    author_email='dan.dedrick@gmail.com',
    description='A tool for executing commands based on strace output',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    url="https://github.com/dandedrick/straceexec",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3"
        ]
    )
