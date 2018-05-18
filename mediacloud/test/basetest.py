import unittest
import ConfigParser
import random

import mediacloud.api
from mediacloud.test import QUERY_LAST_WEEK, QUERY_ENGLISH_LANGUAGE


class ApiBaseTest(unittest.TestCase):

    QUERY = 'obama'
    FILTER_QUERY = '+publish_date:[2015-01-01T00:00:00Z TO 2015-02-01T00:00:00Z] AND +media_id:1'

    def setUp(self):
        self._config = ConfigParser.ConfigParser()
        self._config.read('mc-client.config')
        self._mc = mediacloud.api.MediaCloud(self._config.get('api', 'key'))

    def recentStory(self):
        recent_stories = self._mc.storyList(QUERY_ENGLISH_LANGUAGE, QUERY_LAST_WEEK)
        story = random.choice(recent_stories)
        return story

    def randomMedia(self):
        media_list = self._mc.mediaList()
        media = random.choice(media_list)
        return media


class AdminApiBaseTest(ApiBaseTest):

    def setUp(self):
        self._config = ConfigParser.ConfigParser()
        self._config.read('mc-client.config')
        self._mc = mediacloud.api.AdminMediaCloud(self._config.get('api', 'key'))
