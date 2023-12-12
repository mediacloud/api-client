import os
from unittest import TestCase

import mediacloud.api
from mediacloud.error import MCException


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
