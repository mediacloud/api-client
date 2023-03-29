import unittest
import os
import json
from mediacloud_legacy.storage import MongoStoryDatabase


class StorageTest(unittest.TestCase):

    TEST_DB_NAME = 'mediacloud-test'

    def _createThenDeleteDb(self, db):
        db.createDatabase(self.TEST_DB_NAME)
        db.deleteDatabase(self.TEST_DB_NAME)

    def _updateStoryInDb(self, db):
        story = self._getFakeStory()
        db.createDatabase(self.TEST_DB_NAME)
        # first save it normally
        worked = db.updateStory(story)
        self.assertTrue(worked)
        saved_story = db.getStory(story['stories_id'])
        self.assertNotEqual(saved_story, None)
        self.assertEqual(saved_story['stories_id'], story['stories_id'])
        self.assertEqual(saved_story['story_sentences_count'], 4)
        self.assertFalse('category' in saved_story)
        # now update it with new info and make sure it is still there
        db.updateStory(story, {'category': 'editorial'})
        saved_story = db.getStory(story['stories_id'])
        self.assertNotEqual(saved_story, None)
        self.assertEqual(saved_story['stories_id'], story['stories_id'])
        self.assertEqual(saved_story['story_sentences_count'], 4)
        self.assertTrue('category' in saved_story)
        db.deleteDatabase(self.TEST_DB_NAME)

    def _countStoriesInDb(self, db):
        story1 = self._getFakeStory()
        story1['stories_id'] = "10000000000"
        story2 = self._getFakeStory()
        story1['stories_id'] = "20000000000"
        db.createDatabase(self.TEST_DB_NAME)
        db.initialize()
        db.addStory(story1)
        db.addStory(story2)
        self.assertEqual(2, db.storyCount())
        self.assertEqual(1, db.storyCount({'stories_id': "10000000000"}))
        db.deleteDatabase(self.TEST_DB_NAME)

    def _addStoryToDb(self, db):
        story = self._getFakeStory()
        db.createDatabase(self.TEST_DB_NAME)
        worked = db.addStory(story)
        self.assertTrue(worked)
        worked = db.addStory(story)
        self.assertFalse(worked)
        saved_story = db.getStory(story['stories_id'])
        self.assertNotEqual(saved_story, None)
        self.assertEqual(saved_story['stories_id'], story['stories_id'])
        self.assertEqual(saved_story['story_sentences_count'], 4)
        db.deleteDatabase(self.TEST_DB_NAME)

    def _checkStoryExistsInDb(self, db):
        story = self._getFakeStory()
        db.createDatabase(self.TEST_DB_NAME)
        db.addStory(story)
        db.getStory(story['stories_id'])
        self.assertTrue(db.storyExists(story['stories_id']))
        self.assertFalse(db.storyExists('43223535'))
        db.deleteDatabase(self.TEST_DB_NAME)

    def _testMaxStoryIdInDb(self, db):
        story1 = self._getFakeStory()
        story1['stories_id'] = "10000000000"
        story2 = self._getFakeStory()
        story1['stories_id'] = "20000000000"
        db.createDatabase(self.TEST_DB_NAME)
        db.initialize()
        db.addStory(story1)
        db.addStory(story2)
        self.assertEqual(db.getMaxStoryId(), 20000000000)
        db.deleteDatabase(self.TEST_DB_NAME)

    @staticmethod
    def _getFakeStory():
        with open(os.path.dirname(os.path.realpath(__file__))+'/fixtures/story_27456565.json', 'r') as my_file:
            return json.loads(my_file.read())

    @staticmethod
    def _getFakeStorySentences(page=1):
        with open(os.path.dirname(os.path.realpath(__file__))+'/fixtures/sentences_by_story_'+str(page)+'.json', 'r') as my_file:
            return json.loads(my_file.read())


class MongoStorageTest(StorageTest):

    def testManageDatabase(self):
        db = MongoStoryDatabase()
        self._createThenDeleteDb(db)

    def testGetMaxStoryId(self):
        db = MongoStoryDatabase()
        self._testMaxStoryIdInDb(db)

    def testStoryExists(self):
        db = MongoStoryDatabase()
        self._checkStoryExistsInDb(db)

    def testAddStory(self):
        db = MongoStoryDatabase()
        self._addStoryToDb(db)

    def testUpdateStory(self):
        db = MongoStoryDatabase()
        self._updateStoryInDb(db)

    def testStoryCount(self):
        db = MongoStoryDatabase()
        self._countStoriesInDb(db)
