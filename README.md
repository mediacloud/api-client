MediaCloud Python API Client
============================

🚧 Under construction 🚧  

This is a python client for accessing the MediaCloud API v4. This allows you to perform cross-platform searches and 
also browse our collection/source/feed directory.

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/mitmedialab/MediaCloud-API-Client/blob/master/LICENSE) [![Build Status](https://travis-ci.org/mitmedialab/MediaCloud-API-Client.svg?branch=master)](https://travis-ci.org/mitmedialab/MediaCloud-API-Client)

Usage
-----

First [sign up for an API key](https://search.mediacloud.org/).  Then
```
pip install mediacloud
```

Check `CHANGELOG.md` for a detailed history of changes.

### Examples

Take a look at the test in the `mediacloud/test/` module for more detailed examples.

Development
-----------

If you are interested in adding code to this module, first clone [the GitHub repository](https://github.com/c4fcm/MediaCloud-API-Client).

### Installing

`make install`

### Testing

`make test`

### Distributing a New Version

If you want to, setup [twin's keyring integration](https://pypi.org/project/twine/) to avoid typing your PyPI
password over and over. 

1. Run `make test` to make sure all the test pass
2. Update the version number in `mediacloud/__init__.py`
3. Make a brief note in the CHANGELOG.md about what changes
4. Run `make build-release` to create an install package
5. Run `make release-test` to upload it to PyPI's test platform
6. Run `make release` to upload it to PyPI
