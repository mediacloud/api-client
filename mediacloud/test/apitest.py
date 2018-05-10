import time
import datetime

import mediacloud.api
from mediacloud.test import load_text_from_fixture
from mediacloud.test.basetest import ApiBaseTest, AdminApiBaseTest
from mediacloud.tags import StoryTag, MediaTag, TAG_ACTION_ADD, TAG_ACTION_REMOVE

TEST_TAG_SET_ID = 1727
TEST_TAG_ID_1 = 9172171  # mc-api-test@media.mit.edu:test_tag1
TEST_TAG_ID_2 = 9172168  # mc-api-test@media.mit.edu:test_tag2
GEO_TAG_SET_ID = 1011
SAMPLE_STORY_ID = 101183836


class ApiBigQueryTest(ApiBaseTest):

    def testBigQuery(self):
        query_to_repeat = "(publish_date:[2016-05-16T00:00:00Z TO 2016-05-17T00:00:00Z]) AND (tags_id_media:(8875027))"
        query_pieces = [query_to_repeat for x in range(0, 110)]    # "110" was determined experimentally
        big_query = " AND ".join(query_pieces)
        results = self._mc.storyCount(big_query)
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

        self.assertTrue(self._mc.storyCount(date_query_default)['count'] > 0)
        self.assertTrue(self._mc.storyCount(date_query_inclusive_exclusive)['count'] > 0)
        self.assertTrue(self._mc.storyCount(date_query_inclusive_inclusive)['count'] > 0)
        self.assertTrue(self._mc.storyCount(date_query_exclusive_exclusive)['count'] > 0)
        self.assertTrue(self._mc.storyCount(date_query_exclusive_inclusive)['count'] > 0)


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




'''
TOO SLOW TO RUN!
    def testStoryPublicListByFeed(self):
        FEED_ID = 65    # NYT World feed
        results = self._mc.storyList(feeds_id=FEED_ID)
        self.assertNotEqual(len(results), 0)
        # anyway to check the feed id on a story returned?
'''


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

    def testRandomSeed(self):
        term_freq = self._mc.wordCount(self.QUERY, self.FILTER_QUERY)
        random_term_freq = self._mc.wordCount(self.QUERY, self.FILTER_QUERY, random_seed=20)
        self.assertEqual(len(term_freq), len(random_term_freq))


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

    def testChunkify(self):
        chunk_size = 50
        data = [x for x in range(0, 507)]
        chunked = mediacloud.api._chunkify(data, chunk_size)
        self.assertEqual(11, len(chunked))
        for x in range(0, 10):
            self.assertEqual(chunk_size, len(chunked[x]))
        self.assertEqual(7, len(chunked[10]))

