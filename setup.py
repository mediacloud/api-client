#! /usr/bin/env python
from setuptools import setup
import re
from os import path

version = ''
with open('mediacloud/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(name='mediacloud',
      version=version,
      description='Media Cloud API Client Library',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Rahul Bhargava',
      author_email='rahulb@mit.edu',
      url='http://mediacloud.org',
      test_suite="mediacloud.test",
      packages={'mediacloud'},
      package_data={'': ['LICENSE']},
      install_requires=['requests'],
      license='MIT',
      zip_safe=False,
      extras_require={'db': ['pymongo']}
      )
