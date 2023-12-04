import datetime as dt
import os
from unittest import TestCase

import mediacloud.api
from mediacloud.error import MCException

TEST_COLLECTION_ID = 34412234  # US -National sources
TEST_SOURCE_ID = 1095  # cnn.com
TEST_FEED_ID = 1


class BaseApiTest(TestCase):

    @staticmethod
    def test_no_token():
        try:
            _ = mediacloud.api.DirectoryApi()
            assert False
        except MCException:
            assert True
        try:
            _ = mediacloud.api.DirectoryApi("")
            assert False
        except MCException:
            assert True

    @staticmethod
    def test_token():
        mc_api_key = os.getenv("MC_API_TOKEN")
        _ = mediacloud.api.DirectoryApi(mc_api_key)
        assert True


class DirectoryTest(TestCase):

    def setUp(self):
        self._mc_api_key = os.getenv("MC_API_TOKEN")
        self._directory = mediacloud.api.DirectoryApi(self._mc_api_key)

    def test_collection_list_search(self):
        name_search = 'nigeria'
        collections = []
        limit = 100
        offset = 0
        while True:
            response = self._directory.collection_list(platform=self._directory.PLATFORM_ONLINE_NEWS, name=name_search,
                                                       limit=limit, offset=offset)
            assert response['count'] != 0
            assert len(response['results']) > 0
            collections += response['results']
            if response['next'] is None:
                break
            offset += limit
        for c in collections:
            assert name_search in c['name'].lower()
            assert c['platform'] == self._directory.PLATFORM_ONLINE_NEWS
        assert len(collections) > 0

    def test_source_list(self):
        sources = []
        limit = 100
        offset = 0
        while True:
            response = self._directory.source_list(collection_id=TEST_COLLECTION_ID, limit=limit, offset=offset)
            assert response['count'] != 0
            assert len(response['results']) > 0
            sources += response['results']
            if response['next'] is None:
                break
            offset += limit
        assert len(sources) > 0

    def test_feed_list(self):
        feeds = []
        limit = 100
        offset = 0
        while True:
            response = self._directory.feed_list(source_id=TEST_SOURCE_ID, limit=limit, offset=offset)
            assert response['count'] != 0
            assert len(response['results']) > 0
            feeds += response['results']
            if response['next'] is None:
                break
            offset += limit
        assert len(feeds) > 0

    def test_feed_list_modified_since(self):
        feeds = []
        limit = 100
        offset = 0
        modified_since = dt.datetime(2022, 8, 1)
        while True:
            response = self._directory.feed_list(source_id=TEST_SOURCE_ID, modified_since=modified_since,
                                                 limit=limit, offset=offset)
            assert response['count'] != 0
            assert len(response['results']) > 0
            feeds += response['results']
            if response['next'] is None:
                break
            offset += limit
        assert len(feeds) > 0

    def test_feed_list_modified_before(self):
        feeds = []
        limit = 100
        offset = 0
        server_version = self._directory.version()
        server_now = server_version['now']

        modified_since = dt.datetime(2022, 8, 1)
        while True:
            response = self._directory.feed_list(source_id=TEST_SOURCE_ID,
                                                 modified_since=modified_since,
                                                 modified_before=server_now,
                                                 limit=limit, offset=offset)
            assert response['count'] != 0
            assert len(response['results']) > 0
            feeds += response['results']
            if response['next'] is None:
                break
            offset += limit
        assert len(feeds) > 0
