"""
Minimal tests for DirectoryManagementApi (mediacloud.mgmt).

Live tests follow the same two-token pattern as api_search_test: MC_API_TOKEN (normal) and
MC_API_ADMIN_TOKEN (privileged). Staging integration requires both to be set.
"""
import os
import unittest
from unittest.mock import MagicMock, patch

import pytest

from mediacloud.error import APIResponseError
from mediacloud.mgmt import DirectoryManagementApi

# Directory management integration checks against Tarbell staging (see mediacloud.org deployment).
MCWEB_STAGING_API_BASE = "https://mcweb-staging.tarbell.mediacloud.org/api/"


class DirectoryManagementApiUnitTest(unittest.TestCase):
    """Pure unit tests (no network)."""

    def setUp(self):
        self._api = DirectoryManagementApi("test-token")

    def test_source_collection_delete_uses_http_delete(self):
        with patch.object(self._api, "_query", autospec=True) as mock_query:
            mock_query.return_value = MagicMock(status_code=204)
            self._api.source_collection_delete(source_id=42, collection_id=99)
        mock_query.assert_called_once_with(
            "sources/sources-collections/42/?collection_id=99",
            None,
            "DELETE",
        )

    def test_collection_create_requires_name(self):
        with self.assertRaises(ValueError):
            self._api.collection_create(notes="only notes")

    def test_collection_create_rejects_unknown_kwargs(self):
        with self.assertRaises(ValueError) as ctx:
            self._api.collection_create(name="x", bogus_field=1)
        self.assertIn("Unknown collection params", str(ctx.exception))

    def test_collection_update_rejects_unknown_kwargs(self):
        with self.assertRaises(ValueError):
            self._api.collection_update(collection_id=1, name="ok", extra=2)


@pytest.mark.skipif(not os.getenv("MC_API_TOKEN"), reason="MC_API_TOKEN not set")
class DirectoryManagementApiLiveTest(unittest.TestCase):
    """Smoke against the configured API (default: production search host)."""

    def setUp(self):
        self._mgmt = DirectoryManagementApi(os.environ["MC_API_TOKEN"])

    def test_user_profile(self):
        profile = self._mgmt.user_profile()
        self.assertIsInstance(profile, dict)
        self.assertGreater(len(profile), 0)


@pytest.mark.skipif(
    not os.getenv("MC_API_TOKEN") or not os.getenv("MC_API_ADMIN_TOKEN"),
    reason="MC_API_TOKEN and MC_API_ADMIN_TOKEN required (same as api_search_test)",
)
class DirectoryManagementStagingIntegrationTest(unittest.TestCase):
    """
    Live checks against https://mcweb-staging.tarbell.mediacloud.org/ (staging API).

    Uses MC_API_TOKEN for the 403 assertion (normal key must not be allowed to create
    collections). Uses MC_API_ADMIN_TOKEN for a parallel read sanity check on staging.
    """

    def setUp(self):
        self._mc_api_key = os.environ["MC_API_TOKEN"]
        self._mc_api_admin_key = os.environ["MC_API_ADMIN_TOKEN"]
        if self._mc_api_key == self._mc_api_admin_key:
            self.skipTest("MC_API_TOKEN and MC_API_ADMIN_TOKEN must differ for staging mgmt tests")

        self._prev_base = DirectoryManagementApi.BASE_API_URL
        DirectoryManagementApi.BASE_API_URL = MCWEB_STAGING_API_BASE
        self.addCleanup(self._restore_base_url)
        self._mgmt = DirectoryManagementApi(self._mc_api_key)
        self._admin_mgmt = DirectoryManagementApi(self._mc_api_admin_key)

    def _restore_base_url(self):
        DirectoryManagementApi.BASE_API_URL = self._prev_base

    def test_staging_user_profile_reaches_server(self):
        """Sanity: normal token is accepted on staging before we assert on management errors."""
        profile = self._mgmt.user_profile()
        self.assertIsInstance(profile, dict)
        self.assertGreater(len(profile), 0)

    def test_staging_admin_user_profile_reaches_server(self):
        """Sanity: admin token is accepted on staging (same pattern as BaseSearchTest)."""
        profile = self._admin_mgmt.user_profile()
        self.assertIsInstance(profile, dict)
        self.assertGreater(len(profile), 0)

    def test_non_admin_collection_create_is_forbidden_on_staging(self):
        with self.assertRaises(APIResponseError) as ctx:
            self._mgmt.collection_create(
                name="api-client integration (should not be created)",
                notes="DirectoryManagementStagingIntegrationTest",
            )
        self.assertEqual(ctx.exception.response.status_code, 403)
