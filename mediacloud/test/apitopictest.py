from mediacloud.test.basetest import AdminApiBaseTest

TEST_TOPIC_ID = 1537    # climate change topic
TEST_TOPIC2_ID = 1019   # common core


class ApiTopicTest(AdminApiBaseTest):

    def testTopic(self):
        topic = self._mc.topic(TEST_TOPIC_ID)
        self.assertEqual(int(topic['topics_id']), 1537)
        self.assertEqual(topic['name'], 'Climate Change 2016')

    def testTopicList(self):
        # verify it pulls some
        topic_list = self._mc.topicList()
        self.assertTrue(len(topic_list) > 1)

    def testTopicListPublic(self):
        topic_list = self._mc.topicList(public=True)
        self.assertTrue(len(topic_list) > 1)
        for topic in topic_list['topics']:
            self.assertEqual(topic['is_public'], 1)

    def testTopicListName(self):
        to_match = "common"
        topic_list = self._mc.topicList(name=to_match)
        self.assertTrue(len(topic_list) > 1)
        for topic in topic_list['topics']:
            self.assertTrue(to_match in topic['name'].lower())

    def testTopicListPaging(self):
        # verify second page doesn't contain any ids from the first page
        topic_list_page_1 = self._mc.topicList()
        page_1_ids = [t['topics_id'] for t in topic_list_page_1['topics']]
        self.assertTrue(len(topic_list_page_1) > 1)
        topic_list_page_2 = self._mc.topicList(topic_list_page_1['link_ids']['next'])
        self.assertTrue(len(topic_list_page_2) > 1)
        page_2_ids = [t['topics_id'] for t in topic_list_page_2['topics']]
        for page_2_topic_id in page_2_ids:
            self.assertTrue(page_2_topic_id not in page_1_ids)


class ApiTopicSnapshotTest(AdminApiBaseTest):

    def testTopicSnapshotList(self):
        # make sure it works
        snapshots = self._mc.topicSnapshotList(TEST_TOPIC_ID)
        self.assertEqual(len(snapshots), 1)


class ApiTopicSpiderTest(AdminApiBaseTest):

    def testTopicSpiderStatus(self):
        results = self._mc.topicSpiderStatus(TEST_TOPIC2_ID)
        self.assertTrue('job_states' in results)

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
        self.assertTrue(len(timespans) > 1)


class AdminTopicStoryListTest(AdminApiBaseTest):
    TOPIC_ID = 1

    def testTopicStoryListFacebookData(self):
        response = self._mc.topicStoryListFacebookData(self.TOPIC_ID)
        self.assertEqual(len(response['counts']), 20)
        for story in response['counts']:
            self.assertTrue('facebook_api_collect_date' in story)
            self.assertTrue('facebook_comment_count' in story)
            self.assertTrue('facebook_share_count' in story)
            self.assertTrue('stories_id' in story)

    def testTopicStoryList(self):
        response = self._mc.topicStoryList(self.TOPIC_ID)
        self.assertEqual(len(response['stories']), 20)
        for story in response['stories']:
            self.assertTrue('date_is_reliable' in story)

    def testTopicStoryListPaging(self):
        limit = 50
        response_page_1 = self._mc.topicStoryList(self.TOPIC_ID, limit=limit)
        response_page_1_ids = [m['stories_id'] for m in response_page_1['stories']]
        self.assertEqual(len(response_page_1['stories']), 50)
        self.assertTrue('link_ids' in response_page_1)
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

    def testTopicStoryListSortBitly(self):
        response = self._mc.topicStoryList(self.TOPIC_ID, limit=500, sort='bitly')
        last_bitly_count = 1000000000000
        for story in response['stories']:
            self.assertTrue(story['bitly_click_count'] <= last_bitly_count)
            last_bitly_count = story['bitly_click_count']

    def testTopicStoryListSortInlink(self):
        response = self._mc.topicStoryList(self.TOPIC_ID, limit=500, sort='inlink')
        last_inlink_count = 1000000000000
        for story in response['stories']:
            self.assertTrue(story['inlink_count'] <= last_inlink_count)
            last_inlink_count = story['inlink_count']

    def testTopicStoryListSortFacebook(self):
        response = self._mc.topicStoryList(self.TOPIC_ID, limit=500, sort='facebook')
        last_inlink_count = 1000000000000
        for story in response['stories']:
            self.assertTrue(story['facebook_share_count'] <= last_inlink_count)
            last_inlink_count = story['facebook_share_count']

    def testTopicStoryListSortTwitter(self):
        response = self._mc.topicStoryList(self.TOPIC_ID, limit=500, sort='twitter')
        last_inlink_count = 1000000000000
        for story in response['stories']:
            self.assertTrue(story['normalized_tweet_count'] <= last_inlink_count)
            last_inlink_count = story['normalized_tweet_count']


class AdminTopicStoryCountTest(AdminApiBaseTest):
    TOPIC_ID = 1

    def testTopicStoryCount(self):
        response = self._mc.topicStoryCount(self.TOPIC_ID)
        self.assertTrue('count' in response)
        self.assertTrue(response['count'] > 0)
        response2 = self._mc.topicStoryCount(self.TOPIC_ID, q='Obama')
        self.assertTrue('count' in response2)
        self.assertTrue(response2['count'] > 0)
        self.assertTrue(response['count'] > response2['count'])


class AdminTopicMediaListTest(AdminApiBaseTest):
    TOPIC_ID = 1

    def testTopicMediaList(self):
        response = self._mc.topicMediaList(self.TOPIC_ID)
        self.assertTrue('link_ids' in response)
        self.assertTrue('media' in response)
        for media in response['media']:
            self.assertTrue('media_id' in media)

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
        self.assertTrue('link_ids' in response_page_1)
        response_page_2 = self._mc.topicMediaList(self.TOPIC_ID, link_id=response_page_1['link_ids']['next'],
                                                  limit=limit)
        response_page_2_ids = [m['media_id'] for m in response_page_2['media']]
        # verify no duplicated media_ids across pages
        combined_ids = set(response_page_1_ids+response_page_2_ids)
        self.assertEqual(len(response_page_1_ids)+len(response_page_2_ids), len(combined_ids))

    def testTopicMediaListSortSocial(self):
        response = self._mc.topicMediaList(self.TOPIC_ID, sort='bitly')
        last_bitly_count = 1000000000000
        for media in response['media']:
            self.assertTrue(media['bitly_click_count'] <= last_bitly_count)
            last_bitly_count = media['bitly_click_count']

    def testTopicMediaListSortInlink(self):
        response = self._mc.topicMediaList(self.TOPIC_ID, sort='inlink')
        last_inlink_count = 1000000000000
        for media in response['media']:
            self.assertTrue(media['inlink_count'] <= last_inlink_count)
            last_inlink_count = media['inlink_count']

    def testTopicMediaListSortFacebook(self):
        response = self._mc.topicMediaList(self.TOPIC_ID, sort='facebook')
        last_inlink_count = 1000000000000
        for media in response['media']:
            self.assertTrue(media['facebook_share_count'] <= last_inlink_count)
            last_inlink_count = media['facebook_share_count']

    def testTopicMediaListSortTwitter(self):
        response = self._mc.topicMediaList(self.TOPIC_ID, sort='twitter')

class AdminTopicWordCountTest(AdminApiBaseTest):
    TOPIC_ID = 1

    def testResults(self):
        term_freq = self._mc.topicWordCount(self.TOPIC_ID)
        self.assertEqual(len(term_freq), 500)
        self.assertEqual(term_freq[3]['term'], u'george')

    def testSort(self):
        term_freq = self._mc.topicWordCount(self.TOPIC_ID)
        # verify sorted in desc order
        last_count = 10000000000
        for freq in term_freq:
            self.assertTrue(last_count >= freq['count'])
            last_count = freq['count']

    def testNumWords(self):
        term_freq = self._mc.topicWordCount(self.TOPIC_ID)
        self.assertEqual(len(term_freq), 500)
        term_freq = self._mc.topicWordCount(self.TOPIC_ID, num_words=52)
        self.assertEqual(len(term_freq), 52)
        term_freq = self._mc.topicWordCount(self.TOPIC_ID, num_words=1000)
        self.assertEqual(len(term_freq), 1000)


class AdminTopicSentenceCountTest(AdminApiBaseTest):
    TOPIC_ID = 1

    def testSentenceCount(self):
        results = self._mc.topicSentenceCount(self.TOPIC_ID)
        self.assertTrue(int(results['count']) > 1000)
        results = self._mc.topicSentenceCount(self.TOPIC_ID, snapshots_id=365)
        self.assertTrue(int(results['count']) > 1000)

    def testSentenceCountSplit(self):
        results = self._mc.topicSentenceCount(self.TOPIC_ID, q='*', fq='*', split=True,
                                              split_start_date='2013-01-01', split_end_date='2016-01-01')
        self.assertEqual(results['split']['gap'], '+7DAYS')
        self.assertEqual(len(results['split']), 160)


class AdminTopicMediaMapTest(AdminApiBaseTest):

    def testMediaMap(self):
        results = self._mc.topicMediaMap(TEST_TOPIC2_ID)
        self.assertTrue('gexf' in results)
