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

#### Count Stories Matching a Query

```python
import mediacloud.api
US_NATIONAL_COLLECTION = 34412234
mc_search = mediacloud.api.SearchAPI(YOUR_MC_API_KEY)
all_stories = []
pagination_token = None
more_stories = True
while more_stories:
    page, pagination_token = mc_search.story_list('robots', start_date= , end_date= collection_ids=[US_NATIONAL_COLLECTION])
    all_stories += page
    more_stories = pagination_token is not None
print(f"Retrived {len(all_stories)} matching stories")
```

#### Page Through Stories Matching a Query

```python
import mediacloud.api
INDIA_NATIONAL_COLLECTION = 34412118
mc_search = mediacloud.api.SearchAPI(YOUR_MC_API_KEY)
all_stories = []
pagination_token = None
more_stories = True
while more_stories:
    page, pagination_token = mc_search.story_list('modi AND biden', collection_ids=[INDIA_NATIONAL_COLLECTION],
                                                  pagination_token=pagination_token)
    all_stories += page
    more_stories = pagination_token is not None
print(f"Retrived {len(all_stories)} matching stories")
```

#### Fetch all Sources in a Collection

```python
import mediacloud.api
INDIA_NATIONAL_COLLECTION = 34412118
SOURCES_PER_PAGE = 100  # the number of sources retrieved per page
mc_directory = mediacloud.api.DirectoryApi(YOUR_MC_API_KEY)
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

* `flit install`
* `pre-commit install`

### Testing

`pytest`

### Distributing a New Version

1. Run `pytest` to make sure all the test pass
2. Update the version number in `pyproject.toml`
3. Make a brief note in the `CHANGELOG.md` about what changes
4. Run `flit build` to create an install package
5. Run `flit publish` to upload it to PyPI
