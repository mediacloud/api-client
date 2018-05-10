#! /usr/bin/env python
import unittest
import logging
import sys

import mediacloud.test.apitest as api
import mediacloud.test.api_story_test
import mediacloud.test.api_sentence_test
import mediacloud.test.api_media_test
import mediacloud.test.apitopictest as topic
import mediacloud.test.storagetest as storage

modules = [mediacloud.test.api_story_test,
           mediacloud.test.api_sentence_test,
           mediacloud.test.api_media_test,
           api, topic, storage
        ]

# set up all logging to DEBUG (cause we're running tests here!)
logging.basicConfig(level=logging.DEBUG)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler = logging.FileHandler('mediacloud-api-tesapi.log')
log_handler.setFormatter(log_formatter)
# set up mediacloud logging to the file
mc_logger = logging.getLogger('mediacloud')
mc_logger.propagate = True
mc_logger.addHandler(log_handler)
mc_logger.level = logging.DEBUG
# set up requests logging to the file
requests_logger = logging.getLogger('requests')
requests_logger.propagate = True
requests_logger.addHandler(log_handler)
requests_logger.level = logging.DEBUG

# now run all the tests
suites = [unittest.TestLoader().loadTestsFromModule(module) for module in modules]

if __name__ == "__main__":
    suite = unittest.TestSuite(suites)
    test_result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not test_result.wasSuccessful():
        sys.exit(1)
