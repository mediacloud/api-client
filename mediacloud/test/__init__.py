import os.path
import logging
from dotenv import load_dotenv


TEST_USER_EMAIL = "mc-api-test@media.mit.edu"

QUERY_LAST_FEW_DAYS = "publish_date:[NOW-3DAY TO NOW]"
QUERY_LAST_WEEK = "publish_date:[NOW-7DAY TO NOW]"
QUERY_LAST_MONTH = "publish_date:[NOW-31DAY TO NOW]"
QUERY_LAST_YEAR = "publish_date:[NOW-1YEAR TO NOW]"
QUERY_LAST_DECADE = "publish_date:[NOW-10YEAR TO NOW]"
QUERY_ENGLISH_LANGUAGE = "language:en"

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)

# load env-vars from .env file if there is one
test_env = os.path.join(basedir, '.env')
if os.path.isfile(test_env):
    load_dotenv(dotenv_path=os.path.join(basedir, '.env'), verbose=True)


def load_text_from_fixture(filename):
    with open(os.path.join(basedir, "mediacloud", "test", "fixtures", filename), 'r') as f:
        text = f.read()
    return text
