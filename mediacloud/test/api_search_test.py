import datetime as dt
import os
from unittest import TestCase

import mediacloud.api


class DirectoryTest(TestCase):

    START_DATE = dt.date(2023, 11, 1)
    END_DATE = dt.date(2023, 12, 1)

    def setUp(self):
        self._mc_api_key = os.getenv("MC_API_TOKEN")
        self._search = mediacloud.api.SearchApi(self._mc_api_key)

    def test_story_count(self):
        results = self._search.story_count(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                           collection_ids=[34412234], source_ids=[20775])
        assert 'relevant' in results
        assert results['relevant'] > 0
        assert 'total' in results
        assert results['total'] > 0
        assert results['relevant'] <= results['total']

    def test_story_count_over_time(self):
        results = self._search.story_count_over_time(query="weather", start_date=self.START_DATE,
                                                     end_date=self.END_DATE, collection_ids=[34412234])
        assert len(results) == (self.END_DATE - self.START_DATE).days + 1
        for day in results:
            assert 'date' in day
            assert 'count' in day
            assert 'total_count' in day
            assert day['count'] <= day['total_count']
            assert 'ratio' in day
            assert day['ratio'] < 1

    def test_story_list(self):
        assert True

    def test_story(self):
        # Note: Expected to fail right now
        story_id = 'eebfb686618e34a9bc6e87e87e90c54b'  # not sure this is a valid id (got it by md5 hashing staging-news-search-query.tarbell.mediacloud.org)
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
                                     end_date=self.END_DATE, collection_ids=[34412234],
                                     limit=10)
        assert len(results) > 0

    def test_sources(self):
        results = self._search.sources(query="weather", start_date=self.START_DATE,
                                       end_date=self.END_DATE, collection_ids=[34412234])
        assert len(results) > 0
        last_count = 10000000000
        for s in results:
            assert 'name' in s
            assert 'count' in s
            assert s['count'] > 0
            assert s['count'] <= last_count
            assert 'ratio' in s
            last_count = s['count']

    def test_languages(self):
        results = self._search.languages(query="weather", start_date=self.START_DATE,
                                         end_date=self.END_DATE, collection_ids=[34412234])
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
