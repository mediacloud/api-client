import datetime

from mediacloud.test.basetest import AdminApiBaseTest
from mediacloud.test import QUERY_LAST_WEEK

SENTENCE_COUNT = 100
QUERY_TEST = "*"


class AdminApiSentencesTest(AdminApiBaseTest):

    def testLongQuery(self):
        results = self._mc.sentenceList(
            '((दस्त OR डायरिया OR अतिसार OR रोटा OR "रोटा वायरस" OR "रोटा वाइरस" OR रोटावाइरस OR रोटावायरस) OR ((एआरटी OR एआरवी) AND (एचआईवी OR एड्स)) OR (आवाहन OR "नेशनल एड्स कंट्रोल ऑर्गनाइजेशन" OR "राष्ट्रीय एड्स नियंत्रण संगठन" OR "नैको" OR "एंटीरेट्रोवाइरल" OR "एंटी रेट्रोवायरल" OR "एंटी रेट्रो वायरल" OR "एंटी रेट्रोवायरल") OR मलेरिया OR (निमोनिया OR "न्यूमोकोकल के टीके" OR "न्यूमोकोकल टीका" OR "न्यूमोकोकल कंजुगेट वैक्सीन" OR "न्यूमोकोकल वैक्सीन") OR (ट्यूबरकुलोसिस OR क्षय OR क्षयरोग OR यक्ष्मा OR "क्षय रोग" OR टीबी OR "बीसीजी वैक्सीन" OR "बीसीजी का टीका" OR "बीसीजी के टीके" OR "बीसीजी के टीकों") OR (पोलियो OR आईपीवी OR "इनएक्टिवेटेड पोलियो वैक्सीन" OR (ओपीवी OR "ओरल पोलियो वैक्सीन" NOT (शिप OR वैसेल OR नेवी))) OR "काला ज्वर" OR "काला-अजार" OR "विसरल लेशमेनियासिस" OR "काला आज़ार" OR "काला अजार" OR "कालाजार" OR "काला बुखार" OR टाइफाइड OR "आंत्र ज्वर" OR "लिम्फेटिक फाइलेरिया" OR "हाथीपांव" OR "फाइलेरिया" OR "लिम्फेटिक फाइलेरियासिस" OR एलिफन्टाइसिस OR फीलपाँव OR श्लीपद OR एनटीडी OR "संक्रामक रोगों" OR "संक्रामक रोग" OR "संक्रामक बीमारी" OR "संक्रामक बीमारियाँ" OR "संक्रामक बीमारियाों" OR "इनफेक्शियस डिजीज" OR "मास ड्रग एडमिनिस्ट्रेशन" OR "एमडीए अभियान" OR "द्रव्यमान दवा प्रशासन" OR "सैंड फ्लाई" OR "तीव्र एन्सेफलाइटिस सिंड्रोम" OR "एक्यूट इंसेफेलाइटिस सिंड्रोम" OR "एईएस" OR "चमकी बुखार" OR "नेगलेक्टेड ट्रॉपिकल डिजीज" OR "नेगलेक्टेड ट्रॉपिकल डिसीज" OR "उपेक्षित उष्णकटिबंधीय रोग" OR "उपेक्षित उष्णकटिबंधीय रोगों" OR "उपेक्षित उष्णकटिबंधीय बीमारी" OR "उपेक्षित उष्णकटिबंधीय बीमारियों" OR "उपेक्षित उष्णकटिबंधीय बीमारियां") AND (( tags_id_media:(9325106)))',
            'publish_day:[2019-06-16T00:00:00Z TO 2019-06-18T00:00:00Z]',
            rows=100, sort='random')
        self.assertGreater(len(results), 13)

    def testSentenceListRows(self):
        results = self._mc.sentenceList(QUERY_TEST, QUERY_LAST_WEEK, rows=13)
        self.assertGreater(len(results), 13)
        results = self._mc.sentenceList(QUERY_TEST, QUERY_LAST_WEEK, rows=513)
        self.assertGreater(len(results), 513)

    def testSentenceList(self):
        results = self._mc.sentenceList(QUERY_TEST, QUERY_LAST_WEEK)
        self.assertGreater(len(results), 1000)

    def testSentenceListPaging(self):
        results_page1 = self._mc.sentenceList(QUERY_TEST, QUERY_LAST_WEEK, 0, 10)
        self.assertGreater(len(results_page1), 10)
        page1_sentence_ids = [s['story_sentences_id'] for s in results_page1]
        results_page2 = self._mc.sentenceList(QUERY_TEST, QUERY_LAST_WEEK, 10, 10)
        page2_sentence_ids = [s['story_sentences_id'] for s in results_page2]
        # intersect
        in_both = list(set(page1_sentence_ids) & set(page2_sentence_ids))
        self.assertEqual(len(in_both), 0)

    def testSentenceListSortingAscending(self):
        results = self._mc.sentenceList(QUERY_TEST, QUERY_LAST_WEEK, 0, SENTENCE_COUNT, self._mc.SORT_PUBLISH_DATE_ASC)
        self.assertGreater(len(results), SENTENCE_COUNT)
        last_date = None
        for sentence in results:
            this_date = datetime.datetime.strptime(sentence['publish_date'][0:19], self._mc.SENTENCE_PUBLISH_DATE_FORMAT)
            this_date = this_date.replace(second=0, microsecond=0)  # sorting is by minute
            if last_date is not None:
                self.assertLessEqual(last_date, this_date)
            last_date = this_date

    '''
    Failing for now :-(
    def testSentenceListSortingDescending(self):
        results = self._mc.sentenceList(QUERY_TEST, QUERY_LAST_WEEK, 0, SENTENCE_COUNT, self._mc.SORT_PUBLISH_DATE_DESC)
        self.assertGreater(len(results), SENTENCE_COUNT)
        last_date = None
        for sentence in results:
            this_date = datetime.datetime.strptime(sentence['publish_date'], self._mc.SENTENCE_PUBLISH_DATE_FORMAT)
            this_date = this_date.replace(second=0, microsecond=0)  # sorting is by minute
            if last_date is not None:
                self.assertGreaterEqual(last_date, this_date)
                last_date = this_date
            last_date = this_date
    '''

    def testSentenceListSortingRadom(self):
        # we do random sort by telling we want the random sort, and then offsetting to a different start index
        results1 = self._mc.sentenceList(QUERY_TEST, QUERY_LAST_WEEK, 0, SENTENCE_COUNT, self._mc.SORT_RANDOM)
        self.assertGreater(len(results1), SENTENCE_COUNT)
        results2 = self._mc.sentenceList(QUERY_TEST, QUERY_LAST_WEEK, SENTENCE_COUNT * 2, SENTENCE_COUNT,
                                         self._mc.SORT_RANDOM)
        self.assertGreater(len(results2), SENTENCE_COUNT)
        for idx in range(0, SENTENCE_COUNT):
            self.assertNotEqual(results1[idx]['stories_id'],
                                results2[idx]['stories_id'],
                                "Stories in two different random sets are the same :-(")
