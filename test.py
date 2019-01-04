#! /usr/bin/env python
import unittest
import logging
import sys

import mediacloud.test.api_story_test
import mediacloud.test.api_sentence_test
import mediacloud.test.api_media_test
import mediacloud.test.api_misc_test
import mediacloud.test.api_user_test
import mediacloud.test.api_word_count_test
import mediacloud.test.api_feed_test
import mediacloud.test.api_tags_test
import mediacloud.test.api_topic_test
import mediacloud.test.storage_test

logger = logging.getLogger(__name__)

modules = [mediacloud.test.api_story_test,
           mediacloud.test.api_sentence_test,
           mediacloud.test.api_media_test,
           mediacloud.test.api_misc_test,
           mediacloud.test.api_user_test,
           mediacloud.test.api_word_count_test,
           mediacloud.test.api_feed_test,
           mediacloud.test.api_tags_test,
           mediacloud.test.api_topic_test,
           mediacloud.test.storage_test
           ]

# set up ogging
logging.basicConfig(level=logging.WARN)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler = logging.FileHandler('mediacloud-api-tesapi.log')
log_handler.setFormatter(log_formatter)
mc_logger = logging.getLogger('mediacloud')
mc_logger.propagate = True
mc_logger.addHandler(log_handler)
mc_logger.level = logging.WARN
requests_logger = logging.getLogger('requests')
requests_logger.propagate = True
requests_logger.addHandler(log_handler)
requests_logger.level = logging.WARN

# now run all the tests
suites = [unittest.TestLoader().loadTestsFromModule(m) for m in modules]

failed_suites_count = 0

if __name__ == "__main__":
    for suite in suites:
        test_result = unittest.TextTestRunner(verbosity=3).run(suite)
        if not test_result.wasSuccessful():
            failed_suites_count = failed_suites_count + 1

logger.info("Ran {} suites. {} failed.".format(len(suites), failed_suites_count))

# Let CI tools know if there was an error
if failed_suites_count:
    sys.exit(1)

sys.exit(0)
