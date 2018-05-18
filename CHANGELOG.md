Version History
===============

### v3.0.1

* add `fq` as a valid param on a few more topicStory calls

### v3.0.0

This release is not backwards-compatible.  You will likely need to update your code.

* switch to story-based search
* remove sentence endpoints
* add `storyCount` split options to replace `sentenceCount` with a `split` param
* add in `storyTagCount` to replace `sentenceFieldCount`
* add support for specifying date range by time/day/week/month; default to `publish_day` searching
* being refactoring tests into individual modules by content type (story, sentence, tag, etc.)
* begin removing references to specific content (by id) so we can test on non-production databases

Previous Versions
-----------------

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
