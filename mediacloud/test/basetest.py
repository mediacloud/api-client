import unittest
import ConfigParser
import mediacloud.api

class ApiBaseTest(unittest.TestCase):

    QUERY = 'obama'
    FILTER_QUERY = '+publish_date:[2015-01-01T00:00:00Z TO 2015-02-01T00:00:00Z] AND +media_id:1'
    SENTENCE_COUNT = 100

    def setUp(self):
        self._config = ConfigParser.ConfigParser()
        self._config.read('mc-client.config')
        self._mc = mediacloud.api.MediaCloud(self._config.get('api', 'key'))

class AdminApiBaseTest(unittest.TestCase):

    def setUp(self):
        self._config = ConfigParser.ConfigParser()
        self._config.read('mc-client.config')
        self._mc = mediacloud.api.AdminMediaCloud(self._config.get('api', 'key'))
