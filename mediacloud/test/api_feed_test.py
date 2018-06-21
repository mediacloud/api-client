from mediacloud.test.basetest import ApiBaseTest, AdminApiBaseTest

TEST_MEDIA_ID = 362086  # rahulbotics.com - a source that is ok to mess up
TEST_FEED_ID = 1


class ApiFeedTest(AdminApiBaseTest):

    def testFeedInfo(self):
        results = self._mc.feedList(TEST_MEDIA_ID)
        self.assertIn('type', results[0])
        self.assertIn('active', results[0])
        self.assertIsInstance(results[0]['active'], bool)

    def testFeedScrape(self):
        # queue scrape job
        results = self._mc.feedsScrape(TEST_MEDIA_ID)
        self.assertEqual(TEST_MEDIA_ID, int(results['job_state']['media_id']))
        self.assertTrue(results['job_state']['state'] in ['queued', 'completed'])

    def testFeedScrapeStatus(self):
        media = self.randomMedia()
        scrape_status = self._mc.feedsScrapeStatus(media['media_id'])
        self.assertGreater(len(scrape_status['job_states']), 0)


class ApiFeedsTest(ApiBaseTest):

    def testFeed(self):
        media_set = self._mc.feed(TEST_FEED_ID)
        self.assertEqual(media_set['feeds_id'], TEST_FEED_ID)
        self.assertGreater(media_set['media_id'], 0)

    def testFeedList(self):
        first_list = self._mc.feedList(TEST_FEED_ID)
        self.assertEqual(len(first_list), 20)
        second_list = self._mc.feedList(TEST_FEED_ID, int(first_list[19]['feeds_id'])-1)
        self.assertEqual(len(second_list), 20)
        self.assertEqual(first_list[19]['feeds_id'], second_list[0]['feeds_id'])
        longer_list = self._mc.feedList(TEST_FEED_ID, 0, 200)
        self.assertEqual(len(longer_list), 200)

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
