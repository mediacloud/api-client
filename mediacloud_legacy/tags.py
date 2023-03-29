# pylint: disable=too-many-arguments

# Tag set ids for metadata about media in our system
TAG_SET_PUBLICATION_COUNTRY = 1935  # holds the country of publication of a source
TAG_SET_PUBLICATION_STATE = 1962  # holds the state of publication of a source (only US and India right now)
TAG_SET_PRIMARY_LANGUAGE = 1969  # holds the primary language of a source
TAG_SET_COUNTRY_OF_FOCUS = 1970  # holds the primary focus on what country for a source
TAG_SET_MEDIA_TYPE = 1972  # holds what type of media source this is (broadcast, online, etc)
METADATA_TAG_SETS = [TAG_SET_PUBLICATION_COUNTRY, TAG_SET_PUBLICATION_STATE, TAG_SET_PRIMARY_LANGUAGE,
                     TAG_SET_COUNTRY_OF_FOCUS, TAG_SET_MEDIA_TYPE]

# Tag set ids for information about a story
TAG_SET_NYT_THEMES = 1963  # the tag set the top 600 labels from our NYT-corpus-trained model
TAG_SET_CLIFF_PLACES = 1011  # the tag set all the geographic country and state tags are in
TAG_SET_CLIFF_ORGS = 2388  # the tag set with organizational entities
TAG_SET_CLIFF_PEOPLE = 2389  # the tag set with people entities

# Tag set ids for metadata about stories in our system
TAG_SET_DATE_GUESS_METHOD = 508
TAG_SET_EXTRACTOR_VERSION = 1354
TAG_SET_GEOCODER_VERSION = 1937
TAG_CLIFF_CLAVIN_2_3_0 = 9353691  # the tag that indicates a story was tagged by the CLIFF version 2.3.0
TAG_CLIFF_CLAVIN_2_4_1 = 9696677  # the tag that indicates a story was tagged by the CLIFF version 2.4.1
TAG_SET_NYT_THEMES_VERSION = 1964
TAG_NYT_LABELER_1_0_0 = 9360669  # the tag that indicates a story was tagged by the NYT labeller version 1

# Tag ids for information about a story
TAG_STORY_UNDATEABLE = 8877812  # if a story has this tag, that means it was undateable

'''
These are helpers for calling media/story tag update methods.  These wrappers exist
because you can specify this by tag/tag-set name, or by tag-id.  Because you don't want to mess
these calls up, I found it helpful to formalize this, instead of just accepting a dict from the
caller (which might be missing params).
'''

TAG_ACTION_ADD = 'add'
TAG_ACTION_REMOVE = 'remove'


class TagSpec(object):

    def __init__(self, tag_set_name=None, tag_name=None, action=TAG_ACTION_ADD, tags_id=None):
        self.tag_set_name = tag_set_name
        self.tag_name = tag_name
        self.tags_id = tags_id
        self.action = action

    def isSpecifiedByName(self):
        return (self.tag_name is not None) and (self.tag_set_name is not None)

    def isSpeficiedById(self):
        return self.tags_id is not None

    def getBaseParams(self):
        params = {
            'action': self.action
        }
        if self.isSpeficiedById():
            params['tags_id'] = self.tags_id
        elif self.isSpecifiedByName():
            params['tag'] = self.tag_name
            params['tag_set'] = self.tag_set_name
        return params


class StoryTag(TagSpec):
    """
    Use this to tag stories with metadata, like the language they are in.
    """

    def __init__(self, stories_id, tag_set_name=None, tag_name=None, action=TAG_ACTION_ADD, tags_id=None):
        self.stories_id = stories_id
        super(StoryTag, self).__init__(tag_set_name, tag_name, action, tags_id)

    def getParams(self):
        params = {'stories_id': self.stories_id}
        params.update(self.getBaseParams())
        return params


class MediaTag(TagSpec):
    """
    Use this to tag media with metadata, like the country they are publised in.
    """

    def __init__(self, media_id, tag_set_name=None, tag_name=None, action=TAG_ACTION_ADD, tags_id=None):
        self.media_id = media_id
        super(MediaTag, self).__init__(tag_set_name, tag_name, action, tags_id)

    def getParams(self):
        params = {'media_id': self.media_id}
        params.update(self.getBaseParams())
        return params
