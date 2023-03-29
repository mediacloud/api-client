import datetime
import json
import logging
import time
import requests

import mediacloud
import mediacloud.error
from mediacloud.tags import StoryTag, MediaTag, TAG_SET_PUBLICATION_COUNTRY, TAG_SET_PUBLICATION_STATE, \
    TAG_SET_PRIMARY_LANGUAGE, TAG_SET_COUNTRY_OF_FOCUS, TAG_SET_MEDIA_TYPE, TAG_SET_DATE_GUESS_METHOD, \
    TAG_SET_EXTRACTOR_VERSION, TAG_SET_GEOCODER_VERSION, TAG_SET_NYT_THEMES_VERSION

MAX_HTTP_GET_CHARS = 4000   # experimentally determined for our main servers (conservative)

logger = logging.getLogger(__name__)

VALID_FEED_TYPES = ['syndicated', 'web_page', 'podcast']


# Simple client library for the MediaCloud API v2
class MediaCloud(object):

    V2_API_URL = "https://api.mediacloud.org/api/v2/"

    SORT_PUBLISH_DATE_ASC = "publish_date_asc"
    SORT_PUBLISH_DATE_DESC = "publish_date_desc"
    SORT_RANDOM = "random"
    SORT_PROCESSED_STORIES_ID = "processed_stories_id"

    MSG_CORE_NLP_NOT_ANNOTATED = "story is not annotated"

    SENTENCE_PUBLISH_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"  # use with datetime.datetime.strptime

    FOCAL_TECHNIQUE_BOOLEAN_QUERY = "Boolean Query"

    def __init__(self, auth_token=None, all_fields=False):
        if not auth_token:
            raise mediacloud.error.MCException(u"No api key set - nothing will work without this")
        self._all_fields = None
        self._auth_token = None
        self.setAuthToken(auth_token)
        self.setAllFields(all_fields)

    def setAllFields(self, all_fields):
        # Specify the value of the all_fields param to use for all future requests
        self._all_fields = all_fields

    def setAuthToken(self, auth_token):
        # Specify the auth_token to use for all future requests        '''
        self._auth_token = auth_token

    def verifyAuthToken(self):
        try:
            self.tagSetList(0, 1)
            return True
        except mediacloud.error.MCException:
            return False
        except Exception as exception:
            logger.warning(u"AuthToken verify failed: %s", exception)
        return False

    def userProfile(self):
        # :return: basic info about the current user, including their roles
        return self._queryForJson(self.V2_API_URL+'auth/profile')

    def authLogin(self, email, password):
        # :return: { success: 1, profile: {...}} or {error: msg}
        params = {
            'email': email,
            'password': password
        }
        return self._queryForJson(self.V2_API_URL+'auth/login', params, 'POST_JSON')

    def authRegister(self, email, password, full_name, notes, activation_url, has_consented):
        # :return: {success: 1}, or {error: "msg"}
        params = {
            'email': email,
            'password': password,
            'full_name': full_name,
            'notes': notes,
            'activation_url': activation_url,
            'has_consented': has_consented,
        }
        _validate_bool_params(params, 'has_consented')
        results = self._queryForJson(self.V2_API_URL+'auth/register', params, 'POST_JSON')
        return results

    def authActivate(self, email, activation_token):
        # :return: { success: 1, profile: {...}} or {error: msg}
        params = {
            'email': email,
            'activation_token': activation_token
        }
        return self._queryForJson(self.V2_API_URL+'auth/activate', params, 'POST_JSON')

    def authResendActivationLink(self, email, activation_url):
        # :return: {success: 1}, or {error: "msg"}
        params = {
            'email': email,
            'activation_url': activation_url
        }
        return self._queryForJson(self.V2_API_URL + 'auth/resend_activation_link', params, 'POST_JSON')

    def authSendPasswordResetLink(self, email, password_reset_url):
        # :return: {success: 1}, or {error: "msg"}
        params = {
            'email': email,
            'password_reset_url': password_reset_url
        }
        return self._queryForJson(self.V2_API_URL + 'auth/send_password_reset_link', params, 'POST_JSON')

    def authResetPassword(self, email, password_reset_token, new_password):
        # :return: {success: 1}, or {error: "msg"}
        params = {
            'email': email,
            'password_reset_token': password_reset_token,
            'new_password': new_password
        }
        return self._queryForJson(self.V2_API_URL + 'auth/reset_password', params, 'POST_JSON')

    def authChangePassword(self, old_password, new_password):
        # :return: { success: 1, profile: {...}} or {error: msg}
        params = {
            'old_password': old_password,
            'new_password': new_password
        }
        return self._queryForJson(self.V2_API_URL + 'auth/change_password', params, 'POST_JSON')

    def authResetApiKey(self):
        # :return: {success: 1}, or {error: "msg"}
        return self._queryForJson(self.V2_API_URL + 'auth/reset_api_key', {}, 'POST_JSON')

    def stats(self):
        # High-level stats about the system
        return self._queryForJson(self.V2_API_URL+'stats/list')

    def media(self, media_id):
        # Details about one media source
        results = self._queryForJson(self.V2_API_URL+'media/single/{}'.format(media_id))
        results_with_metadata = self._addMetadataTagsToMediaList(results)
        return results_with_metadata[0]

    def mediaHealth(self, media_id):
        # Details about one media source
        results = self._queryForJson(self.V2_API_URL+'mediahealth/list', {'media_id': media_id})
        if results:
            return results[0]
        return results

    def mediaList(self, last_media_id=0, rows=20, name_like=None,
                  timespans_id=None, tags_id=None, q=None, include_dups=False,
                  unhealthy=None, similar_media_id=None, sort=None, **kwargs):
        # Page through all media sources.
        valid_sort_options = ['id', 'num_stories']
        params = {'last_media_id': last_media_id, 'rows': rows}
        if name_like is not None:
            params['name'] = name_like
        if timespans_id is not None:
            params['timespans_id'] = timespans_id
        if include_dups is not None:
            params['include_dups'] = 1 if include_dups is True else 0
        if unhealthy is not None:
            params['unhealthy'] = 1 if unhealthy is True else 0
        if similar_media_id is not None:
            params['similar_media_id'] = similar_media_id
        if tags_id is not None:
            params['tags_id'] = tags_id
        if q is not None:
            params['q'] = q
        if (sort is not None) and (sort not in valid_sort_options):
            raise ValueError('Sort must be either id num_stories')
        else:
            params['sort'] = sort
        # And verify that the kwargs are tags_ids
        params.update(kwargs)
        # now make the call with all the params
        results = self._queryForJson(self.V2_API_URL+'media/list', params)
        for m in results:  # cleanup from string to float
            m['num_sentences_90'] = float(m['num_sentences_90'])
            m['num_stories_90'] = float(m['num_stories_90'])
        results_with_metadata = self._addMetadataTagsToMediaList(results)
        return results_with_metadata

    def _addMetadataTagsToMediaList(self, media_list):
        for m in media_list:
            metadata = {
                'pub_country': self._firstTagOnMedia(m, TAG_SET_PUBLICATION_COUNTRY),
                'pub_state': self._firstTagOnMedia(m, TAG_SET_PUBLICATION_STATE),
                'language': self._firstTagOnMedia(m, TAG_SET_PRIMARY_LANGUAGE),
                'about_country': self._firstTagOnMedia(m, TAG_SET_COUNTRY_OF_FOCUS),
                'media_type': self._firstTagOnMedia(m, TAG_SET_MEDIA_TYPE),
            }
            m['metadata'] = metadata
        return media_list

    def _firstTagOnMedia(self, media_source, tag_sets_id):
        # Find the first tag on a media source from a set, or None if it doesn't have one
        tags = self._tagsOnMedia(media_source, tag_sets_id)
        return tags[0] if tags else None

    @staticmethod
    def _tagsOnMedia(media_source, tag_sets_id):
        # Find all the tags from a set on a media source
        return [t for t in media_source['media_source_tags'] if t['tag_sets_id'] == tag_sets_id]

    def mediaSuggest(self, url, name=None, feed_url=None, reason=None, tags_ids=None):
        tags_to_apply = tags_ids if tags_ids is not None else []
        if tags_to_apply is None:
            tags_to_apply = []
        for tags_id in tags_to_apply:
            if not isinstance(tags_id, int):
                raise ValueError('The tags_ids must be a list of ids')
        params = {
            'url': url,
            'name': name,
            'feed_url': feed_url,
            'reason': reason,
            'tags_ids': tags_to_apply
        }
        return self._queryForJson(self.V2_API_URL+'media/submit_suggestion', params, 'POST_JSON')

    def feed(self, feeds_id):
        # Details about one feed
        return self._queryForJson(self.V2_API_URL+'feeds/single/{}'.format(feeds_id))[0]

    def feedList(self, media_id, last_feeds_id=0, rows=20):
        # Page through all the feeds of one media source
        return self._queryForJson(self.V2_API_URL+'feeds/list',
                                  {'media_id': media_id, 'last_feeds_id': last_feeds_id, 'rows': rows})

    def storyPublic(self, stories_id):
        # Maintained for backwards compatability
        return self.story(stories_id)

    def story(self, stories_id):
        # Authenticated Public Users: Details about one story.
        # Note that this does NOT include text, nor sentences (due to copyright limitations).
        stories = self._queryForJson(self.V2_API_URL+'stories_public/single/{}'.format(stories_id))
        stories_with_metadata = self._addMetadataTagsToStoryList(stories)
        return stories_with_metadata[0]

    def storyRawCliffResults(self, story_id_list, http_method='POST'):
        return self._queryForJson(self.V2_API_URL+'stories/cliff', {'stories_id': story_id_list}, http_method)

    def storyRawNytThemeResults(self, story_id_list, http_method='POST'):
        return self._queryForJson(self.V2_API_URL+'stories/nytlabels', {'stories_id': story_id_list}, http_method)

    def storyCount(self, solr_query='', solr_filter='', split=None, split_period=None, http_method='POST'):
        # The call returns the number of stories returned by Solr for the specified query
        return self._queryForJson(self.V2_API_URL+'stories_public/count',
                                  {'q': solr_query,
                                   'fq': solr_filter,
                                   'split': 1 if split is True else 0,
                                   'split_period': _validate_split_period_param(split_period)
                                   }, http_method)

    def storyPublicList(self, solr_query='', solr_filter='', last_processed_stories_id=0, rows=20,
                        wc=False, feeds_id=None, sort=SORT_PROCESSED_STORIES_ID):
        # Maintained for backwards compatability
        return self.storyList(solr_query, solr_filter, last_processed_stories_id, rows, wc, feeds_id, sort)

    def storyList(self, solr_query='', solr_filter='', last_processed_stories_id=0, rows=20,
                  wc=False, feeds_id=None, sort=SORT_PROCESSED_STORIES_ID, show_feeds=False, http_method='POST'):
        # This combination doesn't produce expected behaviour
        if (sort == MediaCloud.SORT_RANDOM) and (last_processed_stories_id not in [0, None]):
            raise ValueError("You can't page through randomly sorted story lists")
        # Authenticated Public Users: Search for stories and page through results
        stories = self._queryForJson(self.V2_API_URL+'stories_public/list',
                                     {'q': solr_query,
                                      'fq': solr_filter,
                                      'last_processed_stories_id': last_processed_stories_id,
                                      'rows': rows,
                                      'sort': sort,
                                      'wc': 1 if wc is True else 0,
                                      'feeds_id': feeds_id,
                                      'show_feeds': 1 if show_feeds is True else 0,
                                      },
                                     http_method)
        stories_with_metadata = self._addMetadataTagsToStoryList(stories)
        return stories_with_metadata

    def _addMetadataTagsToStoryList(self, story_list):
        for s in story_list:
            metadata = {
                'date_guess_method': self._firstTagOnStory(s, TAG_SET_DATE_GUESS_METHOD),
                'extractor_version': self._firstTagOnStory(s, TAG_SET_EXTRACTOR_VERSION),
                'geocoder_version': self._firstTagOnStory(s, TAG_SET_GEOCODER_VERSION),
                'nyt_themes_version': self._firstTagOnStory(s, TAG_SET_NYT_THEMES_VERSION)
            }
            s['metadata'] = metadata
        return story_list

    def _firstTagOnStory(self, story, tag_sets_id):
        # Find the first tag on a story from a set, or None if it doesn't have one
        tags = self._tagsOnStory(story, tag_sets_id)
        return tags[0] if tags else None

    @staticmethod
    def _tagsOnStory(story, tag_sets_id):
        # Find all the tags from a set on a media source
        return [t for t in story['story_tags'] if t['tag_sets_id'] == tag_sets_id]

    def storyCoreNlpList(self, story_id_list):
        # The stories/corenlp call takes as many stories_id= parameters as you want to pass it,
        # and it returns the corenlp for each.
        # {stories_id => 1, corenlp => {<corenlp data> } }
        # If no corenlp annotation is available for a given story, the json element for that story looks like:
        # {stories_id => 1, corenlp => 'story is not annotated' }
        return self._queryForJson(self.V2_API_URL+'stories/corenlp',
                                  {'stories_id': story_id_list})

    def storyWordMatrix(self, solr_query='', solr_filter='', rows=1000, max_words=None, stopword_length=None,
                        old_stopwords=False):
        # Helpful to feed term-document-matrix driven analyses, like TF-IDF.
        params = dict()
        params['q'] = solr_query
        params['fq'] = solr_filter
        params['rows'] = rows
        params['old_stopwords'] = 1 if old_stopwords else 0
        if max_words is not None:
            params['max_words'] = max_words
        if stopword_length is not None:
            if stopword_length in ['tiny', 'short', 'long']:
                params['stopword_length'] = stopword_length
            else:
                raise ValueError('Error - stopword_length must be "tiny", "short" or "long"')
        return self._queryForJson(self.V2_API_URL+'stories_public/word_matrix/', params)

    def storyTagCount(self, solr_query='', solr_filter='', limit=None, tag_sets_id=None, http_method='GET'):
        params = {'q': solr_query, 'fq': solr_filter}
        if limit is not None:
            params['limit'] = limit
        if tag_sets_id is not None:
            params['tag_sets_id'] = tag_sets_id
        return self._queryForJson(self.V2_API_URL+'stories/tag_count', params, http_method)

    def wordCount(self, solr_query, solr_filter='', languages=None, num_words=500, sample_size=1000,
                  include_stopwords=False, include_stats=False, ngram_size=1, random_seed=None,
                  old_stopwords=False, http_method='POST'):
        params = {
            'q': solr_query,
            'l': languages,
            'num_words': num_words,
            'sample_size': sample_size,
            'include_stopwords': 1 if include_stopwords is True else 0,
            'include_stats': 1 if include_stats is True else 0,
            'ngram_size': ngram_size,
            'random_seed': int(random_seed) if random_seed is not None else None,
            'old_stopwords':  1 if old_stopwords else 0,
        }
        if solr_filter:
            params['fq'] = solr_filter
        return self._queryForJson(self.V2_API_URL+'wc/list', params, http_method)

    def tag(self, tags_id):
        # Details about one tag
        return self._queryForJson(self.V2_API_URL+'tags/single/{}'.format(tags_id))[0]

    def tagList(self, tag_sets_id=None, last_tags_id=0, rows=20, public_only=False, name_like=None,
                similar_tags_id=None):
        # List all the tags in one tag set, of multipe if tag_sets_id is an array
        params = {
            'last_tags_id': last_tags_id,
            'rows': rows,
            'public': 1 if public_only is True else 0
        }
        if tag_sets_id is not None:
            params['tag_sets_id'] = tag_sets_id
        if name_like is not None:
            params['search'] = name_like
        if similar_tags_id is not None:
            params['similar_tags_id'] = similar_tags_id
        return self._queryForJson(self.V2_API_URL+'tags/list', params)

    def tagSet(self, tag_sets_id):
        # Details about one tag set
        return self._queryForJson(self.V2_API_URL+'tag_sets/single/{}'.format(tag_sets_id))[0]

    def tagSetList(self, last_tag_sets_id=0, rows=20):
        # List all the tag sets
        return self._queryForJson(self.V2_API_URL+'tag_sets/list',
                                  {'last_tag_sets_id': last_tag_sets_id, 'rows': rows})

    def controversyDump(self, controversy_dumps_id):
        # Details about one controversy dump
        return self._queryForJson(self.V2_API_URL+'controversy_dumps/single/{}'.format(controversy_dumps_id))[0]

    def controversyDumpTimeSlice(self, controversy_dump_time_slices_id):
        # Details about one controversy dump time slice
        return self._queryForJson(self.V2_API_URL+'controversy_dump_time_slices/single/{}'.format(
            controversy_dump_time_slices_id))[0]

    def _queryForFile(self, url, params=None, http_method='GET', json_data=None):
        response = self._query(url, params, http_method, json_data)
        return response.content

    def _queryForJson(self, url, params=None, http_method='GET', json_data=None):
        # Helper that returns queries to the API as real objects
        response = self._query(url, params, http_method, json_data)
        # print response.content
        response_json = response.json()
        # print json.dumps(response_json, indent=2)
        if 'error' in response_json:
            logger.error(u'Error in response from server on request to {}: {}'.format(url, response_json['error']))
            raise mediacloud.error.MCException(response_json['error'], requests.codes['ok'])
        return response_json

    @staticmethod
    def _url_length(url, params):
        # this has to be smart to handle ints, ascii strings, and unicode strings
        param_value_length = 0
        for v in params.values():
            try:
                param_value_length += len("{}".format(v))   # using str call here to compute length of ints
            except UnicodeEncodeError:  # it is a unicode string, so str called failed, but len call will work
                param_value_length += len(v)
        param_key_length = sum([len("{}".format(k)) for k in params.keys()])
        total_url_length = len(url) + param_key_length + param_value_length
        return total_url_length

    def _query(self, url, params=None, http_method='GET', json_data=None):
        start_time = time.time()
        logger.debug(u"query {} to {} with {} and {}".format(http_method, url, params, _remove_private_info(json_data)))
        if params is None:
            params = {}
#        if (http_method is not 'PUT_JSON') and (not isinstance(params, dict)):
#            raise ValueError('Queries must include a dict of parameters')
        if ('key' not in params) and (http_method != 'POST_JSON'):
            params['key'] = self._auth_token
        if self._all_fields:
            params['all_fields'] = 1
        if http_method == 'GET':
            # automatically switch to POST if request too long
            try:
                if self._url_length(url, params) > MAX_HTTP_GET_CHARS:
                    r = requests.post(url, data=params, headers={'Accept': 'application/json'})
                else:
                    r = requests.get(url, params=params, headers={'Accept': 'application/json'})
            except Exception as e:
                logger.error(u'Failed to GET or POST to {} because {}'.format(url, e))
                raise e
        elif http_method == 'PUT_JSON':
            try:
                # the json to post could be an array (not a dict), so we need to add the params and
                # the json to post differently
                if json_data is None:
                    params_to_send = {'key': self._auth_token}
                    data_to_send = params
                else:
                    params_to_send = params
                    data_to_send = json_data
                r = requests.put(url, params=params_to_send, data=json.dumps(data_to_send),
                                 headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            except Exception as e:
                logger.exception(e)
                raise e
        elif http_method == 'PUT':
            try:
                r = requests.put(url, params=params, headers={'Accept': 'application/json'})
            except Exception as e:
                logger.error(u'Failed to PUT {} because {}'.format(url, e))
                raise e
        elif http_method == 'POST_JSON':  # posts JSON data, needs key in url
            try:
                url_with_key = url + "?key="+self._auth_token
                r = requests.post(url_with_key, data=json.dumps(params),
                                  headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            except Exception as e:
                logger.error(u'Failed to POST JSON {} because {}'.format(url, e))
                raise e
        elif http_method == 'POST':  # post Form data
            try:
                url_with_key = url + "?key=" + self._auth_token
                r = requests.post(url_with_key, params, headers={'Accept': 'application/json'})
            except Exception as e:
                logger.error(u'Failed to POST {} because {}'.format(url, e))
                raise e
        else:
            raise ValueError('Error - unsupported HTTP method {}'.format(http_method))
        end_time = time.time()
        logger.debug(u"Profiling: {}s for {} to {} (with {} / {})".format(end_time - start_time, http_method,
                                                                          url, params,
                                                                          json.dumps(_remove_private_info(json_data))))
        if r.status_code is not requests.codes['ok']:
            logger.info(u'Bad HTTP response to {}: {} {}'.format(r.url, r.status_code, r.reason))
            # logger.info(u'\t{}'.format(r.content))
            msg = u'Error - got a HTTP status code of {} with the message "{}", body: {}'.format(r.status_code,
                                                                                                 r.reason, r.text)
            raise mediacloud.error.MCException(msg, r.status_code)
        return r

    @staticmethod
    @mediacloud.error.deprecated
    def publish_date_query(start_date, end_date, start_date_inclusive=True, end_date_inclusive=False,
                           field='publish_day'):
        """
        This is deprecated because the defaults didn't match what we use on the online tools, so it was causing
        confusion. Use the `dates_as_query_clause` helper instead.
        """
        valid_date_fields = ['publish_day', 'publish_week', 'publish_month', 'publish_year']
        if field not in valid_date_fields:
            raise mediacloud.error.MCException("Not a valid date field {}".format(field))
        return field+':' + _solr_date_range(start_date, end_date, start_date_inclusive, end_date_inclusive)

    @staticmethod
    def dates_as_query_clause(start_date, end_date, start_date_inclusive=True, end_date_inclusive=True,
                           field='publish_day'):
        valid_date_fields = ['publish_day', 'publish_week', 'publish_month', 'publish_year']
        if field not in valid_date_fields:
            raise mediacloud.error.MCException("Not a valid date field {}".format(field))
        return field+':' + _solr_date_range(start_date, end_date, start_date_inclusive, end_date_inclusive)



    def topicMediaList(self, topics_id, **kwargs):
        params = {}
        valid_params = ['media_id', 'sort', 'name', 'limit',
                        'link_id', 'snapshots_id', 'foci_id', 'timespans_id', 'q']
        _validate_params(params, valid_params, kwargs)
        if 'sort' in params:
            _validate_topic_sort_param(params['sort'])
        results = self._queryForJson(self.V2_API_URL+'topics/{}/media/list'.format(topics_id), params)
        # add in parsed out metadata to make life for users easier
        results['media'] = self._addMetadataTagsToMediaList(results['media'])
        return results

    def topicMediaLinks(self, topics_id, **kwargs):
        params = {}
        valid_params = ['snapshots_id', 'foci_id', 'timespans_id', 'limit', 'link_id']
        _validate_params(params, valid_params, kwargs)
        links = self._queryForJson(self.V2_API_URL+'topics/{}/media/links'.format(topics_id), params)
        # returns media_ids... you'll have to add the media information yourself :-(
        return links

    def topicStoryList(self, topics_id, **kwargs):
        params = {}
        valid_params = ['q', 'fq', 'sort', 'stories_id', 'link_to_stories_id', 'link_from_stories_id',
                        'link_to_media_id', 'link_from_media_id', 'media_id', 'limit', 'link_id', 'snapshots_id',
                        'foci_id', 'timespans_id']
        _validate_params(params, valid_params, kwargs)
        if 'sort' in params:
            _validate_topic_sort_param(params['sort'])
        stories = self._queryForJson(self.V2_API_URL+'topics/{}/stories/list'.format(topics_id), params)
        # can't add in metadata here because the tags aren't returned from this call :-(
        return stories

    def topicStoryLinks(self, topics_id, **kwargs):
        params = {}
        valid_params = ['snapshots_id', 'foci_id', 'timespans_id', 'limit', 'link_id']
        _validate_params(params, valid_params, kwargs)
        links = self._queryForJson(self.V2_API_URL+'topics/{}/stories/links'.format(topics_id), params)
        # returns stories_ids... you'll have to add the story information yourself :-(
        return links

    def topicStoryListFacebookData(self, topics_id, **kwargs):
        # For technical reasons this data is too hard to include in the topicStoryList results :-(
        params = {}
        valid_params = ['q', 'fq', 'limit', 'link_id', 'snapshots_id', 'foci_id', 'timespans_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/{}/stories/facebook'.format(topics_id), params)

    def topicStoryCount(self, topics_id, **kwargs):
        params = {}
        valid_params = ['q', 'fq', 'snapshots_id', 'foci_id', 'timespans_id', 'split', 'split_period']
        _validate_params(params, valid_params, kwargs)
        _validate_bool_params(params, 'split')
        if 'split_period' in params:
            params['split_period'] = _validate_split_period_param(params['split_period'])
        return self._queryForJson(self.V2_API_URL+'topics/{}/stories/count'.format(topics_id), params)

    def topicWordCount(self, topics_id, **kwargs):
        params = {}
        valid_params = ['q', 'fq', 'languages', 'num_words', 'sample_size', 'include_stopwords',
                        'include_stats', 'snapshots_id', 'foci_id', 'timespans_id', 'ngram_size']
        _validate_params(params, valid_params, kwargs)
        _validate_bool_params(params, 'include_stopwords', 'include_stats')
        return self._queryForJson(self.V2_API_URL+'topics/{}/wc/list'.format(topics_id), params)

    def topic(self, topics_id):
        # Details about one controversy
        return self._queryForJson(self.V2_API_URL+'topics/single/{}'.format(topics_id))['topics'][0]

    def topicList(self, link_id=None, name=None, public=None, limit=20):
        # List all the controversies
        params = {}
        if link_id is not None:
            params['link_id'] = link_id
        if public is not None:
            params['public'] = 1 if public is True else 0
        if name is not None:
            params['name'] = name
        params['limit'] = limit
        return self._queryForJson(self.V2_API_URL+'topics/list', params)

    def topicSnapshotCancel(self, topics_id, snapshots_id):
        params = {'snapshots_id': snapshots_id}
        return self._queryForJson(self.V2_API_URL + 'topics/{}/snapshots/cancel'.format(topics_id), params, 'POST_JSON')

    def topicSnapshotList(self, topics_id):
        return self._queryForJson(self.V2_API_URL+'topics/{}/snapshots/list'.format(topics_id))['snapshots']

    def topicCreateSnapshot(self, topics_id, **kwargs):
        params = {}
        valid_params = ['note']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL + 'topics/{}/snapshots/create'.format(topics_id), params, 'POST_JSON')

    def topicGenerateSnapshot(self, topics_id, **kwargs):
        params = {}
        valid_params = ['note', 'snapshots_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/{}/snapshots/generate'.format(topics_id), params, 'POST_JSON')

    def topicSnapshotGenerateStatus(self, topics_id):
        return self._queryForJson(self.V2_API_URL+'topics/{}/snapshots/generate_status'.format(topics_id))

    def topicSnapshotWord2VecModel(self, topics_id, snapshots_id, model_id):
        return self._queryForFile(self.V2_API_URL+'topics/{}/snapshots/{}/word2vec_model/{}'.format(topics_id,
                                                                                                    snapshots_id,
                                                                                                    model_id))

    def topicCreate(self, name, solr_seed_query, description, start_date, end_date, media_ids=[], media_tags_ids=[],
                    **kwargs):
        valid_optional_params = ['max_iterations', 'is_public', 'ch_monitor_id', 'twitter_topics_id',
                                 'is_logogram', 'max_stories']
        params = dict()
        params['name'] = name
        params['solr_seed_query'] = solr_seed_query
        params['description'] = description
        params['start_date'] = start_date
        params['end_date'] = end_date
        params['media_ids'] = media_ids
        params['media_tags_ids'] = media_tags_ids
        _validate_params(params, valid_optional_params, kwargs)
        if (not media_ids) and (not media_tags_ids):
            raise ValueError('You have to specify media_ids or media_tags_ids')
        return self._queryForJson(self.V2_API_URL+'topics/create', params, 'POST_JSON')

    def topicReset(self, topics_id):
        return self._queryForJson(self.V2_API_URL + 'topics/{}/reset'.format(topics_id), http_method='PUT')

    def topicUpdate(self, topics_id, **kwargs):
        valid_params = [
            'name', 'solr_seed_query', 'description', 'start_date', 'end_date', 'media_ids', 'media_tags_ids',
            'max_iterations', 'is_public', 'ch_monitor_id', 'twitter_topics_id', 'is_logogram', 'max_stories'
        ]
        params = {}
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/{}/update'.format(topics_id), params, 'PUT_JSON')

    def topicSpider(self, topics_id, snapshots_id=None):
        # this will generate a new snapshot for you (ie. run a spider job and then a snapshot job)
        params = {}
        if snapshots_id:
            params['snapshots_id'] = snapshots_id
        return self._queryForJson(self.V2_API_URL + 'topics/{}/spider'.format(topics_id), params, 'POST_JSON')

    def topicSpiderStatus(self, topics_id):
        return self._queryForJson(self.V2_API_URL + 'topics/{}/spider_status'.format(topics_id))

# Not implemented yet
#    def topicSpiderIterationsList(self, topics_id):
#        return self._queryForJson(self.V2_API_URL + 'topics/{}/iterations/list'.format(topics_id))

    def topicTimespanList(self, topics_id, **kwargs):
        params = {}
        valid_params = ['snapshots_id', 'foci_id', 'timespans_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/{}/timespans/list'.format(topics_id), params)['timespans']

    def topicFocalSetDefinitionList(self, topics_id):
        return self._queryForJson(self.V2_API_URL+'topics/{}/focal_set_definitions/list'.
                                  format(topics_id))['focal_set_definitions']

    def topicFocalSetDefinitionCreate(self, topics_id, name, description, focal_technique):
        params = {
            'name': name,
            'description': description,
            'focal_technique': focal_technique
        }
        if params['focal_technique'] not in [self.FOCAL_TECHNIQUE_BOOLEAN_QUERY]:
            raise ValueError('%s is not a valid focal technique' % params['focal_technique'])
        return self._queryForJson(self.V2_API_URL+'topics/{}/focal_set_definitions/create'.format(topics_id),
                                  params, http_method='POST_JSON')['focal_set_definitions'][0]

    def topicFocalSetDefinitionDelete(self, topics_id, focal_set_definitions_id):
        return self._queryForJson(self.V2_API_URL+'topics/{}/focal_set_definitions/{}/delete'.format(
            topics_id, focal_set_definitions_id), http_method='PUT')

    def topicFocalSetDefinitionUpdate(self, topics_id, focal_set_definitions_id, **kwargs):
        params = {}
        valid_params = ['name', 'description']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/{}/focal_set_definitions/{}/update'.format(
            topics_id, focal_set_definitions_id), params, http_method='PUT')['focal_set_definitions']

    def topicFocalSetList(self, topics_id, **kwargs):
        params = {}
        valid_params = ['snapshots_id', 'timespans_id', 'foci_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/{}/focal_sets/list'.format(topics_id),
                                  params)['focal_sets']

    def topicFocusDefinitionList(self, topics_id, focal_set_definitions_id):
        params = dict()
        params['focal_set_definitions_id'] = focal_set_definitions_id
        return self._queryForJson(self.V2_API_URL+'topics/{}/focus_definitions/list'.format(topics_id),
                                  params)['focus_definitions']

    def topicFocusDefinitionCreate(self, topics_id, **kwargs):
        params = {}
        valid_params = ['name', 'description', 'query', 'focal_set_definitions_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/{}/focus_definitions/create'.format(topics_id),
                                  params, http_method='POST_JSON')['focus_definitions']

    def topicFocusDefinitionUpdate(self, topics_id, focus_definitions_id, **kwargs):
        params = {}
        valid_params = ['name', 'description', 'query']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/{}/focus_definitions/{}/update'.format(
            topics_id, focus_definitions_id), params, http_method='PUT_JSON')['focus_definitions']

    def topicFocusDefinitionDelete(self, topics_id, focus_definitions_id):
        return self._queryForJson(self.V2_API_URL+'topics/{}/focus_definitions/{}/delete'.format(
            topics_id, focus_definitions_id), http_method='PUT')

    def topicFociList(self, topics_id, focal_sets_id):
        params = {'focal_sets_id': focal_sets_id}
        return self._queryForJson(self.V2_API_URL+'topics/{}/foci/list'.format(topics_id), params)['foci']

    @mediacloud.error.deprecated
    def topicMediaMap(self, topics_id, **kwargs):
        params = {}
        valid_params = ['color_field', 'num_media', 'include_weights', 'num_links_per_medium',
                        'snapshots_id', 'foci_id', 'timespans_id']
        _validate_params(params, valid_params, kwargs)
        return self._query(self.V2_API_URL+'topics/{}/media/map'.format(topics_id), params).content

    @mediacloud.error.deprecated
    def topicMediaMapDownload(self, topics_id, timespan_maps_id, format):
        """
        New endpoint format for downloading auto-generated maps for each timespan in a topic.
        :param topics_id:
        :param timespan_maps_id: as reported by topicMediaMapList
        :param format: 'svg' or 'gexf' (should match what topicMediaMapList reports for timespan_maps_id)
        :return:
        """
        return self._query(self.V2_API_URL+'topics/{}/media/map'.format(topics_id),
                           {'timespan_maps_id': timespan_maps_id, 'format': format}).content

    def topicMediaMapList(self, topics_id, **kwargs):
        params = {}
        valid_params = ['timespans_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/{}/media/list_maps'.format(topics_id), params)

    def userPermissionsList(self):
        return self._queryForJson(self.V2_API_URL+'topics/permissions/user/list')

    def topicPermissionsList(self, topics_id):
        return self._queryForJson(self.V2_API_URL+'topics/{}/permissions/list'.format(topics_id))

    def topicPermissionsUpdate(self, topics_id, email, permission):
        _validate_permission_param(permission)
        params = {
            'email': email,
            'permission': permission
        }
        return self._queryForJson(self.V2_API_URL+'topics/{}/permissions/update'.format(topics_id), params, 'PUT_JSON')

    def topicAddSeedQuery(self, topics_id, platform, source, query):
        params = {
            'topics_id': topics_id,
            'platform': platform,  # twitter or web
            'source': source,  # 'crimson_hexagon' or 'archive_org'
            'query': query,  # boolean query terms in correct format, or ID, or something
        }
        return self._queryForJson(self.V2_API_URL + 'topics/{}/add_seed_query'.format(topics_id), params, 'PUT_JSON')

    def topicRemoveSeedQuery(self, topics_id, topic_seed_queries_id):
        params = {
            'topic_seed_queries_id': topic_seed_queries_id,
        }
        return self._queryForJson(self.V2_API_URL + 'topics/{}/remove_seed_query'.format(topics_id), params, 'PUT_JSON')

    '''
    # not implemented yet
    def topicAddTimespan(self, topics_id, **kwargs):
        params = {}
        valid_params = ['start_date', 'end_date']
        _validate_params(params, valid_params, kwargs)
        _validate_date_params(params, valid_params)
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/timespans/add_dates', params, 'POST_JSON')
    '''

    def storyIsSyndicatedFromAP(self, content):
        params = {
            'content': content,
        }
        return self._queryForJson(self.V2_API_URL+'util/is_syndicated_ap', params, 'PUT_JSON')

    def topicInfo(self):
        return self._queryForJson(self.V2_API_URL + 'topics/info')

    def topicTimespanFiles(self, topics_id, **kwargs):
        params = {}
        valid_params = ['timespans_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/{}/list_timespan_files'.format(topics_id), params)


class AdminMediaCloud(MediaCloud):
    # A MediaCloud API client that includes admin-only methods, including to writing back data to MediaCloud.

    def story(self, stories_id, raw_1st_download=False, corenlp=False, sentences=False, text=False):
        # Full details about one story.  Handy shortcut to storyList if you want sentences broken out
        return self._queryForJson(self.V2_API_URL+'stories/single/{}'.format(stories_id),
                                  {'raw_1st_download': 1 if raw_1st_download else 0,
                                   'corenlp': 1 if corenlp else 0,
                                   'sentences': 1 if sentences else 0,
                                   'text': 1 if text else 0
                                   })[0]

    def storyList(self, solr_query='', solr_filter='', last_processed_stories_id=0, rows=20,
                  wc=False, feeds_id=None, sort=MediaCloud.SORT_PROCESSED_STORIES_ID, raw_1st_download=False,
                  corenlp=False, sentences=False, auth=False, ap_stories_id=0, show_feeds=False, text=False):
        # This combination doesn't produce expected behaviour
        if (sort == MediaCloud.SORT_RANDOM) and (last_processed_stories_id not in [0, None]):
            raise ValueError("You can't page through randomly sorted story lists")
        # Search for stories and page through results
        stories = self._queryForJson(self.V2_API_URL+'stories/list',
                                     {'q': solr_query,
                                      'fq': solr_filter,
                                      'last_processed_stories_id': last_processed_stories_id,
                                      'rows': rows,
                                      'raw_1st_download': 1 if raw_1st_download else 0,
                                      'corenlp': 1 if corenlp else 0,    # this is slow - use storyCoreNlList instead
                                      'sentences': 1 if sentences else 0,
                                      'text': 1 if text else 0,
                                      'ap_stories_id': 1 if ap_stories_id else 0,
                                      'sort': sort,
                                      'wc': 1 if wc is True else 0,
                                      'feeds_id': feeds_id,
                                      'show_feeds': 1 if show_feeds is True else 0,
                                      }, http_method='POST')
        stories_with_metadata = self._addMetadataTagsToStoryList(stories)
        return stories_with_metadata

    def storyUpdate(self, stories_id, **kwargs):
        params = {}
        valid_params = ['title', 'url', 'guid', 'language', 'description', 'publish_date', 'confirm_date', 'undateable']
        _validate_params(params, valid_params, kwargs)
        _validate_bool_params(params, 'confirm_date', 'undateable')
        params['stories_id'] = stories_id
        return self._queryForJson(self.V2_API_URL+'stories/update', {}, 'PUT_JSON', params)

    def sentenceList(self, solr_query, solr_filter='', start=0, rows=1000, sort=MediaCloud.SORT_PUBLISH_DATE_ASC):
        params = {'q': solr_query, 'fq': solr_filter, 'start': start, 'rows': rows, 'sort': sort}
        # Search for sentences and page through results
        return self._queryForJson(self.V2_API_URL+'sentences/list', params, 'POST')

    def tagStories(self, tags=None, clear_others=False):
        # Add some tags to stories. The tags parameter should be a list of StoryTag objects.
        params = {}
        if clear_others is True:
            params['clear_tag_sets'] = 1
        if tags is None:
            tags = {}
        custom_tags = []
        for tag in tags:
            if tag.__class__ is not StoryTag:
                raise ValueError('To use tagStories you must send in a list of StoryTag objects')
            custom_tags.append(tag.getParams())
        return self._queryForJson(self.V2_API_URL+'stories/put_tags', params, 'PUT_JSON', custom_tags)

    def tagMedia(self, tags=None, clear_others=False):
        # Add some tags to media (ie. put them in a colleciton or add metadata to them).
        # The tags parameter should be a list of MediaTag objects.
        params = {}
        if clear_others is True:
            params['clear_tag_sets'] = 1
        if tags is None:
            tags = {}
        custom_tags = []
        for tag in tags:
            if tag.__class__ is not MediaTag:
                raise ValueError('To use tagMedia you must send in a list of MediaTag objects')
            custom_tags.append(tag.getParams())
        return self._queryForJson(self.V2_API_URL+'media/put_tags', params, 'PUT_JSON', custom_tags)

    def createTag(self, tag_sets_id, name, label, description, is_static=False, show_on_media=False,
                  show_on_stories=False):
        params = {
            'tag_sets_id': tag_sets_id,
            'tag': name,
            'label': label,
            'description': description,
            'is_static': 1 if is_static else 0,
            'show_on_media': 1 if show_on_media else 0,
            'show_on_stories': 1 if show_on_stories else 0
        }
        return self._queryForJson(self.V2_API_URL+'tags/create', params, 'POST_JSON')

    def updateTag(self, tags_id, name=None, label=None, description=None, is_static=None, show_on_media=None,
                  show_on_stories=None, tag_sets_id=None):
        params = {'tags_id': tags_id}
        if name is not None:
            params['tag'] = name
        if label is not None:
            params['label'] = label
        if tag_sets_id is not None:
            params['tag_sets_id'] = tag_sets_id
        if description is not None:
            params['description'] = description
        if is_static is not None:
            params['is_static'] = 1 if is_static else 0
        if show_on_media is not None:
            params['show_on_media'] = 1 if show_on_media else 0
        if show_on_stories is not None:
            params['show_on_stories'] = 1 if show_on_stories else 0
        return self._queryForJson(self.V2_API_URL+'tags/update/', {}, 'PUT_JSON', params)

    def createTagSet(self, name, label, description):
        params = {
            'name': name,
            'label': label,
            'description': description,
        }
        return self._queryForJson(self.V2_API_URL+'tag_sets/create', params, 'POST_JSON')

    def updateTagSet(self, tag_sets_id, name=None, label=None, description=None):
        params = {'tag_sets_id': tag_sets_id}
        if name is not None:
            params['name'] = name
        if label is not None:
            params['label'] = label
        if description is not None:
            params['description'] = description

        return self._queryForJson(self.V2_API_URL+'tag_sets/update/', {}, 'PUT_JSON', params)

    def feedCreate(self, media_id, name, url, feed_type='syndicated', active=True):
        _validate_feed_type(feed_type)
        params = {
            'media_id': media_id,
            'name': name,
            'url': url,
            'type': feed_type,
            'active': active,
        }
        return self._queryForJson(self.V2_API_URL+'feeds/create', params, 'POST_JSON')

    def feedUpdate(self, feeds_id, name=None, url=None, feed_type='syndicated', active=True):
        _validate_feed_type(feed_type)
        params = {'feeds_id': feeds_id}
        if name is not None:
            params['name'] = name
        if url is not None:
            params['url'] = url
        if feed_type is not None:
            params['type'] = feed_type
        if active is not None:
            params['active'] = active
        return self._queryForJson(self.V2_API_URL+'feeds/update', params, 'PUT_JSON')

    def feedsScrape(self, media_id):
        params = {'media_id': media_id}
        return self._queryForJson(self.V2_API_URL+'feeds/scrape', params, 'POST_JSON')

    def feedsScrapeStatus(self, media_id=None):
        params = {'media_id': media_id}
        return self._queryForJson(self.V2_API_URL+'feeds/scrape_status', params)

    def mediaCreate(self, media_items):
        # validate and clean input
        valid_params = ['url', 'name', 'foreign_rss_links', 'content_delay', 'feeds', 'tags_ids', 'editor_notes',
                        'public_notes', 'is_monitored']
        boolean_params = ['foreign_rss_links', 'is_monitored']
        for media in media_items:
            for k in media:
                if k not in valid_params:
                    raise ValueError('Invalid param in attempt to create media: {}'.format(k))
                if k in boolean_params:
                    media[k] = 1 if k else 0
            if (media['url'] is None) or (not media['url']):
                raise ValueError('You must supply a media url')
        return self._queryForJson(self.V2_API_URL+'media/create', media_items, 'POST_JSON')

    def mediaUpdate(self, media_id, new_props):
        # validate and clean inputs
        valid_params = ['url', 'name', 'foreign_rss_links', 'content_delay', 'editor_notes', 'public_notes',
                        'is_monitored']
        boolean_params = ['is_monitored']
        for k in new_props:
            if k not in valid_params:
                raise ValueError('Invalid param in attempt to update media: {}'.format(k))
            if k in boolean_params:
                new_props[k] = 1 if k else 0
        if 'url' in new_props and (new_props['url'] is None or not new_props['url']):
            raise ValueError('The media URL can\'t be empty')
        new_props['media_id'] = media_id
        return self._queryForJson(self.V2_API_URL+'media/update', new_props, 'PUT_JSON')

    def mediaSuggestionsList(self, all=False, tags_id=None):
        params = {}
        if all is not None:
            params['all'] = 1 if all else 0
        if tags_id is not None:
            params['tags_id'] = tags_id
        return self._queryForJson(self.V2_API_URL+'media/list_suggestions', params)['media_suggestions']

    def mediaSuggestionsMark(self, media_suggestions_id, status, mark_reason, media_id=None):
        if status not in ['approved', 'rejected']:
            raise ValueError('Invalid media suggestion status: {}'.format(status))
        params = {
            'media_suggestions_id': media_suggestions_id,
            'status': status,
            'mark_reason': mark_reason,
        }
        if media_id is not None:
            params['media_id'] = media_id
        return self._queryForJson(self.V2_API_URL+'media/mark_suggestion', params, 'PUT_JSON')

    def user(self, auth_users_id):
        return self._queryForJson(self.V2_API_URL + 'users/single/{}'.format(auth_users_id))

    def userList(self, auth_users_id=None, search=None, link_id=None):
        # search shuld be email or full_name
        # auth_users_id should be an array
        params = {}
        if auth_users_id:
            params['auth_users_id'] = auth_users_id
        if search:
            params['search'] = search
        if link_id:
            params['link_id'] = link_id
        return self._queryForJson(self.V2_API_URL + 'users/list', params)

    def userUpdate(self, auth_users_id, **kwargs):
        params = {'auth_users_id': auth_users_id}
        valid_params = ['full_name', 'email', 'notes', 'roles', 'max_topic_stories', 'weekly_requests_limit',
                        'active', 'has_consented']
        _validate_params(params, valid_params, kwargs)
        _validate_bool_params(params, 'active')
        return self._queryForJson(self.V2_API_URL + 'users/update', params, 'PUT_JSON')

    def userDelete(self, user_id):
        params = {'auth_users_id': user_id}
        return self._queryForJson(self.V2_API_URL + 'users/delete', params, 'PUT_JSON')

    def validUserRoles(self):
        # list all the possible roles that exist for users
        return self._queryForJson(self.V2_API_URL + 'users/list_roles')

    def topicSnapshotFiles(self, topics_id, **kwargs):
        params = {}
        valid_params = ['snapshots_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/{}/list_snapshot_files'.format(topics_id), params)


def _solr_date_range(start_date, end_date, start_date_inclusive=True, end_date_inclusive=True):
    ret = ''
    if start_date_inclusive:
        ret += '['
    else:
        ret += '{'
    ret += _zi_time(start_date)
    ret += " TO "
    ret += _zi_time(end_date)
    if end_date_inclusive:
        ret += ']'
    else:
        ret += '}'
    return ret


def _zi_time(d):
    return datetime.datetime.combine(d, datetime.time.min).isoformat() + "Z"


def _chunkify(data, chunk_size):
    # Helper method to break an array into a set of smaller arrays
    return [data[x:x+chunk_size] for x in range(0, len(data), chunk_size)]


def _validate_params(params, valid_params, args):
    for key in args.keys():
        if key not in valid_params:
            raise ValueError("{} is not a valid argument for this api method".format(key))
        params[key] = args[key]
    return params


def _validate_split_period_param(period):
    if period not in [None, 'day', 'week', 'month', 'year']:
        raise ValueError('Invalid story count split period - "{}"'.format(period))
    return period


def _validate_sort_param(order):
    if order not in [None, 'social', 'inlink']:
        raise ValueError('Sort must be either social or inlink')


def _validate_topic_sort_param(order):
    if order not in [None, 'inlink', 'facebook', 'twitter', 'random', '',
                     'post_count', 'author_count', 'channel_count']:
        raise ValueError('Invalid sort specified: {}'.format(order))


def _validate_permission_param(permission):
    if permission not in ['none', 'read', 'write', 'admin']:
        raise ValueError('Permission must be none, read, write or admin')


def _validate_bool_params(params, *args):
    for arg in args:
        if arg in params:
            if params[arg] not in [True, False]:
                raise ValueError("{} must be a python boolean (True or False)".format(arg))
            params[arg] = 1 if params[arg] is True else 0
    return params


def _validate_date_params(params, *args):
    for arg in args:
        if arg in params:
            datetime.datetime.strptime(params[arg], '%Y-%m-%d')  # will throw a ValueError if invalid
    return params


def _validate_feed_type(feed_type):
    if feed_type not in VALID_FEED_TYPES:
        raise ValueError('feed_type must be on of []'.format(', '.join(VALID_FEED_TYPES)))


def _remove_private_info(original_data):
    if original_data is None:
        return None
    try:
        return {k: v for k, v in original_data.items() if k not in ['password', 'key']}
    except AttributeError:
        logger.warning("Can't remove private info from something that isn't a dict")
        return original_data
