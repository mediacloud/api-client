import datetime as dt
import os
from unittest import TestCase

import mediacloud.api

COLLECTION_US_NATIONAL = 34412234
AU_BROADCAST_COMPANY = 20775
TOMORROW_TIME = dt.datetime.today() + dt.timedelta(days=1)


class SearchTest(TestCase):

    START_DATE = dt.date(2023, 11, 1)
    END_DATE = dt.date(2023, 12, 1)

    def setUp(self):
        self._mc_api_key = os.getenv("MC_API_TOKEN")
        self._search = mediacloud.api.SearchApi(self._mc_api_key)
        self._mc_api_admin_key = os.getenv("MC_API_ADMIN_TOKEN")
        self._admin_search = mediacloud.api.SearchApi(self._mc_api_admin_key)

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
        story_id = '9f734354744a651e9b99e4fcd93ee9eaee12ed134ba74dcda13b30234f528535'
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
        page, _ = self._admin_search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                                collection_ids=[COLLECTION_US_NATIONAL])
        for story in page:
            assert 'text' not in story
        page, _ = self._admin_search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                                expanded=True, collection_ids=[COLLECTION_US_NATIONAL])
        for story in page:
            assert 'text' in story
            assert len(story['text']) > 0

    def test_story_list_sort_order(self):
        # desc
        page, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                          collection_ids=[COLLECTION_US_NATIONAL])
        last_date = TOMORROW_TIME
        for story in page:
            assert 'indexed_date' in story
            assert story['indexed_date'] <= last_date
            last_date = story['indexed_date']
        # asc
        page, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                          collection_ids=[COLLECTION_US_NATIONAL], sort_order='asc')
        a_long_time_ago = dt.datetime(2000, 1, 1, 0, 0, 0)
        last_date = a_long_time_ago
        for story in page:
            assert 'indexed_date' in story
            assert story['indexed_date'] >= last_date
            last_date = story['indexed_date']

    def test_search_by_indexed_date(self):
        # compare results with indexed_date clause to those without it
        results1 = self._search.story_count(query="weather", start_date=self.START_DATE, end_date=self.END_DATE)
        assert results1['total'] > 0
        results2 = self._search.story_count(query="weather and indexed_date:[{} TO {}]".format(
            self.START_DATE.isoformat(), self.END_DATE.isoformat()),
            start_date=self.START_DATE, end_date=self.END_DATE)
        assert results2['total'] > 0
        assert results1['total'] == results2['total']
        assert results1['relevant'] != results2['relevant']
        assert results1['relevant'] > results2['relevant']  # indexed_date clause sould be more narrow

    def test_verify_story_time_formats(self):
        # indexed_date should have time component
        page, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                          collection_ids=[COLLECTION_US_NATIONAL], page_size=100)
        for story in page:
            assert 'publish_date' in story
            assert isinstance(story['publish_date'], dt.date)
            assert 'indexed_date' in story
            assert isinstance(story['indexed_date'], dt.datetime)

    def test_story_list_page_size(self):
        # test valid number
        page, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                          collection_ids=[COLLECTION_US_NATIONAL], page_size=103)
        assert len(page) == 103

    def test_source_ids_filter(self):
        results = self._search.sources(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                       source_ids=[AU_BROADCAST_COMPANY])
        assert len(results) == 1
        assert results[0]['count'] > 0
        assert results[0]['source'] == "abc.net.au"
        results, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                             source_ids=[AU_BROADCAST_COMPANY])
        assert len(results) > 0
        for s in results:
            assert s['media_url'] == "abc.net.au"
            assert s['media_name'] == "abc.net.au"

    def test_collection_ids_filter(self):
        # first get all domains in collection
        directory_api = mediacloud.api.DirectoryApi(self._mc_api_key)
        limit = 1000
        response = directory_api.source_list(collection_id=COLLECTION_US_NATIONAL, limit=limit)
        sources_in_collection = response['results']
        assert len(sources_in_collection) > 200
        domains = [s['name'] for s in sources_in_collection]
        assert len(domains) == len(sources_in_collection)
        # now check sources to see they're all in collection list of domains
        results = self._search.sources(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                       collection_ids=[COLLECTION_US_NATIONAL])
        for s in results:
            assert s['source'] in domains
        # now check urls for a page of matches and make sure they're all in collection list of domains
        results, _ = self._search.story_list(query="weather", start_date=self.START_DATE, end_date=self.END_DATE,
                                             collection_ids=[COLLECTION_US_NATIONAL])
        assert len(results) > 0
        for s in results:
            assert s['media_url'] in domains


class SearchSyntaxTest(TestCase):

    START_DATE = dt.date(2024, 1, 1)
    END_DATE = dt.date(2024, 1, 30)

    def setUp(self):
        self._mc_api_key = os.getenv("MC_API_TOKEN")
        self._search = mediacloud.api.SearchApi(self._mc_api_key)

    def _count_query(self, query: str) -> int:
        return self._search.story_count(query=query, start_date=self.START_DATE, end_date=self.END_DATE,
                                        collection_ids=[COLLECTION_US_NATIONAL])['relevant']

    def test_title_search(self):
        all_results = self._count_query(query="biden")
        assert all_results > 0
        title_results = self._count_query(query="article_title:biden")
        assert title_results > 0
        assert all_results >= title_results

    def test_single_char_wildcard_search(self):
        women_count = self._count_query(query="women")
        assert women_count > 0
        woman_count = self._count_query(query="woman")
        assert woman_count > 0
        wildcarded_count = self._count_query(query="wom?n")
        assert wildcarded_count > 0
        assert wildcarded_count >= women_count
        assert wildcarded_count >= woman_count

    def test_multiple_char_wildcard_search(self):
        women_count = self._count_query(query="women")
        assert women_count > 0
        woman_count = self._count_query(query="woman")
        assert woman_count > 0
        wildcarded_count = self._count_query(query="wom*n")
        assert wildcarded_count > 0
        assert wildcarded_count >= women_count
        assert wildcarded_count >= woman_count
        wildcarded2_count = self._count_query(query="wom*")
        assert wildcarded2_count > 0
        assert wildcarded2_count >= women_count
        assert wildcarded2_count >= woman_count

    def test_or_search(self):
        women_count = self._count_query(query="women")
        assert women_count > 0
        woman_count = self._count_query(query="woman")
        assert woman_count > 0
        ord_count = self._count_query(query="(woman OR women)")  # NOTE: this needs parentheses
        assert ord_count >= women_count
        assert ord_count >= woman_count

    def test_and_search(self):
        women_count = self._count_query(query="women")
        assert women_count > 0
        woman_count = self._count_query(query="woman")
        assert woman_count > 0
        anded_count = self._count_query(query="woman AND women")
        assert anded_count <= women_count
        assert anded_count <= woman_count

    def test_proximity_search(self):
        woman_count = self._count_query(query="woman")
        killed_count = self._count_query(query="killed")
        and_count = self._count_query(query="woman AND killed")
        proximity_count = self._count_query(query='"woman killed"~10')
        assert woman_count > and_count
        assert killed_count > and_count
        assert proximity_count < and_count

    def test_default_search(self):
        default_count = self._count_query(query="banana monkey")
        and_count = self._count_query(query="banana AND monkey")
        assert default_count > 0
        assert and_count > 0
        assert default_count == and_count

    def test_negation_source(self):
        all_count = self._count_query(query="gaza")
        not_count = self._count_query(query="gaza NOT hamas")
        minus_count = self._count_query(query="gaza -hamas")
        assert all_count > 0
        assert not_count > 0
        assert not_count < all_count
        assert minus_count == not_count
