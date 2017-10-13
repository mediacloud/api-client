#! /usr/bin/env python
import unittest
import logging
import sys

import mediacloud.test.apitest as api
import mediacloud.test.apitopictest as topic
import mediacloud.test.storagetest as storage

test_classes = [
    api.ApiBigQueryTest,
    api.ApiStoriesWordMatrixTest,
    api.ApiMediaHealthTest, api.AdminApiMediaTest, 
    api.ApiMediaTest, api.AdminApiMediaSuggestionsTest,
    api.ApiFeedsTest, api.ApiTagsTest, api.ApiTagSetsTest,
    api.ApiStoriesTest, api.AdminApiStoriesTest, api.AdminApiStoryUpdateTest,
    api.ApiWordCountTest, api.ApiSentencesTest, api.AdminApiSentencesTest,
    storage.MongoStorageTest,
    api.AuthTokenTest, api.UserProfileTest,
    api.ApiAllFieldsOptionTest,
    api.PublishDateQueryTest,
    api.AdminApiTaggingContentTest, api.AdminApiTaggingTest,
    topic.AdminTopicSentenceCountTest,
    topic.ApiTopicTest, topic.ApiTopicSnapshotTest, topic.ApiTopicTimespanTest,
    topic.AdminTopicStoryListTest, topic.AdminTopicMediaListTest, topic.AdminTopicWordCountTest,
    topic.AdminTopicStoryCountTest, topic.AdminTopicMediaMapTest,
    topic.ApiTopicSpiderTest,
    api.StatsTest
]

# test_classes = [ topic.ApiTopicTest ]

# set up all logging to DEBUG (cause we're running tests here!)
logging.basicConfig(level=logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler = logging.FileHandler('mediacloud-api-tesapi.log')
log_handler.setFormatter(log_formatter)
# set up mediacloud logging to the file
mc_logger = logging.getLogger('mediacloud')
mc_logger.propagate = False
mc_logger.addHandler(log_handler)
# set up requests logging to the file
requests_logger = logging.getLogger('requests')
requests_logger.propagate = False
requests_logger.addHandler(log_handler)

# now run all the tests
suites = [unittest.TestLoader().loadTestsFromTestCase(test_class) for test_class in test_classes]

if __name__ == "__main__":
    suite = unittest.TestSuite(suites)
    test_result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not test_result.wasSuccessful():
        sys.exit(1)
