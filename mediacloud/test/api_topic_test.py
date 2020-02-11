import mediacloud.api
from mediacloud.test.basetest import AdminApiBaseTest

TEST_TOPIC_ID = 1537    # climate change topic
TEST_TOPIC2_ID = 1019   # common core
TEST_TOPIC3_ID = 3180   # rahul test


class ApiTopicTest(AdminApiBaseTest):

    def testTopic(self):
        topic = self._mc.topic(TEST_TOPIC_ID)
        self.assertEqual(int(topic['topics_id']), 1537)
        self.assertEqual(topic['name'], 'Climate Change 2016')

    def testTopicHasMaxStories(self):
        topic = self._mc.topic(TEST_TOPIC_ID)
        self.assertIn('max_stories', topic)
        try:
            int(topic['max_stories'])
            self.assertTrue(True)
        except ValueError:
            self.assertTrue(False, "max_stories value of '{}' is not an int ".format(topic['max_stories']))

    def testTopicList(self):
        # verify it pulls some
        topic_list = self._mc.topicList()
        self.assertGreater(len(topic_list['topics']), 1)
        # verify limit param
        topic_list = self._mc.topicList(limit=2)
        self.assertEqual(len(topic_list['topics']), 2)
        # verify limit param
        topic_list = self._mc.topicList(limit=1)
        self.assertEqual(len(topic_list['topics']), 1)

    def testTopicListPublic(self):
        topic_list = self._mc.topicList(public=True)
        self.assertGreater(len(topic_list), 1)
        for topic in topic_list['topics']:
            self.assertEqual(topic['is_public'], 1)

    def testTopicListName(self):
        to_match = "common"
        topic_list = self._mc.topicList(name=to_match)
        self.assertGreater(len(topic_list), 1)
        for topic in topic_list['topics']:
            self.assertIn(to_match.lower(), topic['name'].lower())

    def testTopicListPaging(self):
        # verify second page doesn't contain any ids from the first page
        topic_list_page_1 = self._mc.topicList()
        page_1_ids = [t['topics_id'] for t in topic_list_page_1['topics']]
        self.assertGreater(len(topic_list_page_1), 1)
        topic_list_page_2 = self._mc.topicList(topic_list_page_1['link_ids']['next'])
        self.assertGreater(len(topic_list_page_2), 1)
        page_2_ids = [t['topics_id'] for t in topic_list_page_2['topics']]
        self.assertTrue(len(set(page_1_ids).intersection(set(page_2_ids))), 0)


class ApiTopicSnapshotTest(AdminApiBaseTest):

    def testTopicSnapshotList(self):
        # make sure it works
        snapshots = self._mc.topicSnapshotList(TEST_TOPIC_ID)
        self.assertEqual(len(snapshots), 1)


class ApiTopicSpiderTest(AdminApiBaseTest):

    def testTopicSpiderStatus(self):
        results = self._mc.topicSpiderStatus(TEST_TOPIC2_ID)
        self.assertIn('job_states', results)

'''
    def testTopicSpiderIterationsList(self):
        results = self._mc.topicSpiderIterationsList(TEST_TOPIC2_ID)
        self.assertTrue('iterations' in results)
        self.assertEqual(15, len(results['iterations']))
        first_iteration = results['iterations'][0]
        self.assertTrue('iteration' in first_iteration)
        self.assertEqual(0, first_iteration['iteration'])
        self.assertTrue('count' in first_iteration)
        self.assertTrue(0, first_iteration['count'])
'''


class ApiTopicTimespanTest(AdminApiBaseTest):

    def testTopicTimespanList(self):
        # verify it pulls data
        timespans = self._mc.topicTimespanList(1)
        self.assertGreater(len(timespans), 1)


class AdminTopicStoryListTest(AdminApiBaseTest):
    TOPIC_ID = 1

    def testTopicStoryListFacebookData(self):
        response = self._mc.topicStoryListFacebookData(self.TOPIC_ID)
        self.assertEqual(len(response['counts']), 1000)
        for story in response['counts']:
            self.assertIn('facebook_api_collect_date', story)
            self.assertIn('facebook_comment_count', story)
            self.assertIn('facebook_share_count', story)
            self.assertIn('stories_id', story)

    def testTopicStoryList(self):
        response = self._mc.topicStoryList(self.TOPIC_ID)
        self.assertEqual(len(response['stories']), 20)
        for story in response['stories']:
            self.assertIn('date_is_reliable', story)

    def testTopicStoryListPaging(self):
        limit = 50
        response_page_1 = self._mc.topicStoryList(self.TOPIC_ID, limit=limit)
        response_page_1_ids = [m['stories_id'] for m in response_page_1['stories']]
        self.assertEqual(len(response_page_1['stories']), 50)
        self.assertIn('link_ids', response_page_1)
        response_page_2 = self._mc.topicStoryList(self.TOPIC_ID, link_id=response_page_1['link_ids']['next'],
                                                  limit=limit)
        response_page_2_ids = [m['stories_id'] for m in response_page_2['stories']]
        # verify no duplicated media_ids across pages
        combined_ids = set(response_page_1_ids+response_page_2_ids)
        self.assertEqual(len(response_page_1_ids)+len(response_page_2_ids), len(combined_ids))

    def testTopicStoryListLimit(self):
        response1 = self._mc.topicStoryList(self.TOPIC_ID)
        self.assertEqual(len(response1['stories']), 20)
        response2 = self._mc.topicStoryList(self.TOPIC_ID, limit=67)
        self.assertEqual(len(response2['stories']), 67)

    def testTopicStoryListSortInlink(self):
        response = self._mc.topicStoryList(self.TOPIC_ID, limit=500, sort='inlink')
        last_inlink_count = 1000000000000
        for story in response['stories']:
            self.assertLessEqual(story['inlink_count'], last_inlink_count)
            last_inlink_count = story['inlink_count']

    def testTopicStoryListSortFacebook(self):
        response = self._mc.topicStoryList(self.TOPIC_ID, limit=500, sort='facebook')
        last_inlink_count = 1000000000000
        for story in response['stories']:
            self.assertLessEqual(story['facebook_share_count'], last_inlink_count)
            last_inlink_count = story['facebook_share_count']

    def testTopicStoryListSortTwitter(self):
        response = self._mc.topicStoryList(self.TOPIC_ID, limit=500, sort='twitter')
        last_inlink_count = 1000000000000
        for story in response['stories']:
            if (last_inlink_count is not None) and ('normalized_tweet_count' in story) and (story['normalized_tweet_count'] is not None):
                self.assertLessEqual(story['normalized_tweet_count'], last_inlink_count)
                last_inlink_count = story['normalized_tweet_count']


class TopicStoryLinksTest(AdminApiBaseTest):

    def testStoryLinks(self):
        results = self._mc.topicStoryLinks(TEST_TOPIC_ID)
        self.assertGreater(len(results['links']), 0)

    def testStoryLinksLimit(self):
        results = self._mc.topicStoryLinks(TEST_TOPIC_ID, limit=100)
        self.assertEqual(len(results['links']), 100)

    def testStoryLinksPaging(self):
        results = self._mc.topicStoryLinks(TEST_TOPIC_ID)
        self.assertGreater(len(results['links']), 0)
        results2 = self._mc.topicStoryLinks(TEST_TOPIC_ID, link_id=results['link_ids']['next'])
        self.assertGreater(len(results2['links']), 0)


class AdminTopicStoryCountTest(AdminApiBaseTest):
    TOPIC_ID = 1

    def testTopicStoryCount(self):
        response = self._mc.topicStoryCount(self.TOPIC_ID)
        self.assertIn('count', response)
        self.assertGreater(response['count'], 0)
        response2 = self._mc.topicStoryCount(self.TOPIC_ID, q='Obama')
        self.assertIn('count', response2)
        self.assertGreater(response2['count'], 0)
        self.assertGreater(response['count'], response2['count'])


class AdminTopicMediaListTest(AdminApiBaseTest):
    TOPIC_ID = 1

    def testTopicMediaList(self):
        response = self._mc.topicMediaList(self.TOPIC_ID)
        self.assertIn('link_ids', response)
        self.assertIn('media', response)
        for media in response['media']:
            self.assertIn('media_id', media)

    def testTopicMediaListMetadata(self):
        response = self._mc.topicMediaList(self.TOPIC_ID)
        for media in response['media']:
            self.assertIn("pub_country", media['metadata'])
            self.assertIn("pub_state", media['metadata'])
            self.assertIn("language", media['metadata'])
            self.assertIn("about_country", media['metadata'])
            self.assertIn("media_type", media['metadata'])

    def testTopicMediaListLimit(self):
        response = self._mc.topicMediaList(self.TOPIC_ID)
        self.assertEqual(len(response['media']), 20)
        response = self._mc.topicMediaList(self.TOPIC_ID, limit=31)
        self.assertEqual(len(response['media']), 31)

    def testTopicMediaListPaging(self):
        limit = 10
        response_page_1 = self._mc.topicMediaList(self.TOPIC_ID, limit=limit)
        response_page_1_ids = [m['media_id'] for m in response_page_1['media']]
        self.assertEqual(len(response_page_1['media']), 10)
        self.assertIn('link_ids', response_page_1)
        response_page_2 = self._mc.topicMediaList(self.TOPIC_ID, link_id=response_page_1['link_ids']['next'],
                                                  limit=limit)
        response_page_2_ids = [m['media_id'] for m in response_page_2['media']]
        # verify no duplicated media_ids across pages
        combined_ids = set(response_page_1_ids+response_page_2_ids)
        self.assertEqual(len(response_page_1_ids)+len(response_page_2_ids), len(combined_ids))

    def testTopicMediaListSortInlink(self):
        response = self._mc.topicMediaList(self.TOPIC_ID, sort='inlink')
        last_count = 1000000000000
        for media in response['media']:
            self.assertLessEqual(media['inlink_count'], last_count)
            last_count = media['inlink_count']

    def testTopicMediaListSortFacebook(self):
        response = self._mc.topicMediaList(self.TOPIC_ID, sort='facebook')
        last_count = 1000000000000
        for media in response['media']:
            if (last_count is not None) and (media['facebook_share_count'] is not None):
                self.assertLessEqual(media['facebook_share_count'], last_count)
                last_count = media['facebook_share_count']

    def testTopicMediaListSortTwitter(self):
        response = self._mc.topicMediaList(self.TOPIC_ID, sort='twitter')
        last_count = 1000000000000
        for media in response['media']:
            if (last_count is not None) and ('simple_tweet_count' in media) and (media['simple_tweet_count'] is not None):
                self.assertLessEqual(media['simple_tweet_count'], last_count)
                last_count = media['simple_tweet_count']


class TopicMediaLinksText(AdminApiBaseTest):

    def testMediaLinks(self):
        results = self._mc.topicMediaLinks(TEST_TOPIC_ID)
        self.assertGreater(len(results['links']), 0)

    def testMediaLinksLimit(self):
        results = self._mc.topicMediaLinks(TEST_TOPIC_ID, limit=100)
        self.assertEqual(len(results['links']), 100)

    def testMediaLinksPaging(self):
        results = self._mc.topicMediaLinks(TEST_TOPIC_ID)
        self.assertGreater(len(results['links']), 0)
        results2 = self._mc.topicMediaLinks(TEST_TOPIC_ID, link_id=results['link_ids']['next'])
        self.assertGreater(len(results2['links']), 0)


class AdminTopicWordCountTest(AdminApiBaseTest):
    TOPIC_ID = 1

    def testResults(self):
        term_freq = self._mc.topicWordCount(self.TOPIC_ID)
        self.assertEqual(len(term_freq), 500)
        self.assertIn(term_freq[1]['term'], [u'zimmerman', u'trayvon', u'martin'])  # based on the random sample it can change

    def testSort(self):
        term_freq = self._mc.topicWordCount(self.TOPIC_ID)
        # verify sorted in desc order
        last_count = 10000000000
        for freq in term_freq:
            self.assertGreaterEqual(last_count, freq['count'])
            last_count = freq['count']

    def testNumWords(self):
        term_freq = self._mc.topicWordCount(self.TOPIC_ID)
        self.assertEqual(len(term_freq), 500)
        term_freq = self._mc.topicWordCount(self.TOPIC_ID, num_words=52)
        self.assertEqual(len(term_freq), 52)
        term_freq = self._mc.topicWordCount(self.TOPIC_ID, num_words=1000)
        self.assertGreater(len(term_freq), 500)


class AdminTopicMediaMapTest(AdminApiBaseTest):

    def testMediaMap(self):
        results = self._mc.topicMediaMap(TEST_TOPIC2_ID)
        self.assertIn('gexf', str(results))


class TopicSeedQueryTest(AdminApiBaseTest):

    def testSeedQuery(self):
        results = self._mc.topicAddSeedQuery(TEST_TOPIC3_ID, mediacloud.api.TOPIC_PLATFORM_TWITTER,
                                             mediacloud.api.TOPIC_SOURCE_ARCHIVE, 'rahul')
        self.assertIn('topic_seed_query', results)
        self.assertIn('topic_seed_queries_id', results['topic_seed_query'])
        results = self._mc.topicRemoveSeedQuery(TEST_TOPIC3_ID, results['topic_seed_query']['topic_seed_queries_id'])
        self.assertEqual(results['success'], 1)
