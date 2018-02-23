import time
import datetime

import mediacloud.api
from mediacloud.test import load_text_from_fixture
from mediacloud.test.basetest import ApiBaseTest, AdminApiBaseTest
from mediacloud.tags import StoryTag, MediaTag, TAG_ACTION_ADD, TAG_ACTION_REMOVE

TEST_USER_EMAIL = "mc-api-test@media.mit.edu"
TEST_TAG_SET_ID = 1727
TEST_TAG_ID_1 = 9172171  # mc-api-test@media.mit.edu:test_tag1
TEST_TAG_ID_2 = 9172168  # mc-api-test@media.mit.edu:test_tag2
GEO_TAG_SET_ID = 1011
TEST_MEDIA_SUGGEST_REASON = "!!!! TESTING SUGGESTION !!!!"
SAMPLE_STORY_ID = 101183836


class ApiBigQueryTest(ApiBaseTest):

    def testBigQuery(self):
        query_to_repeat = "(publish_date:[2016-05-16T00:00:00Z TO 2016-05-17T00:00:00Z]) AND (tags_id_media:(8875027))"
        query_pieces = [query_to_repeat for x in range(0, 110)]    # "110" was determined experimentally
        big_query = " AND ".join(query_pieces)
        results = self._mc.sentenceCount(big_query)
        self.assertTrue(results['count'] > 0)


class ApiAllFieldsOptionTest(ApiBaseTest):

    def testAllFieldsOnMedia(self):
        # do a regular query
        media = self._mc.media(1751)
        self.assertNotEqual(media, None)
        self.assertEqual(media['media_id'], 1751)
        self.assertFalse('foreign_rss_links' in media)
        self.assertTrue('url' in media)
        # do an all fields regular query and verify extra fields are there
        self._mc.setAllFields(True)
        media = self._mc.media(1751)
        self.assertNotEqual(media, None)
        self.assertEqual(media['media_id'], 1751)
        self.assertTrue('foreign_rss_links' in media)
        self.assertTrue('url' in media)


class AuthTokenTest(ApiBaseTest):

    def testAuthToken(self):
        valid_auth_token = self._config.get('api', 'key')
        fake_auth_token = 'these are not the keys you are looking for'
        # make sure setAuthToken workds
        self._mc.setAuthToken(fake_auth_token)
        self.assertEqual(self._mc._auth_token, fake_auth_token)
        # see a request with a bad key fail
        try:
            self._mc.media(1)
            self.assertFalse(True)
        except:
            self.assertTrue(True)
        # set the key back to a valid one
        self._mc.setAuthToken(valid_auth_token)

    def testUserAuthToken(self):
        # test failure mode
        try:
            self._mc.userAuthToken('user@funkytown.us', '1234')
            self.assertFalse(True)
        except:
            self.assertTrue(True)


class UserProfileTest(ApiBaseTest):

    def testUserProfile(self):
        profile = self._mc.userProfile()
        self.assertTrue('email' in profile)
        self.assertTrue('auth_roles' in profile)
        self.assertTrue('admin' in profile['auth_roles'])


class StatsTest(ApiBaseTest):

    def testStats(self):
        stats = self._mc.stats()
        data_keys  = [
            "total_downloads",
            "total_sentences",
            "active_crawled_feeds",
            "active_crawled_media",
            "daily_stories",
            "total_stories",
            "daily_downloads",
            "stats_date"
        ]
        for key in data_keys:
            self.assertTrue(key in stats, "{0} not found".format(key))


class PublishDateQueryTest(ApiBaseTest):

    def testPublishDateQuery(self):
        start_date = datetime.date(2014, 06, 02)
        end_date = datetime.date(2014, 06, 03)
        date_query_default = self._mc.publish_date_query(start_date, end_date)
        self.assertEqual(date_query_default, "publish_date:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z}")

        date_query_inclusive_exclusive = self._mc.publish_date_query(start_date, end_date, start_date_inclusive=True, end_date_inclusive=False)
        self.assertEqual(date_query_inclusive_exclusive, "publish_date:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z}")

        date_query_inclusive_inclusive = self._mc.publish_date_query(start_date, end_date, start_date_inclusive=True, end_date_inclusive=True)
        self.assertEqual(date_query_inclusive_inclusive, "publish_date:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z]")

        date_query_exclusive_inclusive = self._mc.publish_date_query(start_date, end_date, start_date_inclusive=False, end_date_inclusive=True)
        self.assertEqual(date_query_exclusive_inclusive, "publish_date:{2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z]")

        date_query_exclusive_exclusive = self._mc.publish_date_query(start_date, end_date, start_date_inclusive=False, end_date_inclusive=False)
        self.assertEqual(date_query_exclusive_exclusive, "publish_date:{2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z}")

        self.assertTrue(self._mc.sentenceCount(date_query_default)['count'] > 0)
        self.assertTrue(self._mc.sentenceCount(date_query_inclusive_exclusive)['count'] > 0)
        self.assertTrue(self._mc.sentenceCount(date_query_inclusive_inclusive)['count'] > 0)
        self.assertTrue(self._mc.sentenceCount(date_query_exclusive_exclusive)['count'] > 0)
        self.assertTrue(self._mc.sentenceCount(date_query_exclusive_inclusive)['count'] > 0)


class ApiMediaHealthTest(ApiBaseTest):

    def testMediaHealth(self):
        media_health = self._mc.mediaHealth(2)
        self.assertEqual(media_health['media_id'], 2)
        self.assertEqual(media_health['is_healthy'], 0)
        self.assertEqual(media_health['coverage_gaps'], len(media_health['coverage_gaps_list']))
        self.assertTrue('start_date' in media_health)
        self.assertTrue('end_date' in media_health)

    def testNoHealthData(self):
        health = self._mc.mediaHealth(99999999999)  # ie. an invalid id
        self.assertEqual(0, len(health))


class ApiMediaTest(ApiBaseTest):

    def testMedia(self):
        media = self._mc.media(1)
        self.assertNotEqual(media, None)
        self.assertEqual(int(media['media_id']), 1)
        self.assertEqual(media['name'], 'New York Times')
        self.assertTrue("is_monitored" in media)
        self.assertTrue("editor_notes" in media)
        self.assertTrue("public_notes" in media)
        self.assertTrue(len(media['media_source_tags']) > 0)
        self.assertTrue("pub_country" in media['metadata'])
        self.assertTrue("pub_state" in media['metadata'])
        self.assertTrue("language" in media['metadata'])
        self.assertTrue("about_country" in media['metadata'])
        self.assertTrue("media_type" in media['metadata'])

    def testMediaListWithName(self):
        matching_list = self._mc.mediaList(name_like='new york times')
        self.assertEqual(len(matching_list), 2)

    def testMediaList(self):
        first_list = self._mc.mediaList()
        for media in first_list:
            self.assertTrue(media['media_id'] > 0)
            self.assertTrue("is_monitored", media)
            self.assertTrue("editor_notes", media)
            self.assertTrue("public_notes", media)
            self.assertTrue(len(media['media_source_tags']) > 0)
            self.assertTrue("pub_country" in media['metadata'])
            self.assertTrue("pub_state" in media['metadata'])
            self.assertTrue("language" in media['metadata'])
            self.assertTrue("about_country" in media['metadata'])
            self.assertTrue("media_type" in media['metadata'])
        self.assertNotEqual(first_list, None)
        self.assertEqual(len(first_list), 20)
        last_page_one_media_id = int(first_list[19]['media_id'])-1
        self.assertTrue(last_page_one_media_id > 0)
        second_list = self._mc.mediaList(last_page_one_media_id)
        for media in second_list:
            self.assertTrue(media['media_id'] > last_page_one_media_id)
        self.assertEqual(len(second_list), 20)
        self.assertEqual(first_list[19]['media_id'], second_list[0]['media_id'])
        longer_list = self._mc.mediaList(0, 200)
        self.assertEqual(len(longer_list), 200)

    def testMediaListWithTagId(self):
        matching_list = self._mc.mediaList(tags_id=8875027)  # US MSM
        self.assertTrue(len(matching_list) > 0)

    def testMediaListUnhealthy(self):
        # make sure no overlap in healthy and unhealthy first page of results
        ids = set([m['media_id'] for m in self._mc.mediaList()])
        healthy_ids = set([i for i in ids if self._mc.mediaHealth(i)['is_healthy'] == 1])
        unhealthy_ids = set([m['media_id'] for m in self._mc.mediaList(unhealthy=True)])
        intersection = list(healthy_ids & unhealthy_ids)
        self.assertTrue(len(intersection) == 0)


class ApiFeedTest(AdminApiBaseTest):

    def testFeedScrape(self):
        test_media_id = 362086     # rahulbotics.com
        # queue scrape job
        results = self._mc.feedsScrape(test_media_id)
        self.assertEqual(test_media_id, int(results['job_state']['media_id']))
        self.assertTrue(results['job_state']['state'] in ['queued', 'completed'])

    def testFeedScrapeStatus(self):
        test_media_id = 1 # nyt
        # verify pending jobs
        scrape_status = self._mc.feedsScrapeStatus(test_media_id)
        self.assertEqual(23, len(scrape_status['job_states']))


class AdminApiMediaSuggestionsTest(AdminApiBaseTest):

    def testMediaSuggestionMark(self):
        suggest_result = self._mc.mediaSuggest("https://rahulbotics",
                                        name="Rahulbotics",
                                        reason=TEST_MEDIA_SUGGEST_REASON,
                                        tags_ids=[9353679])
        self.assertTrue('success' in suggest_result)
        self.assertEqual(1, int(suggest_result['success']))
        list_result = self._mc.mediaSuggestionsList()
        for suggestion in list_result:
            if suggestion['reason'] == TEST_MEDIA_SUGGEST_REASON:
                mark_result = self._mc.mediaSuggestionsMark(suggestion['media_suggestions_id'], "rejected",
                                                       "This was a test suggestion, so we are deleting it.")
                self.assertTrue('success' in mark_result)
                self.assertEqual(1, int(mark_result['success']))

    def testMediaSuggest(self):
        results = self._mc.mediaSuggest("https://rahulbotics",
                                        name="Rahulbotics",
                                        reason=TEST_MEDIA_SUGGEST_REASON,
                                        tags_ids=[9353679])
        self.assertTrue('success' in results)
        self.assertEqual(1, int(results['success']))

    def testMediaSuggestionsList(self):
        results = self._mc.mediaSuggestionsList()
        # could be empty, so lets just make sure it is an array
        self.assertTrue(isinstance(results, list))
        for suggestion in results:
            self.assertTrue('email' in suggestion)


class ApiTagsTest(ApiBaseTest):

    def testTags(self):
        tag = self._mc.tag(8876989) # US mainstream media
        self.assertEqual(tag['tags_id'], 8876989)
        self.assertEqual(tag['tag'], 'JP')
        self.assertEqual(tag['tag_sets_id'], 597)

    def testTagList(self):
        # verify it only pulls tags from that one set
        first_list = self._mc.tagList(597)
        self.assertEqual(len(first_list), 20)
        ignore = [self.assertEqual(tag['tag_sets_id'], 597) for tag in first_list]
        # make sure paging through a set works right
        second_list = self._mc.tagList(597, int(first_list[19]['tags_id'])-1)
        self.assertEqual(len(second_list), 20)
        ignore = [self.assertEqual(tag['tag_sets_id'], 597) for tag in second_list]
        self.assertEqual(first_list[19]['tags_id'], second_list[0]['tags_id'])
        # make sure you can pull a longer list of tags
        longer_list = self._mc.tagList(597, 0, 150)
        self.assertEqual(len(longer_list), 150)
        ignore = [self.assertEqual(tag['tag_sets_id'], 597) for tag in longer_list]
        longest_list = self._mc.tagList(597, 0, 200)
        self.assertEqual(len(longest_list), 173)
        ignore = [self.assertEqual(tag['tag_sets_id'], 597) for tag in longest_list]
        # try getting only the public tags in the set
        full_list = self._mc.tagList(6, rows=200)
        public_list = self._mc.tagList(6, rows=200, public_only=True)
        self.assertNotEqual(len(full_list), len(public_list))

    def testTagListMultpleSets(self):
        search = "Ghana"
        collection1_id = 5 # collections
        collection2_id= 556 # GV
        list_1 = self._mc.tagList(collection1_id, name_like=search)
        self.assertTrue(len(list_1) > 0)
        list_2 = self._mc.tagList(collection2_id, name_like=search)
        self.assertTrue(len(list_2) > 0)
        combined_list = self._mc.tagList([collection1_id, collection2_id], name_like=search)
        self.assertEqual(len(combined_list), len(list_1) + len(list_2))

    def testTagListSimilar(self):
        collection_tags = self._mc.tagList(similar_tags_id=8876989)
        self.assertEqual(20, len(collection_tags))

    def testTagListSearch(self):
        # verify search works at all
        collection_tags = self._mc.tagList(name_like="collection")
        self.assertTrue(len(collection_tags) > 0, "Got %d tags matching 'collection'" % len(collection_tags))
        # verify search works on tags without descriptions
        geo_tags = self._mc.tagList(name_like="geonames_")
        self.assertTrue(len(geo_tags) > 0, "Got %d tags matching 'geonames_'" % len(geo_tags))


class ApiTagSetsTest(ApiBaseTest):

    def testTagSet(self):
        tagSet = self._mc.tagSet(597)
        self.assertEqual(tagSet['tag_sets_id'], 597)
        self.assertEqual(tagSet['name'], 'gv_country')

    def testTagSetList(self):
        first_list = self._mc.tagSetList()
        self.assertEqual(len(first_list), 20)
        second_list = self._mc.tagSetList(int(first_list[19]['tag_sets_id'])-1)
        self.assertEqual(len(second_list), 20)
        self.assertEqual(first_list[19]['tag_sets_id'], second_list[0]['tag_sets_id'])
        longer_list = self._mc.tagSetList(0, 50)
        self.assertEqual(len(longer_list), 50)


class ApiFeedsTest(ApiBaseTest):

    def testFeed(self):
        media_set = self._mc.feed(1)
        self.assertEqual(media_set['feeds_id'], 1)
        self.assertEqual(media_set['name'], 'Bits')
        self.assertEqual(media_set['media_id'], 1)

    def testFeedList(self):
        first_list = self._mc.feedList(1)
        self.assertEqual(len(first_list), 20)
        second_list = self._mc.feedList(1, int(first_list[19]['feeds_id'])-1)
        self.assertEqual(len(second_list), 20)
        self.assertEqual(first_list[19]['feeds_id'], second_list[0]['feeds_id'])
        longer_list = self._mc.feedList(1, 0, 200)
        self.assertEqual(len(longer_list), 142)


class AdminApiMediaTest(AdminApiBaseTest):

    def testMediaUpdate(self):
        test_media_id = 362086     # rahulbotics.com
        prop_to_change = 'editor_notes'
        updated_prop_value = 'Rahul\'s test domain!'
        original = self._mc.media(test_media_id)
        # update something
        results = self._mc.mediaUpdate(test_media_id, { prop_to_change: updated_prop_value })
        updated = self._mc.media(test_media_id)
        self.assertEqual(updated[prop_to_change], updated_prop_value)
        # set it back and verify
        results = self._mc.mediaUpdate(test_media_id, { prop_to_change: original[prop_to_change] })
        reverted = self._mc.media(test_media_id)
        self.assertEqual(reverted[prop_to_change], original[prop_to_change])

    def testMediaCreateDuplicate(self):
        media_item = {
            'url': "http://nytimes.com",
            'editor_notes': "duplicate for testing",
            'tags_ids': [8875027],
            'name': 'Duplicate New York Times'
        }
        media_to_create = [media_item]
        results = self._mc.mediaCreate(media_to_create)
        self.assertEqual(len(results), len(media_to_create))
        self.assertTrue("media_id" in results[0])
        self.assertTrue("status" in results[0])
        self.assertTrue("url" in results[0])
        self.assertEqual("existing", results[0]['status'])


class AdminApiStoriesTest(AdminApiBaseTest):

    def testStoryListSort(self):
        results_by_id = self._mc.storyList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY, sort=mediacloud.api.MediaCloud.SORT_PROCESSED_STORIES_ID, rows=20)
        self.assertEqual(len(results_by_id), 20)
        results_by_bitly = self._mc.storyList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY, sort=mediacloud.api.MediaCloud.SORT_BITLY_CLICK_COUNT, rows=20)
        self.assertEqual(len(results_by_bitly), 20)
        for i in [0,19]:
            self.assertNotEqual(results_by_id[i]['stories_id'], results_by_bitly[i]['stories_id'])

    def testStoryListWordCount(self):
        results = self._mc.storyList(wc=True)
        for story in results:
            self.assertTrue('wc' in story)
            self.assertTrue(story['wc'] > 0)

    def testStoryWithSentences(self):
        story = self._mc.story(27456565, sentences=True)
        self.assertEqual(int(story['stories_id']), 27456565)
        self.assertEqual(story['media_id'], 1144)
        self.assertTrue('story_sentences' in story)
        self.assertFalse('story_text' in story)
        self.assertFalse('is_fully_extracted' in story)

    def testStoryWithText(self):
        story = self._mc.story(27456565, text=True)
        self.assertEqual(int(story['stories_id']), 27456565)
        self.assertEqual(story['media_id'], 1144)
        self.assertFalse('story_sentences' in story)
        self.assertTrue('story_text' in story)
        self.assertTrue('is_fully_extracted' in story)

    def testStoryList(self):
        results = self._mc.storyList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY)
        self.assertNotEqual(len(results), 0)
        for story in results:
            self.assertTrue('bitly_click_count' in story)
            self.assertTrue('date_guess_method' in story['metadata'])
            self.assertTrue('extractor_version' in story['metadata'])
            self.assertTrue('geocoder_version' in story['metadata'])
            self.assertTrue('nyt_themes_version' in story['metadata'])

    def testStoryListDefaults(self):
        results = self._mc.storyList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY, rows=10)
        for story in results:
            self.assertFalse('story_sentences' in story)
            self.assertFalse('story_text' in story)
            self.assertFalse('is_fully_extracted' in story)

    def testStoryListWithSentences(self):
        results = self._mc.storyList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY, sentences=True, rows=10)
        for story in results:
            self.assertTrue('story_sentences' in story)
            self.assertFalse('story_text' in story)
            self.assertFalse('is_fully_extracted' in story)

    def testStoryListWithText(self):
        results = self._mc.storyList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY, text=True, rows=10)
        for story in results:
            self.assertFalse('story_sentences' in story)
            self.assertTrue('story_text' in story)
            self.assertTrue('is_fully_extracted' in story)

    def testStoryRawCliffResults(self):
        cliff_results = self._mc.storyRawCliffResults([SAMPLE_STORY_ID])
        self.assertEqual(len(cliff_results), 1)
        self.assertEqual(cliff_results[0]['stories_id'], SAMPLE_STORY_ID)
        self.assertTrue('results' in cliff_results[0]['cliff'])
        self.assertTrue('organizations' in cliff_results[0]['cliff']['results'])

    def testStoryRawNytThemeResults(self):
        nyt_theme_results = self._mc.storyRawNytThemeResults([SAMPLE_STORY_ID])
        self.assertEqual(len(nyt_theme_results), 1)
        self.assertEqual(nyt_theme_results[0]['stories_id'], SAMPLE_STORY_ID)
        self.assertTrue('descriptors600' in nyt_theme_results[0]['nytlabels'])

'''
TOO SLOW!
    def testStoryListInFeed(self):
        TEST_FEEDS_ID_1 = 61  # NYT US news feeds (http://www.nytimes.com/services/xml/rss/nyt/US.xml)
        TEST_FEEDS_ID_2 = 313908  # WashPo Business feed (https://core.mediacloud.org/admin/downloads/list?f=313908)
        results1 = set([s['stories_id'] for s in self._mc.storyList(feeds_id=TEST_FEEDS_ID_1)])
        results2 = set([s['stories_id'] for s in self._mc.storyList(feeds_id=TEST_FEEDS_ID_2)])
        intersection = list(results1 & results2)
        self.assertTrue(len(intersection) == 0)
        # now test lower level (only do 3 cause it takes a long time)
        results1 = self._mc.storyList(feeds_id=TEST_FEEDS_ID_1, show_feeds=True, rows=3)
        for s in results1:
            feed_ids = [f['feeds_id'] for f in s['feeds']]
            self.assertTrue(TEST_FEEDS_ID_1 in feed_ids)
'''


class ApiStoriesWordMatrixTest(ApiBaseTest):

    def testStoryWordMatrix(self):
        results = self._mc.storyWordMatrix("obama",
            "(publish_date:[2016-05-16T00:00:00Z TO 2016-05-17T00:00:00Z]) AND (tags_id_media:(8875027))")
        self.assertTrue("word_matrix" in results)
        self.assertTrue("word_list" in results)


class ApiStoriesTest(ApiBaseTest):

    def testStory(self):
        story = self._mc.story(27456565)
        self.assertEqual(int(story['stories_id']), 27456565)
        self.assertEqual(story['media_id'], 1144)
        self.assertFalse('story_sentences' in story)
        self.assertFalse('story_text' in story)
        self.assertFalse('is_fully_extracted' in story)
        self.assertTrue('bitly_click_count' in story)

    def testStoryPublic(self):
        story = self._mc.story(27456565)
        self.assertEqual(story['media_id'], 1144)
        self.assertTrue('story_sentences' not in story)
        self.assertTrue('language' in story)
        self.assertTrue('title' in story)
        self.assertTrue('bitly_click_count' in story)

    def testStoryPublicList(self):
        results = self._mc.storyList(self.QUERY, self.FILTER_QUERY)
        self.assertNotEqual(len(results), 0)
        for story in results:
            self.assertTrue('bitly_click_count' in story)

    def testStoryCount(self):
        results = self._mc.storyCount(self.QUERY, self.FILTER_QUERY)
        self.assertEqual(results['count'], 741)

'''
TOO SLOW TO RUN!
    def testStoryPublicListByFeed(self):
        FEED_ID = 65    # NYT World feed
        results = self._mc.storyList(feeds_id=FEED_ID)
        self.assertNotEqual(len(results), 0)
        # anyway to check the feed id on a story returned?
'''


class AdminApiSentencesTest(AdminApiBaseTest):

    def testSentenceListSortingAscending(self):
        results = self._mc.sentenceList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY, 0, ApiBaseTest.SENTENCE_COUNT,
            self._mc.SORT_PUBLISH_DATE_ASC)
        self.assertEqual(len(results['response']['docs']), ApiBaseTest.SENTENCE_COUNT)
        last_date = None
        for sentence in results['response']['docs']:
            this_date = datetime.datetime.strptime(sentence['publish_date'], self._mc.SENTENCE_PUBLISH_DATE_FORMAT)
            this_date = this_date.replace(second=0, microsecond=0) # sorting is by minute
            if last_date is not None:
                self.assertTrue(last_date <= this_date, "Date wrong: "+str(last_date)+" is not <= "+str(this_date))
                last_date = this_date
            last_date = this_date

    def testSentenceListSortingDescending(self):
        results = self._mc.sentenceList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY, 0, ApiBaseTest.SENTENCE_COUNT,
            self._mc.SORT_PUBLISH_DATE_DESC)
        self.assertEqual(len(results['response']['docs']), ApiBaseTest.SENTENCE_COUNT)
        last_date = None
        for sentence in results['response']['docs']:
            this_date = datetime.datetime.strptime(sentence['publish_date'], self._mc.SENTENCE_PUBLISH_DATE_FORMAT)
            this_date = this_date.replace(second=0, microsecond=0) # sorting is by minute
            if last_date is not None:
                self.assertTrue(last_date >= this_date, "Date wrong: "+str(last_date)+" is not >= "+str(this_date))
                last_date = this_date
            last_date = this_date

    def testSentenceListSortingRadom(self):
        # we do random sort by telling we want the random sort, and then offsetting to a different start index
        results1 = self._mc.sentenceList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY, 0, ApiBaseTest.SENTENCE_COUNT,
            self._mc.SORT_RANDOM)
        self.assertEqual(len(results1['response']['docs']), ApiBaseTest.SENTENCE_COUNT)
        results2 = self._mc.sentenceList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY, ApiBaseTest.SENTENCE_COUNT*2, ApiBaseTest.SENTENCE_COUNT,
            self._mc.SORT_RANDOM)
        self.assertEqual(len(results2['response']['docs']), ApiBaseTest.SENTENCE_COUNT)
        for idx in range(0, ApiBaseTest.SENTENCE_COUNT):
            self.assertNotEqual(results1['response']['docs'][idx]['stories_id'], results2['response']['docs'][idx]['stories_id'],
                "Stories in two different random sets are the same :-(")

    def testSentenceList(self):
        results = self._mc.sentenceList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY)
        self.assertEqual(int(results['responseHeader']['status']), 0)
        self.assertEqual(int(results['response']['numFound']), 2240)
        self.assertEqual(len(results['response']['docs']), 1000)

    def testSentenceListPaging(self):
        # test limiting rows returned
        results = self._mc.sentenceList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY, 0, 100)
        self.assertEqual(int(results['response']['numFound']), 2240)
        self.assertEqual(len(results['response']['docs']), 100)
        # test starting offset
        results = self._mc.sentenceList(ApiBaseTest.QUERY, ApiBaseTest.FILTER_QUERY, 5700)
        self.assertEqual(int(results['response']['numFound']), 2240)
        self.assertFalse('docs' in results['response'], 0)


class ApiSentencesTest(ApiBaseTest):

    def testUnicodeSentenceCount(self):
        # make sure Unicode str doesn't toss an error
        split_start_date = '2017-03-15'
        split_end_date = '2017-03-30'
        q = u'+( \u5b89\u90e8 ) AND media_id:97659'
        results = self._mc.sentenceCount(solr_query=q, split_start_date=split_start_date, split_end_date=split_end_date)
        self.assertTrue(results is not None)

    def testSentenceCount(self):
        # basic counting
        results = self._mc.sentenceCount('obama', '+media_id:1')
        self.assertTrue(int(results['count']) > 10000)
        # counting with a default split weekly (>180 days)
        results = self._mc.sentenceCount('obama', '+media_id:1', True, '2013-01-01', '2014-01-01')
        self.assertEqual(results['split']['gap'], '+7DAYS')
        self.assertEqual(len(results['split']), 56)
        # counting with a default split 3-day (<180 days, >90 days)
        results = self._mc.sentenceCount('obama', '+media_id:1', True, '2014-01-01', '2014-06-01')
        self.assertEqual(results['split']['gap'], '+3DAYS')
        self.assertEqual(len(results['split']), 54)
        # counting with a default split daily (<90 days)
        results = self._mc.sentenceCount('obama', '+media_id:1', True, '2014-01-01', '2014-01-07')
        self.assertEqual(results['split']['gap'], '+1DAY')
        self.assertEqual(len(results['split']), 9)
        # test forcing a daily split
        results = self._mc.sentenceCount('obama', '+media_id:1', True, '2014-01-01', '2014-06-01', True)
        self.assertEqual(results['split']['gap'], '+1DAY')
        self.assertEqual(len(results['split']), 154)

    def testFieldCount(self):
        # regular call for story counts
        story_results = self._mc.sentenceFieldCount('obama', '+media_id:1', field='tags_id_stories')
        self.assertFalse('stats' in story_results)
        self.assertFalse('counts' in story_results)
        self.assertTrue(len(story_results) > 0)
        ignore = [self.assertTrue(tag['count']) for tag in story_results]
        # with stats
        results = self._mc.sentenceFieldCount('obama', '+media_id:1', include_stats=True)
        self.assertTrue('stats' in results)
        self.assertTrue('counts' in results)
        # filter by tag set
        sentence_results = self._mc.sentenceFieldCount('obama', '+media_id:1', tag_sets_id=GEO_TAG_SET_ID)
        self.assertTrue(len(sentence_results) > 0)
        ignore = [self.assertEqual(tag['tag_sets_id'], GEO_TAG_SET_ID) for tag in sentence_results]


class ApiWordCountTest(ApiBaseTest):

    QUERY = 'robots'

    def testResults(self):
        term_freq = self._mc.wordCount(self.QUERY, self.FILTER_QUERY)
        self.assertEqual(term_freq[1]['stem'], u'human')

    def testSort(self):
        term_freq = self._mc.wordCount(self.QUERY, self.FILTER_QUERY)
        # verify sorted in desc order
        last_count = 10000000000
        for freq in term_freq:
            self.assertTrue(last_count >= freq['count'])
            last_count = freq['count']

    def testNumWords(self):
        term_freq = self._mc.wordCount(self.QUERY, self.FILTER_QUERY)
        self.assertGreater(len(term_freq), 100)
        term_freq = self._mc.wordCount(self.QUERY, self.FILTER_QUERY, num_words=100)
        self.assertEqual(len(term_freq), 100)

    def testStopWords(self):
        term_freq = self._mc.wordCount(self.QUERY, self.FILTER_QUERY)
        self.assertEqual(term_freq[1]['stem'], u'human')
        term_freq = self._mc.wordCount(self.QUERY, self.FILTER_QUERY, include_stopwords=True)
        self.assertEqual(term_freq[3]['stem'], u'of')

    def testStats(self):
        term_freq = self._mc.wordCount(self.QUERY, self.FILTER_QUERY)
        self.assertEqual(term_freq[1]['stem'], u'human')
        term_freq = self._mc.wordCount(self.QUERY, self.FILTER_QUERY, include_stats=True)
        self.assertEqual(len(term_freq), 2)
        self.assertTrue('stats' in term_freq.keys())
        self.assertTrue('words' in term_freq.keys())

    def testBigram(self):
        term_freq = self._mc.wordCount(self.QUERY, self.FILTER_QUERY, ngram_size=2)
        for term in term_freq:
            self.assertEqual(len(term['term'].split(' ')), 2)


class AdminApiTaggingTest(AdminApiBaseTest):

    def testTagCreate(self):
        new_tag_name = 'test-create-tag-'+str(int(time.time()))
        self._mc.createTag(TEST_TAG_SET_ID, new_tag_name, 'Test Create Tag', 'this is just a test tag')
        # now search for it by name
        results = self._mc.tagList(name_like=new_tag_name)
        self.assertNotEqual(0, len(results))

    def testTagUpdate(self):
        example_tag_id = TEST_TAG_ID_1
        # change the name, label and description
        self._mc.updateTag(example_tag_id, 'modified tag', 'modified label', 'modified description')
        modified_tag = self._mc.tag(example_tag_id)
        self.assertEqual(modified_tag['tag'], 'modified tag')
        self.assertEqual(modified_tag['label'], 'modified label')
        self.assertEqual(modified_tag['description'], 'modified description')
        # set it back
        self._mc.updateTag(example_tag_id, 'example tag', 'example label', 'This is an example tag used in api client test scripts')
        modified_tag = self._mc.tag(example_tag_id)
        self.assertEqual(modified_tag['tag'], 'example tag')
        self.assertEqual(modified_tag['label'], 'example label')
        self.assertEqual(modified_tag['description'], 'This is an example tag used in api client test scripts')

    def testTagSetUpdate(self):
        example_tag_sets_id = TEST_TAG_SET_ID
        # change the name, label and description
        self._mc.updateTagSet(example_tag_sets_id, TEST_USER_EMAIL, 'modified label', 'modified description')
        modified_tag = self._mc.tagSet(example_tag_sets_id)
        self.assertEqual(modified_tag['name'], TEST_USER_EMAIL)
        self.assertEqual(modified_tag['label'], 'modified label')
        self.assertEqual(modified_tag['description'], 'modified description')
        # set it back
        self._mc.updateTagSet(example_tag_sets_id, TEST_USER_EMAIL, 'rahulbot', 'The tag set of Rahul!')
        modified_tag = self._mc.tagSet(example_tag_sets_id)
        self.assertEqual(modified_tag['name'], TEST_USER_EMAIL)
        self.assertEqual(modified_tag['label'], 'rahulbot')
        self.assertEqual(modified_tag['description'], 'The tag set of Rahul!')


class AdminApiTaggingContentTest(AdminApiBaseTest):

    def testTagMedia(self):
        media_to_tag = 4451    # ESPN.com
        test_tag_id1 = TEST_TAG_ID_1
        tag_set_name = TEST_USER_EMAIL
        # add a tag
        desired_tag = MediaTag(media_to_tag, tags_id=test_tag_id1, action=TAG_ACTION_ADD)
        response = self._mc.tagMedia([desired_tag])
        self.assertTrue('success' in response)
        self.assertEqual(response['success'], 1)
        # and check it
        story = self._mc.media(media_to_tag)
        tags_on_media = [t['tags_id'] for t in story['media_source_tags'] if t['tag_set'] == tag_set_name]
        self.assertTrue(int(test_tag_id1) in tags_on_media)
        # and remove it
        desired_tag = MediaTag(media_to_tag, tags_id=test_tag_id1, action=TAG_ACTION_REMOVE)
        response = self._mc.tagMedia([desired_tag])
        self.assertTrue('success' in response)
        self.assertEqual(response['success'], 1)
        story = self._mc.media(media_to_tag)
        tags_on_media = [t['tags_id'] for t in story['media_source_tags'] if t['tag_set'] == tag_set_name]
        self.assertEqual(0, len(tags_on_media))

    def testTagStories(self):
        test_story_id = 2
        tag_set_name = TEST_USER_EMAIL
        # tag a story with two things
        desired_tags = [StoryTag(test_story_id, tag_set_name, 'test_tag1'),
                 StoryTag(test_story_id, tag_set_name, 'test_tag2')]
        response = self._mc.tagStories(desired_tags)
        self.assertTrue('success' in response)
        self.assertEqual(response['success'], 1)
        story = self._mc.story(test_story_id, sentences=True)   # make sure it worked
        tags_on_story = [t for t in story['story_tags'] if t['tag_set'] == tag_set_name]
        self.assertEqual(2, len(tags_on_story))
        # test removal by action
        desired_tags = [StoryTag(test_story_id, tag_set_name, 'test_tag1', TAG_ACTION_REMOVE)]
        response = self._mc.tagStories(desired_tags)
        story = self._mc.story(test_story_id, sentences=True)   # make sure it worked
        tags_on_story = [t for t in story['story_tags'] if t['tag_set'] == tag_set_name]
        self.assertEqual(1, len(tags_on_story))
        # test removal by clear others
        desired_tags = [StoryTag(test_story_id, tag_set_name, 'test_tag1')]
        response = self._mc.tagStories([], clear_others=True)
        story = self._mc.story(test_story_id, sentences=True)   # make sure it worked
        tags_on_story = [t for t in story['story_tags'] if t['tag_set'] == tag_set_name]
        self.assertEqual(1, len(tags_on_story))

    def testChunkify(self):
        chunk_size = 50
        data = [x for x in range(0, 507)]
        chunked = mediacloud.api._chunkify(data, chunk_size)
        self.assertEqual(11, len(chunked))
        for x in range(0, 10):
            self.assertEqual(chunk_size, len(chunked[x]))
        self.assertEqual(7, len(chunked[10]))


class AdminApiStoryUpdateTest(AdminApiBaseTest):

    def testStoryUpdate(self):
        # check the story has a language
        story = self._mc.story(27456565)
        original_language = story['language']
        self.assertEqual(original_language, 'en')
        # change it to spanish
        results = self._mc.storyUpdate(27456565, language='es')
        self.assertEqual(results['success'], 1)
        story = self._mc.story(27456565)
        self.assertEqual(story['language'], 'es')
        # and set it back
        results = self._mc.storyUpdate(27456565, language=original_language)
        self.assertEqual(results['success'], 1)
        story = self._mc.story(27456565)
        self.assertEqual(story['language'], original_language)


class ApiStoryAPSyndicatedTest(ApiBaseTest):

    def testIsSyndicated(self):
        text = load_text_from_fixture("sample_story_ap.txt")
        results = self._mc.storyIsSyndicatedFromAP(text)
        self.assertEqual(results['is_syndicated'], 1)

    def testIsNotSyndicated(self):
        text = load_text_from_fixture("sample_story_not_ap.txt")
        results = self._mc.storyIsSyndicatedFromAP(text)
        self.assertEqual(results['is_syndicated'], 0)
