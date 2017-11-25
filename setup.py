#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Crosslink setup module."""
from __future__ import absolute_import, unicode_literals, with_statement

import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand  # flake8: disable=H306,N812


class PyTest(TestCommand):

    """Test harness."""

    user_options = []

    def initialize_options(self):
        """Initialise options hook."""
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        """Run tests hook."""
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def get_version(fname='crosslink/__init__.py'):
    """Get __version__ from package __init__."""
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


tests_require = ['pytest']

setup(
    name='crosslink',
    version=get_version(),
    description='crosslink identities.',
    keywords='github gitlab bitbucket keybase openhub',
    author='John Vandenberg',
    author_email='jayvdb@gmail.com',
    url='https://github.com/jayvdb/crosslink',
    license='MIT',
    packages=[str('crosslink'), str('crosslink/services')],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
    tests_require=tests_require,
    cmdclass={'test': PyTest},
)
