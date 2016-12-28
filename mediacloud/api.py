import logging
import json
import datetime
from collections import namedtuple
import urllib
import requests
import mediacloud
import mediacloud.error
from mediacloud.tags import StoryTag, SentenceTag, MediaTag

MAX_HTTP_GET_CHARS = 4000   # experimentally determined for our main servers (conservative)

class MediaCloud(object):
    '''
    Simple client library for the MediaCloud API v2
    '''

    V2_API_URL = "https://api.mediacloud.org/api/v2/"

    SORT_PUBLISH_DATE_ASC = "publish_date_asc"
    SORT_PUBLISH_DATE_DESC = "publish_date_desc"
    SORT_RANDOM = "random"
    SORT_PROCESSED_STORIES_ID = "processed_stories_id"
    SORT_BITLY_CLICK_COUNT = "bitly_click_count"

    MSG_CORE_NLP_NOT_ANNOTATED = "story is not annotated"

    SENTENCE_PUBLISH_DATE_FORMAT = "%Y-%m-%d %H:%M:%S" # use with datetime.datetime.strptime

    FOCAL_TECHNIQUE_BOOLEAN_QUERY = "Boolean Query"

    def __init__(self, auth_token=None, all_fields=False):
        self._logger = logging.getLogger(__name__)
        self.setAuthToken(auth_token)
        self.setAllFields(all_fields)

    def setAllFields(self, all_fields):
        '''
        Specify the value of the all_fields param to use for all future requests
        '''
        self._all_fields = all_fields

    def setAuthToken(self, auth_token):
        '''
        Specify the auth_token to use for all future requests
        '''
        self._auth_token = auth_token

    def userAuthToken(self, username, password):
        '''
        Get a auth_token for future requests to use
        '''
        self._logger.debug("Requesting new auth token for "+username)
        response = self._queryForJson(self.V2_API_URL+'auth/single/',
            {'username':username, 'password':password})
        response = response[0]
        if response['result'] == 'found':
            self._logger.debug(" new token is "+response['token'])
            return response['token']
        else:
            self._logger.warn("AuthToken request for "+username+" failed!")
            raise RuntimeError(response['result'])

    def verifyAuthToken(self):
        try:
            self.tagSetList(0, 1)
            return True
        except mediacloud.error.MCException:
            return False
        except Exception as exception:
            self._logger.warn("AuthToken verify failed: %s", exception)
        return False

    def userProfile(self):
        '''
        Returns basic info about the current user, including their roles
        '''
        return self._queryForJson(self.V2_API_URL+'auth/profile')

    def stats(self):
        '''
        High-level stats about the system
        '''
        return self._queryForJson(self.V2_API_URL+'stats')

    def media(self, media_id):
        '''
        Details about one media source
        '''
        return self._queryForJson(self.V2_API_URL+'media/single/'+str(media_id))[0]

    def mediaHealth(self, media_id):
        '''
        Details about one media source
        '''
        return self._queryForJson(self.V2_API_URL+'mediahealth/list',
            {'media_id':media_id})[0]

    def mediaList(self, last_media_id=0, rows=20, name_like=None,
                timespans_id=None, topic_mode=None, tags_id=None, q=None, include_dups=False,
                name_or_tag=None, unhealthy=None, similar_media_id=None):
        '''
        Page through all media sources
        '''
        params = {'last_media_id':last_media_id, 'rows':rows}
        if name_like is not None:
            params['name'] = name_like
        if name_or_tag is not None:
            params['name_or_tag'] = name_or_tag
        if timespans_id is not None:
            params['timespans_id'] = timespans_id
        if topic_mode is not None:
            params['topic_mode'] = topic_mode
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
        return self._queryForJson(self.V2_API_URL+'media/list', params)

    def mediaSuggest(self, url, name=None, feed_url=None, reason=None, collections=[]):
        for c in collections:
            if not isinstance(c, int):
                raise ValueError('The collections must be a list of ids')
        params = {
            'url': url,
            'name': name,
            'feed_url': feed_url,
            'reason': reason,
            'collection': collections
        }
        return self._queryForJson(self.V2_API_URL+'media/suggestions/submit', params, 'PUT_JSON')

    def feed(self, feeds_id):
        '''
        Details about one feed
        '''
        return self._queryForJson(self.V2_API_URL+'feeds/single/'+str(feeds_id))[0]

    def feedList(self, media_id, last_feeds_id=0, rows=20):
        '''
        Page through all the feeds of one media source
        '''
        return self._queryForJson(self.V2_API_URL+'feeds/list',
            {'media_id':media_id, 'last_feeds_id':last_feeds_id, 'rows':rows})

    def storyPublic(self, stories_id):
        '''
        Maintained for backwards compatability
        '''
        return self.story(stories_id)

    def story(self, stories_id):
        '''
        Authenticated Public Users: Details about one story.
        Note that this does NOT include text, nor sentences (due to copyright limitations).
        '''
        return self._queryForJson(self.V2_API_URL+'stories_public/single/'+str(stories_id))[0]

    def storyCount(self, solr_query='', solr_filter=''):
        '''
        The call returns the number of stories returned by Solr for the specified query
        '''
        return self._queryForJson(self.V2_API_URL+'stories_public/count',
                {'q': solr_query,
                 'fq': solr_filter
                })

    def storyPublicList(self, solr_query='', solr_filter='', last_processed_stories_id=0, rows=20,
            wc=False, feeds_id=None, sort=SORT_PROCESSED_STORIES_ID, show_feeds=False):
        '''
        Maintained for backwards compatability
        '''
        return self.storyList(solr_query, solr_filter, last_processed_stories_id, rows, wc, feeds_id, sort)

    def storyList(self, solr_query='', solr_filter='', last_processed_stories_id=0, rows=20,
            wc=False, feeds_id=None, sort=SORT_PROCESSED_STORIES_ID, show_feeds=False):
        '''
        Authenticated Public Users: Search for stories and page through results
        '''
        return self._queryForJson(self.V2_API_URL+'stories_public/list',
                {'q': solr_query,
                 'fq': solr_filter,
                 'last_processed_stories_id': last_processed_stories_id,
                 'rows': rows,
                 'sort': sort,
                 'wc': 1 if wc is True else 0,
                 'feeds_id': feeds_id,
                 'show_feeds': 1 if show_feeds is True else 0,
                })

    def storyCoreNlpList(self, story_id_list):
        '''
        The stories/corenlp call takes as many stories_id= parameters as you want to pass it,
        and it returns the corenlp for each.
        {stories_id => 1, corenlp => {<corenlp data> } }
        If no corenlp annotation is available for a given story, the json element for that story looks like:
        {stories_id => 1, corenlp => 'story is not annotated' }
        '''
        return self._queryForJson(self.V2_API_URL+'stories/corenlp',
            {'stories_id': story_id_list})

    def storyWordMatrix(self, solr_query='', solr_filter='', rows=1000, max_words=None, stopword_length=None):
        '''
        Helpful to feed term-document-matrix driven analyses, like TF-IDF.
        '''
        params = {'q':solr_query, 'fq':solr_filter}
        params['rows'] = rows
        if max_words is not None:
            params['max_words'] = max_words
        if stopword_length is not None:
            if stopword_length in ['tiny', 'short', 'long']:
                params['stopword_length'] = stopword_length
            else:
                raise ValueError('Error - stopword_length must be "tiny", "short" or "long"')
        return self._queryForJson(self.V2_API_URL+'stories_public/word_matrix/', params)

    def sentence(self, story_sentences_id):
        '''
        Return info about a single sentence
        '''
        return self._queryForJson(self.V2_API_URL+'sentences/single/'+str(story_sentences_id))[0]

    def sentenceCount(self, solr_query, solr_filter=' ', split=False, split_start_date=None, split_end_date=None, split_daily=False):
        if split not in [True, False]:
            raise ValueError('split much be a boolean True or False')
        params = {'q':solr_query, 'fq':solr_filter}
        params['split'] = 1 if split is True else 0
        params['split_daily'] = 1 if split_daily is True else 0
        if split is True:
            datetime.datetime.strptime(split_start_date, '%Y-%m-%d')    #will throw a ValueError if invalid
            datetime.datetime.strptime(split_end_date, '%Y-%m-%d')    #will throw a ValueError if invalid
            params['split_start_date'] = split_start_date
            params['split_end_date'] = split_end_date
        return self._queryForJson(self.V2_API_URL+'sentences/count', params)

    def sentenceFieldCount(self, solr_query, solr_filter=' ', sample_size=1000, include_stats=False, field='tags_id_story_sentences', tag_sets_id=None):
        '''
        Right now the fields supported are 'tags_id_stories' or 'tags_id_story_sentences'
        '''
        params = {'q':solr_query, 'fq':solr_filter, 'sample_size':sample_size, 'field':field}
        if tag_sets_id is not None:
            params['tag_sets_id'] = tag_sets_id
        params['include_stats'] = 1 if include_stats is True else 0
        return self._queryForJson(self.V2_API_URL+'sentences/field_count', params)

    def wordCount(self, solr_query, solr_filter='', languages='en', num_words=500, sample_size=1000, include_stopwords=False, include_stats=False):
        params = {
            'q': solr_query,
            'l': languages,
            'num_words': num_words,
            'sample_size': sample_size,
            'include_stopwords': 1 if include_stopwords is True else 0,
            'include_stats': 1 if include_stats is True else 0,
        }
        if len(solr_filter) > 0:
            params['fq'] = solr_filter
        return self._queryForJson(self.V2_API_URL+'wc/list', params)

    def tag(self, tags_id):
        '''
        Details about one tag
        '''
        return self._queryForJson(self.V2_API_URL+'tags/single/'+str(tags_id))[0]

    def tagList(self, tag_sets_id=None, last_tags_id=0, rows=20, public_only=False, name_like=None, similar_tags_id=None):
        '''
        List all the tags in one tag set
        '''
        params = {
            'last_tags_id': last_tags_id
            , 'rows': rows
            , 'public': 1 if public_only is True else 0
        }
        if tag_sets_id is not None:
            params['tag_sets_id'] = tag_sets_id
        if name_like is not None:
            params['search'] = name_like
        if similar_tags_id is not None:
            params['similar_tags_id'] = similar_tags_id
        return self._queryForJson(self.V2_API_URL+'tags/list', params)

    def tagSet(self, tag_sets_id):
        '''
        Details about one tag set
        '''
        return self._queryForJson(self.V2_API_URL+'tag_sets/single/'+str(tag_sets_id))[0]

    def tagSetList(self, last_tag_sets_id=0, rows=20):
        '''
        List all the tag sets
        '''
        return self._queryForJson(self.V2_API_URL+'tag_sets/list',
            {'last_tag_sets_id': last_tag_sets_id, 'rows':rows})

    def controversyDump(self, controversy_dumps_id):
        '''
        Details about one controversy dump
        '''
        return self._queryForJson(self.V2_API_URL+'controversy_dumps/single/'+str(controversy_dumps_id))[0]

    def controversyDumpTimeSlice(self, controversy_dump_time_slices_id):
        '''
        Details about one controversy dump time slice
        '''
        return self._queryForJson(self.V2_API_URL+'controversy_dump_time_slices/single/'+str(controversy_dump_time_slices_id))[0]

    def _queryForJson(self, url, params=None, http_method='GET', json_data=None):
        '''
        Helper that returns queries to the API as real objects
        '''
        response = self._query(url, params, http_method, json_data)
        # print response.content
        response_json = response.json()
        # print json.dumps(response_json, indent=2)
        if 'error' in response_json:
            self._logger.error('Error in response from server on request to '+url+' : '+response_json['error'])
            raise mediacloud.error.MCException(response_json['error'], requests.codes['ok'])
        return response_json

    def _query(self, url, params=None, http_method='GET', json_data=None):
        self._logger.debug("query "+http_method+" to "+url+" with "+str(params)+" and "+str(json_data))
        if params is None:
            params = {}
#        if (http_method is not 'PUT_JSON') and (not isinstance(params, dict)):
#            raise ValueError('Queries must include a dict of parameters')
        if ('key' not in params) and (http_method is not 'POST'):
            params['key'] = self._auth_token
        if self._all_fields:
            params['all_fields'] = 1
        if http_method is 'GET':
            # automatically switch to POST if request too long
            total_url_length = len(url)+sum([len(str(k)) for k in params.keys()])+sum([len(str(v)) for v in params.values()])
            try:
                if total_url_length > MAX_HTTP_GET_CHARS:
                    r = requests.post(url, data=params, headers={'Accept': 'application/json'})
                else:
                    r = requests.get(url, params=params, headers={'Accept': 'application/json'})
            except Exception as e:
                self._logger.error('Failed to GET or POST to url '+url+' because '+str(e))
                raise e
        elif http_method is 'PUT_JSON':
            try:
                # the json to post could be an array (not a dict), so we need to add the params and the json to post differently
                data_to_send = None # as json
                url_with_key = url
                if json_data is None:
                    url_with_key = url_with_key + "?key=" + self._auth_token
                    data_to_send = params
                else:
                    url_with_key = url_with_key + "?" + urllib.urlencode(params)
                    data_to_send = json_data
                    self._logger.info(url_with_key)
                    self._logger.info(json.dumps(data_to_send))
                r = requests.put(url_with_key, data=json.dumps(data_to_send), headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            except Exception as e:
                self._logger.exception(e)
                raise e
        elif http_method is 'PUT':
            try:
                r = requests.put(url, params=params, headers={'Accept': 'application/json'})
            except Exception as e:
                self._logger.error('Failed to PUT url '+url+' because '+str(e))
                raise e
        elif http_method is 'POST': # posts JSON data, needs key in url
            try:
                url_with_key = url + "?key="+self._auth_token
                r = requests.post(url_with_key, data=json.dumps(params), headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            except Exception as e:
                self._logger.error('Failed to POST url '+url+' because '+str(e))
                raise e
        else:
            raise ValueError('Error - unsupported HTTP method %s' % http_method)
        if r.status_code is not requests.codes['ok']:
            self._logger.info('Bad HTTP response to '+r.url +' : '+str(r.status_code)  + ' ' +  str(r.reason))
            self._logger.info('\t' + r.content)
            msg = 'Error - got a HTTP status code of %s with the message "%s", body: %s' % (
                str(r.status_code), str(r.reason), str(r.text))
            raise mediacloud.error.MCException(msg, r.status_code)
        return r

    def publish_date_query(self, start_date, end_date, start_date_inclusive=True, end_date_inclusive=False):
        return 'publish_date:' + _solr_date_range(start_date, end_date, start_date_inclusive, end_date_inclusive)

    def topicMediaList(self, topics_id, **kwargs):
        params = {}
        valid_params = ['media_id', 'sort', 'name', 'limit',
            'link_id', 'snapshots_id', 'foci_id', 'timespans_id']
        _validate_params(params, valid_params, kwargs)
        if 'sort' in params:
            _validate_sort_param(params['sort'])
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/media/list', params)

    def topicStoryList(self, topics_id, **kwargs):
        params = {}
        valid_params = ['q', 'sort', 'stories_id', 'link_to_stories_id', 'link_from_stories_id',
            'link_to_media_id', 'link_from_media_id', 'media_id', 'limit', 'link_id', 'snapshots_id',
            'foci_id', 'timespans_id']
        _validate_params(params, valid_params, kwargs)
        if 'sort' in params:
            _validate_sort_param(params['sort'])
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/stories/list', params)

    def topicStoryCount(self, topics_id, **kwargs):
        params = {}
        valid_params = ['q', 'snapshots_id', 'foci_id', 'timespans_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/stories/count', params)

    def topicWordCount(self, topics_id, **kwargs):
        params = {}
        valid_params = ['q', 'fq', 'languages', 'num_words', 'sample_size', 'include_stopwords',
            'include_stats', 'snapshots_id', 'foci_id', 'timespans_id']
        _validate_params(params, valid_params, kwargs)
        _validate_bool_params('include_stopwords', 'include_stats')
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/wc/list', params)

    def topicSentenceCount(self, topics_id, **kwargs):
        params = {}
        valid_params = ['q', 'fq', 'split', 'split_start_date', 'split_end_date',
            'snapshots_id', 'foci_id', 'timespans_id']
        _validate_params(params, valid_params, kwargs)
        _validate_bool_params(params, 'split', 'split_daily')
        if 'split' in params and params['split'] is True:
            _validate_date_params(params, 'split_start_date', 'split_end_date')
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/sentences/count', params)

    def topic(self, topics_id):
        '''
        Details about one controversy
        '''
        return self._queryForJson(self.V2_API_URL+'topics/single/'+str(topics_id))['topics'][0]

    def topicList(self, link_id=None):
        '''
        List all the controversies
        '''
        params = {}
        if link_id is not None:
            params['link_id'] = link_id
        return self._queryForJson(self.V2_API_URL+'topics/list', params)

    def topicSnapshotList(self, topics_id):
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/snapshots/list')['snapshots']

    def topicGenerateSnapshot(self, topics_id, **kwargs):
        params = {}
        valid_params = ['note']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/snapshots/generate', params, 'POST')

    def topicTimespanList(self, topics_id, **kwargs):
        params = {}
        valid_params = ['snapshots_id', 'foci_id', 'timespans_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/timespans/list', params)['timespans']

    def topicFocalSetDefinitionList(self, topics_id):
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/focal_set_definitions/list')['focal_set_definitions']

    def topicFocalSetDefinitionCreate(self, topics_id, name, description, focal_technique):
        params = {
            'name': name,
            'description': description,
            'focal_technique': focal_technique
        }
        if params['focal_technique'] not in [self.FOCAL_TECHNIQUE_BOOLEAN_QUERY]:
            raise ValueError('%s is not a valid focal technique' % params['focal_technique'])
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/focal_set_definitions/create',
            params, http_method='POST')['focal_set_definitions'][0]

    def topicFocalSetDefinitionDelete(self, topics_id, focal_set_definitions_id):
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/focal_set_definitions/'+
            focal_set_definitions_id+'/delete', http_method='PUT')

    def topicFocalSetDefinitionUpdate(self, topics_id, focal_set_definitions_id, **kwargs):
        params = {}
        valid_params = ['name', 'description']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/focal_set_definitions/'+
            str(focal_set_definitions_id)+'/update', params, http_method='PUT')['focal_set_definitions']

    def topicFocalSetList(self, topics_id, **kwargs):
        params = {}
        valid_params = ['snapshots_id', 'timespans_id', 'foci_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/focal_sets/list',
            params)['focal_sets']

    def topicFocusDefinitionList(self, topics_id, focal_set_definitions_id):
        params = {}
        params['focal_set_definitions_id'] = focal_set_definitions_id
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/focus_definitions/list',
            params)['focus_definitions']

    def topicFocusDefinitionCreate(self, topics_id, **kwargs):
        params = {}
        valid_params = ['name', 'description', 'query', 'focal_set_definitions_id']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/focus_definitions/create',
            params, http_method='POST')['focus_definitions']

    def topicFocusDefinitionUpdate(self, topics_id, focus_definitions_id, **kwargs):
        params = {}
        valid_params = ['name', 'description', 'query']
        _validate_params(params, valid_params, kwargs)
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/focus_definitions/'+
            str(focus_definitions_id)+'/update', params, http_method='PUT')['focus_definitions']

    def topicFocusDefinitionDelete(self, topics_id, focus_definitions_id):
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/focus_definitions/'+
            str(focus_definitions_id)+'/delete', http_method='PUT')

    def topicFociList(self, topics_id, focal_sets_id):
        params = {'focal_sets_id': focal_sets_id}
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/foci/list', params)['foci']

    def userPermissionsList(self):
        return self._queryForJson(self.V2_API_URL+'topics/permissions/user/list')

    def topicPermissionsList(self, topics_id):
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/permissions/list')

    def topicPermissionsUpdate(self, topics_id, email, permission):
        _validate_permission_param(permission)
        params = {
            'email': email,
            'permission': permission
        }
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/permissions/update', params, 'PUT_JSON')

    '''
    # not implemented yet
    def topicAddTimespan(self, topics_id, **kwargs):
        params = {}
        valid_params = ['start_date', 'end_date']
        _validate_params(params, valid_params, kwargs)
        _validate_date_params(params, valid_params)
        return self._queryForJson(self.V2_API_URL+'topics/'+str(topics_id)+'/timespans/add_dates', params, 'POST')
    '''


class AdminMediaCloud(MediaCloud):
    '''
    A MediaCloud API client that includes admin-only methods, including to writing back
    data to MediaCloud.
    '''

    def story(self, stories_id, raw_1st_download=False, corenlp=False, sentences=False, text=False):
        '''
        Full details about one story.  Handy shortcut to storyList if you want sentences broken out
        '''
        return self._queryForJson(self.V2_API_URL+'stories/single/'+str(stories_id),
                {'raw_1st_download': 1 if raw_1st_download else 0,
                 'corenlp': 1 if corenlp else 0,
                 'sentences': 1 if sentences else 0,
                 'text': 1 if text else 0
                })[0]

    def storyList(self, solr_query='', solr_filter='', last_processed_stories_id=0, rows=20,
                  wc=False, feeds_id=None, sort=MediaCloud.SORT_PROCESSED_STORIES_ID, raw_1st_download=False,
                  corenlp=False, sentences=False, text=False, ap_stories_id=0, show_feeds=False):
        '''
        Search for stories and page through results
        '''
        return self._queryForJson(self.V2_API_URL+'stories/list',
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
                })

    def sentenceList(self, solr_query, solr_filter='', start=0, rows=1000, sort=MediaCloud.SORT_PUBLISH_DATE_ASC):
        '''
        Search for sentences and page through results
        '''
        return self._queryForJson(self.V2_API_URL+'sentences/list',
                {'q': solr_query,
                 'fq': solr_filter,
                 'start': start,
                 'rows': rows,
                 'sort': sort
                })

    def tagStories(self, tags=None, clear_others=False):
        '''
        Add some tags to stories. The tags parameter should be a list of StoryTag objects.
        '''
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

    def tagSentences(self, tags=None, clear_others=False):
        '''
        Add some tags to sentences. The tags parameter should be a list of SentenceTag objects
        '''
        params = {}
        if clear_others is True:
            params['clear_tag_sets'] = 1
        # bath into smaller requests so we don't hit the 414 Request-URI Too Large error
        if tags is None:
            tags = {}
        results = []
        for tag_chunk in _chunkify(tags, 50):
            custom_tags = []
            for tag in tag_chunk:
                if tag.__class__ is not SentenceTag:
                    raise ValueError('To use tagSentences you must send in a list of SentenceTag objects')
                custom_tags.append(tag.getParams())
            results.append(self._queryForJson(self.V2_API_URL+'sentences/put_tags', params, 'PUT_JSON', custom_tags))
        return results

    def tagMedia(self, tags=None, clear_others=False):
        '''
        Add some tags to media (ie. put them in a colleciton or add metadata to them).
        The tags parameter should be a list of MediaTag objects.
        '''
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

    def createTag(self, tag_sets_id, name, label, description, is_static=False, show_on_media=False, show_on_stories=False):
        params = {
            'tag_sets_id': tag_sets_id,
            'tag': name,
            'label': label,
            'description': description,
            'is_static': 1 if is_static else 0,
            'show_on_media': 1 if show_on_media else 0,
            'show_on_stories': 1 if show_on_stories else 0
        }
        return self._queryForJson(self.V2_API_URL+'tags/create', params, 'POST')

    def updateTag(self, tags_id, name=None, label=None, description=None, is_static=False, show_on_media=False, show_on_stories=False):
        params = { 'tags_id': tags_id }
        if name is not None:
            params['tag'] = name
        if label is not None:
            params['label'] = label
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
        return self._queryForJson(self.V2_API_URL+'tag_sets/create', params, 'POST')

    def updateTagSet(self, tag_sets_id, name=None, label=None, description=None, show_on_media=False, show_on_stories=False):
        params = { 'tag_sets_id': tag_sets_id }
        if name is not None:
            params['name'] = name
        if label is not None:
            params['label'] = label
        if description is not None:
            params['description'] = description
        return self._queryForJson(self.V2_API_URL+'tag_sets/update/', {}, 'PUT_JSON', params)

    def feedCreate(self, media_id, name, url, feed_type='syndicated', feed_status='active'):
        _validate_feed_type(feed_type)
        _validate_feed_status(feed_status)
        params = {
            'media_id': media_id,
            'name': name,
            'url': url,
            'feed_type': feed_type,
            'feed_status': feed_status
        }
        return self._queryForJson(self.V2_API_URL+'feeds/create', params, 'POST')

    def feedUpdate(self, feeds_id, name=None, url=None, feed_type='syndicated', feed_status='active'):
        _validate_feed_type(feed_type)
        _validate_feed_status(feed_status)
        params = { 'feeds_id': feeds_id}
        if name is not None:
            params['name'] = name
        if url is not None:
            params['url'] = url
        if feed_type is not None:
            params['feed_type'] = feed_type
        if feed_status is not None:
            params['feed_status'] = feed_status
        return self._queryForJson(self.V2_API_URL+'feeds/update', params, 'PUT_JSON')

    def feedsScrape(self, media_id):
        return self._queryForJson((self.V2_API_URL+'feeds/scrape/%d') % media_id, params, 'POST')

    def mediaCreate(self, media_items):
        # validate and clean input
        valid_params = ['url', 'name', 'foreign_rss_links', 'content_delay', 'feeds', 'tags_ids', 'editor_notes', 'public_notes', 'is_monitored' ]
        boolean_params = ['foreign_rss_links', 'is_monitored']
        for media in media_items:
            for k in media:
                if k not in valid_params:
                    raise ValueError('Invalid param in attempt to create media: '+str(k))
                if k in boolean_params:
                    media[k] = 1 if k else 0
            if media['url'] is None or len(media['url']) == 0:
                raise ValueError('You must supply a media url')
        return self._queryForJson(self.V2_API_URL+'media/create', media_items, 'POST')

    def mediaUpdate(self, media_id, url=None, name=None, foreign_rss_links=None, content_delay=None, editor_notes=None, public_notes=None, is_monitored=None):
        params = { 'media_id': media_id }
        if name is not None:
            params['name'] = name
        if url is not None:
            params['url'] = url
        if foreign_rss_links is not None:
            params['foreign_rss_links'] = 1 if foreign_rss_links else 0
        if content_delay is not None:
            params['content_delay'] = content_delay
        if editor_notes is not None:
            params['editor_notes'] = editor_notes
        if public_notes is not None:
            params['public_notes'] = public_notes
        if is_monitored is not None:
            params['is_monitored'] = 1 if is_monitored else 0
        return self._queryForJson(self.V2_API_URL+'media/update', params, 'PUT_JSON')

    def mediaSuggestionsList(self, all=False):
        return self._queryForJson(self.V2_API_URL+'media/list', {'all': all})

    def mediaSuggestionsMark(self, media_suggestions_id, status, mark_reason):
        if status not in ['approved', 'rejected']:
            raise ValueError('Invalid media suggestion status: '+str(status))
        params = {
            'media_suggestions_id': media_suggestions_id,
            'status': status,
            'mark_reason': mark_reason
        }
        return self._queryForJson(self.V2_API_URL+'media/suggestions/mark', params, 'PUT_JSON')

def _solr_date_range(start_date, end_date, start_date_inclusive=True, end_date_inclusive=False):
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
    '''
    Helper method to break an array into a set of smaller arrays
    '''
    return [data[x:x+chunk_size] for x in xrange(0, len(data), chunk_size)]

def _validate_params(params, valid_params, args):
    for key, value in args.iteritems():
        if key not in valid_params:
            raise ValueError('%s is not a valid argument for this api method' % key)
        params[key] = value
    return params

def _validate_sort_param(order):
    if order not in [None, 'social', 'inlink']:
        raise ValueError('Sort must be either social or inlink')

def _validate_permission_param(permission):
    if permission not in ['none', 'read', 'write', 'admin']:
        raise ValueError('Permission must be none, read, write or admin')

def _validate_bool_params(params, *args):
    for arg in args:
        if arg in params:
            if params[arg] not in [True, False]:
                raise ValueError('%s must be a python boolean (True or False)' % arg)
            params[arg] = 1 if params[arg] is True else 0
    return params

def _validate_date_params(params, *args):
    for arg in args:
        if arg in params:
            datetime.datetime.strptime(params[arg], '%Y-%m-%d')    #will throw a ValueError if invalid
    return params

def _validate_feed_type(feed_type):
    if feed_type not in ['syndicated', 'web_page']:
            raise ValueError('feed_type must be syndicated or web_page')

def _validate_feed_status(feed_type):
    if feed_status not in ['active', 'inactive', 'skipped']:
        raise ValueError('feed_status must be active, inactive, or skipped')
