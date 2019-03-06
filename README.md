MediaCloud Python API Client
============================

This is a python client for accessing the [MediaCloud API v2](https://github.com/berkmancenter/mediacloud/blob/master/doc/api_2_0_spec/api_2_0_spec.md). 
We support Python versions 2.7 and 3.6.

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/mitmedialab/MediaCloud-API-Client/blob/master/LICENSE) [![Build Status](https://travis-ci.org/mitmedialab/MediaCloud-API-Client.svg?branch=master)](https://travis-ci.org/mitmedialab/MediaCloud-API-Client)

Usage
-----

First [sign up for an API key](https://core.mediacloud.org/login/register).  Then
```
pip install mediacloud
```

Check `CHANGELOG.md` for a detailed history of changes.

Examples
--------

Find out how many stories in the top US online news sites mentioned "Zimbabwe" in the last year:
```python
import mediacloud.api
mc = mediacloud.api.MediaCloud('MY_API_KEY')
res = mc.storyCount('zimbabwe AND president AND tags_id_media:58722749', 'publish_date:[NOW-1YEAR TO NOW]')
print(res['count']) # prints the number of stories found
```

Get 2000 stories from the NYT about a topic in 2018 and dump the output to json:

```python
import mediacloud.api, json, datetime
mc = mediacloud.api.MediaCloud('MY_API_KEY')

fetch_size = 500
stories = []
last_processed_stories_id = 0
while len(stories) < 2000:
    fetched_stories = mc.storyList('trump AND "north korea" AND media_id:1', 
                                   solr_filter=mc.publish_date_query(datetime.date(2018,1,1), datetime.date(2019,1,1)),
                                   last_processed_stories_id=last_processed_stories_id, rows= fetch_size)
    stories.extend(fetched_stories)
    if len( fetched_stories) < fetch_size:
        break
    last_processed_stories_id = stories[-1]['processed_stories_id']
print(json.dumps(stories))
```

Find the most commonly used words in stories from the US top online news sites that mentioned "Zimbabwe" and "president" in 2013:
```python
import mediacloud.api, datetime
mc = mediacloud.api.MediaCloud('MY_API_KEY')
words = mc.wordCount('zimbabwe AND president AND tags_id_media:58722749',
                     mc.publish_date_query( datetime.date( 2013, 1, 1), datetime.date( 2014, 1, 1)))
print(words[0])  # prints the most common word
```

To find out all the details about one particular story by id:
```python
import mediacloud.api
mc = mediacloud.api.MediaCloud('MY_API_KEY')
story = mc.story(169440976)
print(story['url'])  # prints the url the story came from
```

To save the first 100 stories from one day to a database:
```python
import mediacloud.api, datetime
mc = mediacloud.api.MediaCloud('MY_API_KEY')
db = mediacloud.storage.MongoStoryDatabase('one_day')
stories = mc.storyList('*', mc.publish_date_query( datetime.date (2014, 01, 01), datetime.date(2014,01,02) ),
                       last_processed_stories_id=0,rows=100)
[db.addStory(s) for s in stories]
print(db.storyCount())
```

Take a look at the test in the `mediacloud/test/` module for more detailed examples.

Development
-----------

If you are interested in adding code to this module, first clone [the GitHub repository](https://github.com/c4fcm/MediaCloud-API-Client).

## Testing

You need to create an `MC_API_KEY` envvar and set it to your API key (we use [`python-dotenv`](https://pypi.org/project/python-dotenv/)).
Then run `make test`. We run continuous integration (via [Travis](https://travis-ci.org/mitmedialab/MediaCloud-API-Client)),
so every push runs the whole test suite (we also do this nightly and on PRs). 

## Distributing a New Version

If you want to, setup [twin's keyring integration](https://pypi.org/project/twine/) to avoid typing your PyPI
password over and over. 

1. Run `make test` to make sure all the test pass
2. Update the version number in `mediacloud/__init__.py`
3. Make a brief note in the CHANGELOG.md about what changes
4. Run `make build-release` to create an install package
5. Run `make release-test` to upload it to PyPI's test platform
5. Run `make release` to upload it to PyPI
