#!/usr/bin/env python

import os
import sys
try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

if sys.version_info < (3, 3, 0):
  print('This module is not supported on versions lower than python 3.3, sorry !')
  print('Your version of python is %s, try installing it with a more recent version.'
        % '.'.join(map(str, sys.version_info[:3])))
  sys.exit(1)

setup(
  name="rst2ansi",
  version="0.1.0",
  author="Snaipe",
  author_email="franklinmathieu@gmail.com",
  description="A minecraft server manager",
  license="MIT",
  keywords="rst restructuredtext ansi console code converter",
  url="https://github.com/Snaipe/python-rst-to-ansi",
  packages=['rst2ansi'],
  requires=['docutils'],
  scripts=['bin/rst2ansi'],
  data_files=[],
  classifiers=[
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing :: Markup",
    "Topic :: Utilities",
  ],
)
