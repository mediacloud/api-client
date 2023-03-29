import copy
import logging


class StoryDatabase(object):

    # callbacks you can register listeners against
    EVENT_PRE_STORY_SAVE = "preStorySave"
    EVENT_POST_STORY_SAVE = "postStorySave"

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._db = None

    def storyExists(self, story_id):
        raise NotImplementedError("Subclasses should implement this!")

    def updateStory(self, story, extra_attributes={}):
        # if it is a new story, just add it normally
        if not self.storyExists(story['stories_id']):
            return self.addStory(story, extra_attributes)
        else:
            story_to_save = copy.deepcopy(story)
            story_to_save.update(extra_attributes)
            story_to_save['stories_id'] = story['stories_id']
            if 'story_sentences' in story:
                story_to_save['story_sentences_count'] = len(story['story_sentences'])
            return self._updateStory(story_to_save)
            # self.getStory(story['stories_id'])
            # self._logger.debug('Updated {}'.format(story['stories_id']))

    def addStory(self, story, extra_attributes={}):
        # Save a story (python object) to the database. This does NOT update stories.
        # Return success or failure boolean.
        if self.storyExists(story['stories_id']):
            self._logger.info('Not saving {} - already exists'.format(story['stories_id']))
            return False
        story_to_save = copy.deepcopy(story)
        story_to_save.update(extra_attributes)
        story_to_save['_stories_id'] = story['stories_id']
        if 'story_sentences' in story:
            story_to_save['story_sentences_count'] = len(story['story_sentences'])
        self._saveStory(story_to_save)
        self.getStory(story['stories_id'])
        self._logger.debug('Saved {}'.format(story['stories_id']))
        return True

    def _updateStory(self, story_attributes):
        raise NotImplementedError("Subclasses should implement this!")

    def _saveStory(self, story_attributes):
        raise NotImplementedError("Subclasses should implement this!")

    def getStory(self, story_id):
        raise NotImplementedError("Subclasses should implement this!")

    def storyCount(self, search_criteria=None):
        raise NotImplementedError("Subclasses should implement this!")

    def createDatabase(self, db_name):
        raise NotImplementedError("Subclasses should implement this!")

    def deleteDatabase(self, db_name):
        raise NotImplementedError("Subclasses should implement this!")

    def getMaxStoryId(self):
        raise NotImplementedError("Subclasses should implement this!")

    def initialize(self):
        raise NotImplementedError("Subclasses should implement this!")


class MongoStoryDatabase(StoryDatabase):

    def __init__(self, db_name=None, uri="mongodb://localhost:27017"):
        super(MongoStoryDatabase, self).__init__()
        import pymongo
        self._server = pymongo.MongoClient(uri)
        if db_name is not None:
            self.selectDatabase(db_name)

    def createDatabase(self, db_name):
        self.selectDatabase(db_name)

    def selectDatabase(self, db_name):
        self._db = self._server[db_name]

    def deleteDatabase(self, db_name):
        self._db.drop_collection('stories')

    def storyExists(self, story_id):
        matching_count = self.storyCount({"stories_id": story_id})
        return matching_count != 0

    def _updateStory(self, story_attributes):
        self._db.stories.update_one({'stories_id': story_attributes['stories_id']}, {'$set': story_attributes})
        story = self.getStory(story_attributes['stories_id'])
        return story

    def _saveStory(self, story_attributes):
        self._db.stories.insert_one(story_attributes)
        story = self.getStory(story_attributes['stories_id'])
        return story

    def getStory(self, story_id):
        stories = self._db.stories.find({"stories_id": story_id}).limit(1)
        try:
            return stories.next()
        except StopIteration:
            return None

    def getMaxStoryId(self):
        max_story_id = self._db.stories.find().sort("stories_id", -1)[0]['stories_id']
        return int(max_story_id)

    def initialize(self):
        # nothing to init for mongo
        return

    def storyCount(self, search_criteria=None):
        criteria = {}
        if search_criteria is not None:
            criteria = search_criteria
        return self._db['stories'].count_documents(criteria)
