import datetime

from mediacloud.test.basetest import ApiBaseTest
import mediacloud
import mediacloud.api


class StatsTest(ApiBaseTest):

    def testStats(self):
        stats = self._mc.stats()
        data_keys = [
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
            self.assertIn(key, stats)


class DatesAsQueryClauseTest(ApiBaseTest):

    def testDateDefaults(self):
        start_date = datetime.date(2014, 6, 2)
        end_date = datetime.date(2014, 6, 3)
        date_query_default = self._mc.dates_as_query_clause(start_date, end_date)
        self.assertEqual(date_query_default, "publish_day:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z]")

    def testDateField(self):
        start_date = datetime.date(2014, 6, 2)
        end_date = datetime.date(2014, 6, 3)
        date_query_default = self._mc.dates_as_query_clause(start_date, end_date)
        self.assertEqual(date_query_default, "publish_day:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z]")
        date_query_default = self._mc.dates_as_query_clause(start_date, end_date, field='publish_week')
        self.assertEqual(date_query_default, "publish_week:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z]")

    def testDateInslusivity(self):
        start_date = datetime.date(2014, 6, 2)
        end_date = datetime.date(2014, 6, 3)

        date_query_inclusive_exclusive = self._mc.dates_as_query_clause(start_date, end_date, start_date_inclusive=True,
                                                                        end_date_inclusive=False)
        self.assertEqual(date_query_inclusive_exclusive, "publish_day:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z}")

        date_query_inclusive_inclusive = self._mc.dates_as_query_clause(start_date, end_date, start_date_inclusive=True,
                                                                        end_date_inclusive=True)
        self.assertEqual(date_query_inclusive_inclusive, "publish_day:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z]")

        date_query_exclusive_inclusive = self._mc.dates_as_query_clause(start_date, end_date, start_date_inclusive=False,
                                                                        end_date_inclusive=True)
        self.assertEqual(date_query_exclusive_inclusive, "publish_day:{2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z]")

        date_query_exclusive_exclusive = self._mc.dates_as_query_clause(start_date, end_date, start_date_inclusive=False,
                                                                        end_date_inclusive=False)
        self.assertEqual(date_query_exclusive_exclusive, "publish_day:{2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z}")


class ApiAllFieldsOptionTest(ApiBaseTest):

    def testAllFieldsOnMedia(self):
        # do a regular query
        media = self._mc.media(1751)
        self.assertNotEqual(media, None)
        self.assertEqual(media['media_id'], 1751)
        self.assertNotIn('foreign_rss_links', media)
        self.assertIn('url', media)
        # do an all fields regular query and verify extra fields are there
        self._mc.setAllFields(True)
        media = self._mc.media(1751)
        self.assertNotEqual(media, None)
        self.assertEqual(media['media_id'], 1751)
        self.assertIn('foreign_rss_links', media)
        self.assertIn('url', media)


class ApiChunkifyTest(ApiBaseTest):

    def testChunkify(self):
        chunk_size = 50
        data = [x for x in range(0, 507)]
        chunked = mediacloud.api._chunkify(data, chunk_size)
        self.assertEqual(11, len(chunked))
        for x in range(0, 10):
            self.assertEqual(chunk_size, len(chunked[x]))
        self.assertEqual(7, len(chunked[10]))


class RemovePrivateInfoTest(ApiBaseTest):

    def testKeyRemoval(self):
        data = {'key': 'SOME_RANDOM_KEY'}
        clean_data = mediacloud.api._remove_private_info(data)
        self.assertEqual(0, len(clean_data.keys()))

    def testPasswordRemoval(self):
        data = {'password': 'MY_AWESOME_PSWD'}
        clean_data = mediacloud.api._remove_private_info(data)
        self.assertEqual(0, len(clean_data.keys()))

    def testListInput(self):
        data = ['sdfd', 'sdfdf', 'sfdf']
        clean_data = mediacloud.api._remove_private_info(data)
        self.assertEqual(len(data), len(clean_data))

    def testRetention(self):
        data = {'password': 'MY_AWESOME_PSWD', 'key': 'SOME_RANDOM_KEY', 'other_stuff': 'THAT_SHOULD_REMAIN'}
        clean_data = mediacloud.api._remove_private_info(data)
        self.assertEqual(1, len(clean_data.keys()))
        self.assertEqual('other_stuff', list(clean_data.keys())[0])
