import datetime

from mediacloud.test.basetest import ApiBaseTest
import mediacloud

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

    def testPublishDateDefaults(self):
        start_date = datetime.date(2014, 06, 02)
        end_date = datetime.date(2014, 06, 03)
        date_query_default = self._mc.publish_date_query(start_date, end_date)
        self.assertEqual(date_query_default, "publish_day:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z}")

    def testPublishDateField(self):
        start_date = datetime.date(2014, 06, 02)
        end_date = datetime.date(2014, 06, 03)
        date_query_default = self._mc.publish_date_query(start_date, end_date)
        self.assertEqual(date_query_default, "publish_day:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z}")
        date_query_default = self._mc.publish_date_query(start_date, end_date, field='publish_week')
        self.assertEqual(date_query_default, "publish_week:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z}")

    def testPublishDateInslusivity(self):
        start_date = datetime.date(2014, 06, 02)
        end_date = datetime.date(2014, 06, 03)

        date_query_inclusive_exclusive = self._mc.publish_date_query(start_date, end_date, start_date_inclusive=True,
                                                                     end_date_inclusive=False)
        self.assertEqual(date_query_inclusive_exclusive, "publish_day:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z}")

        date_query_inclusive_inclusive = self._mc.publish_date_query(start_date, end_date, start_date_inclusive=True,
                                                                     end_date_inclusive=True)
        self.assertEqual(date_query_inclusive_inclusive, "publish_day:[2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z]")

        date_query_exclusive_inclusive = self._mc.publish_date_query(start_date, end_date, start_date_inclusive=False,
                                                                     end_date_inclusive=True)
        self.assertEqual(date_query_exclusive_inclusive, "publish_day:{2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z]")

        date_query_exclusive_exclusive = self._mc.publish_date_query(start_date, end_date, start_date_inclusive=False,
                                                                     end_date_inclusive=False)
        self.assertEqual(date_query_exclusive_exclusive, "publish_day:{2014-06-02T00:00:00Z TO 2014-06-03T00:00:00Z}")


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


class AdminApiChunkifyTest(ApiBaseTest):

    def testChunkify(self):
        chunk_size = 50
        data = [x for x in range(0, 507)]
        chunked = mediacloud.api._chunkify(data, chunk_size)
        self.assertEqual(11, len(chunked))
        for x in range(0, 10):
            self.assertEqual(chunk_size, len(chunked[x]))
        self.assertEqual(7, len(chunked[10]))
