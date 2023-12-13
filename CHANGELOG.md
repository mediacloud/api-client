Version History
===============


Version 4
---------

### v4.1.1
* improve consistency of results by changing date from str to dt.date in count_over_time

### v4.1.0
* created new SearchAPI module to support updated search API

### v4.0.1
* added a "modified_before" parameter to DirectoryApi.feed_list for use by rss_fetcher

### v4.0.0

* ⚠️ 🚧 Complete rewrite. This is first work on supporting new API for cross-platform search and directory of
collections/sources/feeds. This is an entirely new system we are building out.


Version 3
---------

### v3.13.0

* add TIMEOUT_SECS property, defaulting to 30 seconds (configurable by user on `MediaCloud` object)

### v3.12.5

* update MongoDB storage helper to use URI for connection (so it support user/pass authentication)

### v3.12.4

* prevent people from trying to page through randomly sorted `storyList` results - it doesn't work so we shouldn't
let them try

### v3.12.3

* pass `old_stopwords` param as int to `storyWordMatrix` and `wordCount`

### v3.12.2

* added `old_stopwords` param to `storyWordMatrix` and `wordCount`

### v3.12.1

* switch two more methods to use POST to send data over so they can request larger batches of results by sending in a
big array of story ids (`storyRawCliffResults` and `storyRawNytThemeResults`)

### v3.12.0

* deprecate `publish_date_query` - switch to `dates_as_query_clause` instead (defaults to inclusive, matching our web
tools and typical usage patterns)

### v3.11.3

* support new topic story list sorting options

### v3.11.2

* even more work on POSTing long queries

### v3.11.1

* more work on POSTing long queries

### v3.11.0

* add support for making some common requests via POST, so they can support really long queries

### v3.10.0

* remove deprecated topic "mode" parameter
* add topic snapshots (admin-only) and timespans list endpoints

### v3.9.3

* even more work on topic media map download endpoint

### v3.9.2

* more work fixing topic media map download endpoint

### v3.9.1

* fix media map param typo

### v3.9.0

* fix topic mode support
* add new topic media map list call, and update media map call

### v3.8.0

* add support for topicInfo call

### v3.7.6

* add support for podcast feed type

### v3.7.5

* remove silly logging error

### v3.7.4

* more privacy-related logging improvements (and tests for them)

### v3.7.3

* improve logging to not log key user data

### v3.7.2

* remove registration `subscribe_to_newsletter`

### v3.7.1

* remove registration-related `has_consented` hack

### v3.7.0

* add support for mutiple topic seed queries via `topic_queries` endpoints

### v3.6.5

* support searching for media by boolean combinations of tags

### v3.6.4

* allow downloading randomly sorted lists of topic stories

### v3.6.3

* fix bug with `has_consented` on auth/reg call

### v3.6.2

* add `has_consented` to auth/reg call

### v3.6.1

* fix update focus call to use JSON format

### v3.6.0

* add `has_consented` to user update

### v3.5.1

* fix for spidering into an existing snapshot

### v3.5.0

* add new snapshots/create endpoint, and support passing in a snapshots_id to the topicSpider call

### v3.4.4

* more work on exceptions and documentation for importing

### v3.4.3

* fix problem with `MCException`s not saving the details that caused them

### v3.4.2

* default development to python3 (we still test on both 3.6 and 2.7 on CI)
* upgrade release strategy to use twine

### v3.4.1

* setup for CI - added linting and automated release tasks via makefile

### v3.4.0

* add more options to user update endpoint, and user deletion endpoint

### v3.3.1

* add paging to user list endpoint

### v3.3.0

* new user management admin endpoints

### v3.2.3

* fix bug related to word counts with no `fq` param

### v3.2.2

* fix bug related to paging over topicMediaLinks and topicStoryLinks

### v3.2.1

* adds paging support to topicStoryLinks and topicMediaLinks

### v3.2.0

* adds topicStoryLinks and topicMediaLinks endpoints

### v3.1.1

* adds in parsed out metadata to the topicMediaList call (under a `metadata` property on each item)

### v3.1.0

* updates feed management for new backend API changes

### v3.0.4

* adds ability to move tags from one tag_set to another (use the `tag_sets_id` argumet to `updateTag` method)

### v3.0.3

* fixes https problem that was making POST calls fail

### v3.0.2

* fixes dumb typo

### v3.0.1

* adds `fq` as a valid param on a few more topicStory calls

### v3.0.0

This release is not backwards-compatible.  You will likely need to update your code.

* switches to story-based search
* removes sentence endpoints
* adds `storyCount` split options to replace `sentenceCount` with a `split` param
* adds in `storyTagCount` to replace `sentenceFieldCount`
* adds support for specifying date range by time/day/week/month; default to `publish_day` searching
* begins refactoring tests into individual modules by content type (story, sentence, tag, etc.)
* begins removing references to specific content (by id) so we can test on non-production databases


Version 2
---------

* __v2.53.0__: add random_seed option to wordCount call
* __v2.52.0__: added new topicSnapshotWord2VecModel endpoint
* __v2.51.0__: added sort options to mediaList
* __v2.50.0__: added profiling timing at debug log level
* __v2.49.0__: fix return value in `topicReset`
* __v2.48.0__: add dangerous `topicReset` function
* __v2.47.0__: add labelled metadata to story list results
* __v2.46.0__: add labelled metadata to media list and media results
* __v2.45.0__: add new `max_stories` param to topic read, create and update endpoints
* __v2.44.0__: add new `storyIsSyndicatedFromAP` endpoint and tests
* __v2.43.3__: fix source suggestion collection support
* __v2.43.2__: fix raw story detail cliff and nytlabels endpoints
* __v2.43.1__: make JSON posts py3 compatible
* __v2.43.0__: topicList limit option, story-update endpoint, remove story coreNLP support, remove sentence-level tagging
* __v2.42.0__: add is_logogram option to topic creation and updating
* __v2.41.0__: updates to topic stories and media sorting, and ngram_size param to word count endpoints
* __v2.40.1__: auth api fixes
* __v2.40.0__: add support for listing topics by name, or by if they are public or not
* __v2.39.2__: work on feed-related calls
* __v2.39.1__: fix topicMediaList to accept q as a param
* __v2.39.0__: new user reg endpoints, handle unicode in GET queries better
* __v2.38.2__: don't default wordcount to English
* __v2.38.1__: fix bug in mediaSuggestionsMark for approving media suggestions
* __v2.38.0__: add topic media map support
* __v2.37.0__: media source feed scraping, topic create/update, snapshot generate, mediaUpdate change
* __v2.36.2__: fixed defaults on updateTag
* __v2.36.1__: fixed system stats endpoint
* __v2.36.0__: added mediaSuggest workflow endpoints
* __v2.35.6__: mediaCreate fixes, storyList feed support
* __v2.35.5__: create media fixes
* __v2.35.4__: create collection fixes
* __v2.35.3__: fixes to clear_others support in tag* calls
* __v2.35.2__: fixes to updateMedia
* __v2.35.1__: fixes to createTagSet
* __v2.35.0__: tons of new source-related endpoints
* __v2.34.0__: new permissons endpoints
* __v2.33.1__: move topic endpoints to standard client so users can run them
* __v2.33.0__: lots of new api endpoints for topic management
* __v2.32.0__: fix links in topicStoryList and topicMediaList
* __v2.31.0__: migrate dumpsList and timesliceList to snapshotList and timespanList
* __v2.30.0__: migrate controversyList and controversy to topicList and topic
* __v2.29.1__: fixes to topicWordCount method return value
* __v2.29.0__: add topicSentenceCount, and paging for topicMediaList & topicStoriesList endpoints
* __v2.28.0__: add storyWordMatrix, support long queries via POST automatically
* __v2.27.0__: first topic endpoints
* __v2.26.1__: chunk sentence tag calls to avoid URI length limit in PUT requests
* __v2.26.0__: add storyCount endpoint, cleanup some failing test cases
* __v2.25.0__: add mediaHealth endpoint, support `ap_stories_id` flag in storiesList, fix `controversy_dump_time_slices` endpoint, remove mediaSet and Dashboard endpoints
* __v2.24.1__: fixes tab/spaces bug
* __v2.24.0__: adds new params to the `mediaList` query (searching by controversy, solr query, tags_id, etc)
* __v2.23.0__: adds solr date generation helpers
* __v2.22.2__: fixes the PyPI readme
* __v2.22.1__: moves `sentenceList` to the admin client, preps for PyPI release
* __v2.22.0__: adds the option to enable `all_fields` at the API client level (ie. for all requests)
