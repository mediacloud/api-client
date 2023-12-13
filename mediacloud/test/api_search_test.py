import datetime as dt
import os
from unittest import TestCase

import mediacloud.api

COLLECTION_US_NATIONAL = 34412234
AU_BROADCAST_COMPANY = 20775
TOMORROW = dt.date.today() + dt.timedelta(days=1)


class DirectoryTest(TestCase):

    START_DATE = dt.date(2023, 11, 1)
    END_DATE = dt.date(2023, 12, 1)

    def setUp(self):
        self._mc_api_key = os.getenv("MC_API_TOKEN")
        self._search = mediacloud.api.SearchApi(self._mc_api_key)

    def test_story_count(self):
        results = self._search.story_count(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                           collection_ids=[COLLECTION_US_NATIONAL], source_ids=[AU_BROADCAST_COMPANY])
        assert 'relevant' in results
        assert results['relevant'] > 0
        assert 'total' in results
        assert results['total'] > 0
        assert results['relevant'] <= results['total']

    def test_story_count_over_time(self):
        results = self._search.story_count_over_time(query="weather", start_date=self.START_DATE,
                                                     end_date=self.END_DATE, collection_ids=[COLLECTION_US_NATIONAL])
        assert len(results) == (self.END_DATE - self.START_DATE).days + 1
        for day in results:
            assert 'date' in day
            assert isinstance(day['date'], dt.date)
            assert 'count' in day
            assert 'total_count' in day
            assert day['count'] <= day['total_count']
            assert 'ratio' in day
            assert day['ratio'] < 1

    def test_story(self):
        # Note: Expected to fail right now
        story_id = 'eebfb686618e34a9bc6e87e87e90c54b'  # not sure this is a valid id
        story = self._search.story(story_id)
        assert 'id' in story
        assert story['id'] == story_id
        assert 'title' in story
        assert 'url' in story
        assert 'language' in story
        assert 'publish_date' in story
        assert 'publish_day' in story

    def test_words(self):
        # expected to fail for now
        results = self._search.words(query="weather", start_date=self.START_DATE,
                                     end_date=self.END_DATE, collection_ids=[COLLECTION_US_NATIONAL],
                                     limit=10)
        assert len(results) > 0

    def test_sources(self):
        results = self._search.sources(query="weather", start_date=self.START_DATE,
                                       end_date=self.END_DATE, collection_ids=[COLLECTION_US_NATIONAL])
        assert len(results) > 0
        last_count = 10000000000
        for s in results:
            assert 'source' in s
            assert 'count' in s
            assert s['count'] > 0
            assert s['count'] <= last_count
            last_count = s['count']

    def test_languages(self):
        results = self._search.languages(query="weather", start_date=self.START_DATE,
                                         end_date=self.END_DATE, collection_ids=[COLLECTION_US_NATIONAL])
        assert len(results) > 0
        assert results[0]['language'] == 'en'
        last_ratio = 1
        for lang in results:
            assert 'language' in lang
            assert len(lang['language']) == 2
            assert 'ratio' in lang
            assert lang['ratio'] < 1
            assert lang['ratio'] <= last_ratio
            last_ratio = lang['ratio']
            assert 'value' in lang
            assert lang['value'] > 0

    def test_story_list_paging(self):
        results1, next_page_token1 = self._search.story_list(query="weather", start_date=self.START_DATE,
                                                             end_date=self.END_DATE,
                                                             collection_ids=[COLLECTION_US_NATIONAL])
        assert len(results1) == 1000
        assert next_page_token1 is not None
        results2, next_page_token2 = self._search.story_list(query="weather", start_date=self.START_DATE,
                                                             end_date=self.END_DATE,
                                                             collection_ids=[COLLECTION_US_NATIONAL],
                                                             pagination_token=next_page_token1)
        assert len(results2) == 1000
        assert next_page_token2 is not None
        assert next_page_token1 != next_page_token2

    def test_story_list_expanded(self):
        # note - requires staff API token
        page, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                          collection_ids=[COLLECTION_US_NATIONAL])
        for story in page:
            assert 'text' not in story
        page, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                          expanded=True, collection_ids=[COLLECTION_US_NATIONAL])
        for story in page:
            assert 'text' in story
            assert len(story['text']) > 0

    def test_story_list_sort_order(self):
        # desc
        page, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                          collection_ids=[COLLECTION_US_NATIONAL])
        last_pub_date = TOMORROW
        for story in page:
            assert 'publish_date' in story
            assert story['publish_date'] <= last_pub_date
            last_pub_date = story['publish_date']
        # asc
        page, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                          collection_ids=[COLLECTION_US_NATIONAL], sort_order='asc')
        a_long_time_ago = dt.date(2000, 1, 1)
        last_pub_date = a_long_time_ago
        for story in page:
            assert 'publish_date' in story
            assert story['publish_date'] >= last_pub_date
            last_pub_date = story['publish_date']

    def test_story_list_sort_field(self):
        # publish_date
        page, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                          collection_ids=[COLLECTION_US_NATIONAL])
        last_date = TOMORROW
        for story in page:
            assert 'publish_date' in story
            assert story['publish_date'] <= last_date
            last_date = story['publish_date']
        # indexed date
        page, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                          collection_ids=[COLLECTION_US_NATIONAL], sort_field="indexed_date")
        last_date = TOMORROW
        for story in page:
            assert 'indexed_date' in story
            assert story['indexed_date'] <= last_date
            last_date = story['indexed_date']

    def test_story_list_page_size(self):
        # test valid number
        page, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                          collection_ids=[COLLECTION_US_NATIONAL], page_size=103)
        assert len(page) == 103
