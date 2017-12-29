import os.path
import codecs

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def load_text_from_fixture(filename):
    f = codecs.open(os.path.join(basedir, "mediacloud", "test", "fixtures", filename), 'r',
                    encoding='utf8')
    text = f.read()
    return text
