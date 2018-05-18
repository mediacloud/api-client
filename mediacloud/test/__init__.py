import os.path
import codecs

TEST_USER_EMAIL = "mc-api-test@media.mit.edu"

QUERY_LAST_FEW_DAYS = "publish_date:[NOW-3DAY TO NOW]"
QUERY_LAST_WEEK = "publish_date:[NOW-7DAY TO NOW]"
QUERY_LAST_MONTH = "publish_date:[NOW-31DAY TO NOW]"
QUERY_LAST_YEAR = "publish_date:[NOW-1YEAR TO NOW]"
QUERY_LAST_DECADE = "publish_date:[NOW-10YEAR TO NOW]"
QUERY_ENGLISH_LANGUAGE = "language:en"

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def load_text_from_fixture(filename):
    f = codecs.open(os.path.join(basedir, "mediacloud", "test", "fixtures", filename), 'r',
                    encoding='utf8')
    text = f.read()
    return text
