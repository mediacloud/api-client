MediaCloud Python API Client
============================

🚧 Under construction 🚧  

This is a python client for accessing the MediaCloud API v4. This allows you to perform cross-platform searches and 
also browse our collection/source/feed directory.

![pylint](https://github.com/mediacloud/api-client/actions/workflows/pylint.yml/badge.svg) ![pytest](https://github.com/mediacloud/api-client/actions/workflows/pytest.yml/badge.svg) [![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/mitmedialab/MediaCloud-API-Client/blob/master/LICENSE)

Usage
-----

First [sign up for an API key](https://search.mediacloud.org/).  Then
```
pip install mediacloud
```

Check `CHANGELOG.md` for a detailed history of changes.

### Examples

Take a look at the test in the `mediacloud/test/` module for more detailed examples.

#### Fetch all Sources in a Collection

```python
import mediacloud.api
INDIA_NATIONAL_COLLECTION = 34412118
SOURCES_PER_PAGE = 100  # the number of sources retrieved per page
mc_directory = mediacloud.api.DirectoryApi(MC_API_KEY)
sources = []
offset = 0   # offset for paging through
while True:
    # grab a page of sources in the collection
    response = mc_directory.source_list(collection_id=INDIA_NATIONAL_COLLECTION, limit=SOURCES_PER_PAGE, offset=offset)
    # add it to our running list of all the sources in the collection
    sources += response['results']
    # if there is no next page then we're done so bail out
    if response['next'] is None:
        break
    # otherwise setup to fetch the next page of sources
    offset += len(response['results'])
print("India National Collection has {} sources".format(len(sources)))
```

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
