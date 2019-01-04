from mediacloud.test.basetest import ApiBaseTest
from mediacloud.test import QUERY_LAST_WEEK


class ApiWordCountTest(ApiBaseTest):

    QUERY = 'robots'

    def testSort(self):
        term_freq = self._mc.wordCount('*', QUERY_LAST_WEEK)
        last_count = None
        for word in term_freq:
            if last_count is not None:
                self.assertLessEqual(word['count'], last_count)
            last_count = word['count']

    def testNumWords(self):
        term_freq = self._mc.wordCount('*', QUERY_LAST_WEEK)
        self.assertEqual(len(term_freq), 500)
        term_freq = self._mc.wordCount('*', QUERY_LAST_WEEK, num_words=101)
        self.assertEqual(len(term_freq), 101)

    def testStopWords(self):
        term_freq = self._mc.wordCount('*', QUERY_LAST_WEEK)
        term_freq_with_stopwords = self._mc.wordCount('*', QUERY_LAST_WEEK, include_stopwords=True)
        self.assertNotEqual(term_freq[0]['term'], term_freq_with_stopwords[0]['term'])

    def testStats(self):
        term_freq = self._mc.wordCount('*', QUERY_LAST_WEEK, include_stats=True)
        self.assertTrue('stats' in term_freq.keys())
        self.assertTrue('words' in term_freq.keys())

    def testBigram(self):
        term_freq = self._mc.wordCount('*', QUERY_LAST_WEEK, ngram_size=2)
        for term in term_freq:
            self.assertEqual(len(term['term'].split(' ')), 2,
                             "Uh oh - '{}' doesn't seem like a bigram! ({})".format(term['term'], term['stem']))

    def testRandomSeed(self):
        term_freq = self._mc.wordCount('*', QUERY_LAST_WEEK)
        random_term_freq = self._mc.wordCount('*', QUERY_LAST_WEEK, random_seed=20)
        self.assertEqual(len(term_freq), len(random_term_freq))
