from mediacloud.test.basetest import ApiBaseTest, AdminApiBaseTest
import mediacloud.tags as tags
from mediacloud.test import QUERY_LAST_WEEK, QUERY_LAST_YEAR, QUERY_LAST_MONTH, QUERY_LAST_DECADE, \
    QUERY_ENGLISH_LANGUAGE, load_text_from_fixture
from mediacloud.test import TEST_USER_EMAIL
from mediacloud.tags import StoryTag, TAG_ACTION_REMOVE

TEST_STORY_ID = 2  # a super old, unused story that we can add and remove tags from without causing problems


class ApiStoriesWordMatrixTest(ApiBaseTest):

    def testStoryWordMatrix(self):
        results = self._mc.storyWordMatrix("puppies", [QUERY_LAST_WEEK, QUERY_ENGLISH_LANGUAGE])
        self.assertIn("word_matrix", results)
        self.assertIn("word_list", results)


class ApiStoryTagCountTest(ApiBaseTest):

    def testStoryTagCount(self):
        counts = self._mc.storyTagCount('*', [QUERY_LAST_WEEK, QUERY_ENGLISH_LANGUAGE], tag_sets_id=tags.TAG_SET_CLIFF_PLACES)
        self.assertTrue(len(counts) > 0)
        for tag_count in counts:
            self.assertEqual(tag_count['tag_sets_id'], tags.TAG_SET_CLIFF_PLACES)


class ApiStoryCountTest(ApiBaseTest):

    def testStoryCount(self):
        week_results = self._mc.storyCount('*', QUERY_LAST_WEEK)
        self.assertGreater(week_results['count'], 0)
        year_results = self._mc.storyCount('*', QUERY_LAST_YEAR)
        self.assertGreater(year_results['count'], 0)
        self.assertGreater(year_results['count'], week_results['count'])

    def testUnicodeStoryCount(self):
        # make sure Unicode str doesn't toss an error
        q = u"+( \u5b89\u90e8 ) AND media_id:97659"
        results = self._mc.storyCount(q, QUERY_LAST_YEAR)
        self.assertIsNotNone(results)

    def testStoryCountSplit(self):
        results = self._mc.storyCount('*', QUERY_LAST_WEEK, split=True)
        self.assertEqual(len(results['counts']), 8)
        results = self._mc.storyCount('*', QUERY_LAST_MONTH, split=True, split_period='week')
        self.assertEqual(len(results['counts']), 5)
        results = self._mc.storyCount('*', QUERY_LAST_YEAR, split=True, split_period='month')
        self.assertEqual(len(results['counts']), 13)
        results = self._mc.storyCount('*', QUERY_LAST_DECADE, split=True, split_period='year')
        self.assertEqual(len(results['counts']), 11)


class ApiStoryTest(ApiBaseTest):

    def testStory(self):
        story = self.recentStory()
        self.assertEqual(int(story['stories_id']), story['stories_id'])
        self.assertGreater(story['media_id'], 0)
        self.assertNotIn('story_sentences', story)
        self.assertNotIn('story_text', story)
        self.assertNotIn('is_fully_extracted', story)

    def testStoryPublic(self):
        story = self.recentStory()
        self.assertGreater(story['media_id'], 0)
        self.assertNotIn('story_sentences', story)
        self.assertIn('language', story)
        self.assertIn('title', story)

    def testStoryRawCliffResults(self):
        story = self.recentStory()
        cliff_results = self._mc.storyRawCliffResults([story['stories_id']])
        self.assertEqual(len(cliff_results), 1)
        self.assertEqual(cliff_results[0]['stories_id'], story['stories_id'])
        self.assertIn('results', cliff_results[0]['cliff'])
        self.assertIn('organizations', cliff_results[0]['cliff']['results'])

    def testStoryRawNytThemeResults(self):
        story = self.recentStory()
        nyt_theme_results = self._mc.storyRawNytThemeResults([story['stories_id']])
        self.assertEqual(len(nyt_theme_results), 1)
        self.assertEqual(nyt_theme_results[0]['stories_id'], story['stories_id'])
        self.assertIn('descriptors600', nyt_theme_results[0]['nytlabels'])


class AdminApiStoryTest(AdminApiBaseTest):

    def testStoryWithSentences(self):
        story = self.recentStory()
        story = self._mc.story(story['stories_id'], sentences=True)
        self.assertEqual(int(story['stories_id']), story['stories_id'])
        self.assertIn('story_sentences', story)
        self.assertNotIn('story_text', story)
        self.assertNotIn('is_fully_extracted', story)

    def testStoryWithText(self):
        story = self.recentStory()
        story = self._mc.story(story['stories_id'], text=True)
        self.assertEqual(int(story['stories_id']), story['stories_id'])
        self.assertNotIn('story_sentences', story)
        self.assertIn('story_text', story)
        self.assertIn('is_fully_extracted', story)

    def testStoryUpdate(self):
        test_story_id = 27456565    # picked randomly
        # check the story has a language
        story = self._mc.story(test_story_id)
        original_language = story['language']
        self.assertEqual(original_language, 'en')
        # change it to spanish
        results = self._mc.storyUpdate(test_story_id, language='es')
        self.assertEqual(results['success'], 1)
        story = self._mc.story(test_story_id)
        self.assertEqual(story['language'], 'es')
        # and set it back
        results = self._mc.storyUpdate(test_story_id, language=original_language)
        self.assertEqual(results['success'], 1)
        story = self._mc.story(test_story_id)
        self.assertEqual(story['language'], original_language)

    def testIsSyndicated(self):
        text = load_text_from_fixture("sample_story_ap.txt")
        results = self._mc.storyIsSyndicatedFromAP(text)
        self.assertEqual(results['is_syndicated'], 1)

    def testIsNotSyndicated(self):
        text = load_text_from_fixture("sample_story_not_ap.txt")
        results = self._mc.storyIsSyndicatedFromAP(text)
        self.assertEqual(results['is_syndicated'], 0)


class ApiStoryListTest(ApiBaseTest):

    def testStoryListRows(self):
        results = self._mc.storyList('*', QUERY_LAST_WEEK, rows=10)
        self.assertEqual(len(results), 10)
        results = self._mc.storyList('*', QUERY_LAST_WEEK, rows=53)
        self.assertEqual(len(results), 53)

    def testStoryPublicList(self):
        results = self._mc.storyList('*', QUERY_LAST_WEEK, rows=10)
        self.assertNotEqual(len(results), 0)

    def testStoryListWordCount(self):
        results = self._mc.storyList('*', QUERY_LAST_WEEK, wc=True)
        for story in results:
            self.assertIn('word_count', story)
            self.assertGreater(story['word_count'], 0)

    def testStoryListMetadata(self):
        results = self._mc.storyList('*', QUERY_LAST_WEEK)
        self.assertNotEqual(len(results), 0)
        for story in results:
            self.assertIn('date_guess_method', story['metadata'])
            self.assertIn('extractor_version', story['metadata'])
            self.assertIn('geocoder_version', story['metadata'])
            self.assertIn('nyt_themes_version', story['metadata'])

    def testStoryListDefaults(self):
        results = self._mc.storyList('*', QUERY_LAST_WEEK)
        for story in results:
            self.assertNotIn('story_sentences', story)
            self.assertNotIn('story_text', story)
            self.assertNotIn('is_fully_extracted', story)


class AdminApiStoryListTest(AdminApiBaseTest):

    def testStoryListWithSentences(self):
        results = self._mc.storyList('*', QUERY_LAST_WEEK, sentences=True)
        for story in results:
            self.assertIn('story_sentences', story)
            self.assertNotIn('story_text', story)
            self.assertNotIn('is_fully_extracted', story)

    def testStoryListWithText(self):
        results = self._mc.storyList('*', QUERY_LAST_WEEK, text=True)
        for story in results:
            self.assertNotIn('story_sentences', story)
            self.assertIn('story_text', story)
            self.assertIn('is_fully_extracted', story)


class AdminApiTaggingContentTest(AdminApiBaseTest):

    def testTagStories(self):
        tag_set_name = TEST_USER_EMAIL
        # tag a story with two things
        desired_tags = [StoryTag(TEST_STORY_ID, tag_set_name, 'test_tag1'),
                        StoryTag(TEST_STORY_ID, tag_set_name, 'test_tag2')]
        response = self._mc.tagStories(desired_tags)
        self.assertIn('success' , response)
        self.assertEqual(response['success'], 1)
        story = self._mc.story(TEST_STORY_ID, sentences=True)   # make sure it worked
        tags_on_story = [t for t in story['story_tags'] if t['tag_set'] == tag_set_name]
        self.assertEqual(2, len(tags_on_story))
        # test removal by action
        desired_tags = [StoryTag(TEST_STORY_ID, tag_set_name, 'test_tag1', TAG_ACTION_REMOVE)]
        response = self._mc.tagStories(desired_tags)
        self.assertIn('success' , response)
        story = self._mc.story(TEST_STORY_ID, sentences=True)   # make sure it worked
        tags_on_story = [t for t in story['story_tags'] if t['tag_set'] == tag_set_name]
        self.assertEqual(1, len(tags_on_story))
        # test removal by clear others
        response = self._mc.tagStories([], clear_others=True)
        self.assertIn('success' , response)
        story = self._mc.story(TEST_STORY_ID, sentences=True)   # make sure it worked
        tags_on_story = [t for t in story['story_tags'] if t['tag_set'] == tag_set_name]
        self.assertEqual(1, len(tags_on_story))
