#! /usr/bin/env python
import re
from os import path
from setuptools import setup

REQUIRED_PACKAGES = [
    # utilities
    "requests==2.*",  # widely used HTTP library
]

with open('mediacloud/__init__.py', 'r', encoding="utf-8") as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

# add README.md to distribution
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding="utf-8") as f:
    long_description = f.read()

setup(name='mediacloud',
      maintainer='Rahul Bhargava',
      maintainer_email='r.bhargava@northeastern.edu',
      version=version,
      description='Media Cloud API Client Library',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://mediacloud.org',
      test_suite="mediacloud.test",
      packages=['mediacloud'],
      package_data={'': ['LICENSE']},
      python_requires='>3.7',
      install_requires=REQUIRED_PACKAGES,
      extras_require={'dev': ['pytest', 'pylint', 'twine', 'wheel', 'keyring', 'python-dotenv']},
      license='MIT',
      )
