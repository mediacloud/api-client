from mediacloud.test.basetest import ApiBaseTest, AdminApiBaseTest
from mediacloud.test import TEST_USER_EMAIL
from mediacloud.tags import MediaTag, TAG_ACTION_ADD, TAG_ACTION_REMOVE

TESTING_COLLECTION = 9353679
TEST_MEDIA_SUGGEST_REASON = "!!!! TESTING SUGGESTION !!!!"
TEST_TAG_ID_1 = 9172171  # mc-api-test@media.mit.edu:test_tag1


class ApiMediaHealthTest(ApiBaseTest):

    def testMediaHealth(self):
        media = self.randomMedia()
        media_health = self._mc.mediaHealth(media['media_id'])
        self.assertEqual(media_health['media_id'], media['media_id'])
        self.assertIn(media_health['is_healthy'], [True, False])
        self.assertEqual(media_health['coverage_gaps'], len(media_health['coverage_gaps_list']))
        self.assertIn('start_date', media_health)
        self.assertIn('end_date', media_health)

    def testNoHealthData(self):
        health = self._mc.mediaHealth(99999999999)  # ie. an invalid id
        self.assertEqual(0, len(health))


class ApiMediaTest(ApiBaseTest):

    def testMedia(self):
        media = self.randomMedia()
        self.assertIsNotNone(media)
        self.assertIn("is_monitored", media)
        self.assertIn("editor_notes", media)
        self.assertIn("public_notes", media)
        self.assertGreater(len(media['media_source_tags']), 0)
        # and the metadata data that we add in ourselves...
        self.assertIn("pub_country", media['metadata'])
        self.assertIn("pub_state", media['metadata'])
        self.assertIn("language", media['metadata'])
        self.assertIn("about_country", media['metadata'])
        self.assertIn("media_type", media['metadata'])

    def testMediaListSort(self):
        # test default sort
        default_list = self._mc.mediaList(name_like="guardian")
        for idx, m in enumerate(default_list[1:]):
            self.assertTrue(default_list[idx]['media_id'] < m['media_id'],
                            "{}:#{} < {}:#{}?".format(idx, default_list[idx]['media_id'], idx+1, m['media_id']))
        # test num_stories sort
        sorted_list = self._mc.mediaList(name_like="guardian", sort='num_stories')
        for idx, m in enumerate(sorted_list[1:]):
            self.assertGreaterEqual(sorted_list[idx]['num_stories_90'], m['num_stories_90'])
        # test invalid sort options
        try:
            self._mc.mediaList("guardian", sort='!!!!!')
            self.assertTrue(False)
        except ValueError:
            self.assertTrue(True)

    def testMediaListWithName(self):
        matching_list = self._mc.mediaList(name_like='new york times')
        self.assertEqual(len(matching_list), 2)

    def testMediaList(self):
        first_list = self._mc.mediaList()
        for media in first_list:
            self.assertTrue(media['media_id'] > 0)
            self.assertTrue("is_monitored", media)
            self.assertTrue("editor_notes", media)
            self.assertTrue("public_notes", media)
            self.assertTrue(len(media['media_source_tags']) > 0)
            self.assertIn("pub_country", media['metadata'])
            self.assertIn("pub_state", media['metadata'])
            self.assertIn("language", media['metadata'])
            self.assertIn("about_country", media['metadata'])
            self.assertIn("media_type", media['metadata'])
        self.assertNotEqual(first_list, None)
        self.assertEqual(len(first_list), 20)
        last_page_one_media_id = int(first_list[19]['media_id'])-1
        self.assertTrue(last_page_one_media_id > 0)
        second_list = self._mc.mediaList(last_page_one_media_id)
        for media in second_list:
            self.assertTrue(media['media_id'] > last_page_one_media_id)
        self.assertEqual(len(second_list), 20)
        self.assertEqual(first_list[19]['media_id'], second_list[0]['media_id'])
        longer_list = self._mc.mediaList(0, 200)
        self.assertEqual(len(longer_list), 200)

    def testMediaListWithTagId(self):
        matching_list = self._mc.mediaList(tags_id=8875027)  # US MSM
        self.assertTrue(len(matching_list) > 0)

    def testMediaListUnhealthy(self):
        # make sure no overlap in healthy and unhealthy first page of results
        ids = set([m['media_id'] for m in self._mc.mediaList()])
        healthy_ids = set([i for i in ids if self._mc.mediaHealth(i)['is_healthy'] is True])
        unhealthy_ids = set([m['media_id'] for m in self._mc.mediaList(unhealthy=True)])
        intersection = list(healthy_ids & unhealthy_ids)
        self.assertTrue(len(intersection) == 0)


class AdminApiMediaSuggestionsTest(AdminApiBaseTest):

    def testMediaSuggestionMark(self):
        suggest_result = self._mc.mediaSuggest("https://rahulbotics",
                                        name="Rahulbotics",
                                        reason=TEST_MEDIA_SUGGEST_REASON,
                                        tags_ids=[TESTING_COLLECTION])
        self.assertIn('success', suggest_result)
        self.assertEqual(1, suggest_result['success'])
        list_result = self._mc.mediaSuggestionsList()
        for suggestion in list_result:
            if suggestion['reason'] == TEST_MEDIA_SUGGEST_REASON:
                mark_result = self._mc.mediaSuggestionsMark(suggestion['media_suggestions_id'], "rejected",
                                                       "This was a test suggestion, so we are deleting it.")
                self.assertIn('success', mark_result)
                self.assertEqual(1, mark_result['success'])

    def testMediaSuggest(self):
        results = self._mc.mediaSuggest("https://rahulbotics",
                                        name="Rahulbotics",
                                        reason=TEST_MEDIA_SUGGEST_REASON,
                                        tags_ids=[TESTING_COLLECTION])
        self.assertIn('success', results)
        self.assertEqual(1, results['success'])

    def testMediaSuggestionsList(self):
        results = self._mc.mediaSuggestionsList()
        # could be empty, so lets just make sure it is an array
        self.assertIsInstance(results, list)
        for suggestion in results:
            self.assertIn('email', suggestion)


class AdminApiMediaTest(AdminApiBaseTest):

    def testMediaUpdate(self):
        test_media_id = 362086     # rahulbotics.com
        prop_to_change = 'editor_notes'
        updated_prop_value = 'Rahul\'s test domain!'
        original = self._mc.media(test_media_id)
        # update something
        results = self._mc.mediaUpdate(test_media_id, { prop_to_change: updated_prop_value })
        updated = self._mc.media(test_media_id)
        self.assertEqual(updated[prop_to_change], updated_prop_value)
        # set it back and verify
        results = self._mc.mediaUpdate(test_media_id, { prop_to_change: original[prop_to_change] })
        reverted = self._mc.media(test_media_id)
        self.assertEqual(reverted[prop_to_change], original[prop_to_change])

    def testMediaCreateDuplicate(self):
        media_item = {
            'url': "http://nytimes.com",
            'editor_notes': "duplicate for testing",
            'tags_ids': [8875027],
            'name': 'Duplicate New York Times'
        }
        media_to_create = [media_item]
        results = self._mc.mediaCreate(media_to_create)
        self.assertEqual(len(results), len(media_to_create))
        self.assertIn("media_id", results[0])
        self.assertIn("status", results[0])
        self.assertIn("url", results[0])
        self.assertEqual("existing", results[0]['status'])


class AdminApiTaggingContentTest(AdminApiBaseTest):

    def testTagMedia(self):
        media_to_tag = 4451    # ESPN.com
        test_tag_id1 = TEST_TAG_ID_1
        tag_set_name = TEST_USER_EMAIL
        # add a tag
        desired_tag = MediaTag(media_to_tag, tags_id=test_tag_id1, action=TAG_ACTION_ADD)
        response = self._mc.tagMedia([desired_tag])
        self.assertTrue('success' in response)
        self.assertEqual(response['success'], 1)
        # and check it
        story = self._mc.media(media_to_tag)
        tags_on_media = [t['tags_id'] for t in story['media_source_tags'] if t['tag_set'] == tag_set_name]
        self.assertTrue(int(test_tag_id1) in tags_on_media)
        # and remove it
        desired_tag = MediaTag(media_to_tag, tags_id=test_tag_id1, action=TAG_ACTION_REMOVE)
        response = self._mc.tagMedia([desired_tag])
        self.assertTrue('success' in response)
        self.assertEqual(response['success'], 1)
        story = self._mc.media(media_to_tag)
        tags_on_media = [t['tags_id'] for t in story['media_source_tags'] if t['tag_set'] == tag_set_name]
        self.assertEqual(0, len(tags_on_media))