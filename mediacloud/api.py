import datetime as dt
import logging
from typing import Any, Dict, List, Optional, Union

import requests

import mediacloud
import mediacloud.error

logger = logging.getLogger(__name__)


class BaseApi:

    # Default applied to all queries made to main server. You can alter this on
    # your instance if you want to bail out more quickly, or know you have longer
    # running queries
    TIMEOUT_SECS = 60

    BASE_API_URL = "https://search.mediacloud.org/api/"

    def __init__(self, auth_token: Optional[str] = None):
        if not auth_token:
            raise mediacloud.error.MCException("No api key set - nothing will work without this")
        # Specify the auth_token to use for all future requests
        self._auth_token = auth_token
        # better performance to put all HTTP through this one object
        self._session = requests.Session()
        self._session.headers.update({'Authorization': f'Token {self._auth_token}'})
        self._session.headers.update({'Accept': 'application/json'})

    def user_profile(self) -> Dict:
        # :return: basic info about the current user, including their roles
        return self._query('auth/profile')

    def version(self) -> Dict:
        """
        returns dict with (at least):
        GIT_REV, now (float epoch time), version
        """
        return self._query('version')

    def _query(self, endpoint: str, params: Optional[Dict] = None, method: str = 'GET') -> Dict:
        """
        Centralize making the actual queries here for easy maintenance and testing of HTTP comms
        """
        endpoint_url = self.BASE_API_URL + endpoint
        if method == 'GET':
            r = self._session.get(endpoint_url, params=params, timeout=self.TIMEOUT_SECS)
        elif method == 'POST':
            r = self._session.post(endpoint_url, json=params, timeout=self.TIMEOUT_SECS)
        else:
            raise RuntimeError(f"Unsupported method of '{method}'")
        if r.status_code != 200:
            raise RuntimeError(f"API Server Error {r.status_code}. Params: {params}")
        return r.json()


class DirectoryApi(BaseApi):

    PLATFORM_ONLINE_NEWS = "online_news"
    PLATFORM_YOUTUBE = "youtube"
    PLATFORM_TWITTER = "twitter"
    PLATFORM_REDDIT = "reddit"

    def collection_list(self, platform: Optional[str] = None, name: Optional[str] = None,
                        limit: Optional[int] = 0, offset: Optional[int] = 0) -> Dict:
        params: Dict[Any, Any] = dict(limit=limit, offset=offset)
        if name:
            params['name'] = name
        if platform:
            params['platform'] = platform
        return self._query('sources/collections/', params)

    def source_list(self, platform: Optional[str] = None, name: Optional[str] = None,
                    collection_id: Optional[int] = None,
                    limit: Optional[int] = 0, offset: Optional[int] = 0) -> Dict:
        params: Dict[Any, Any] = dict(limit=limit, offset=offset)
        if collection_id:
            params['collection_id'] = collection_id
        if name:
            params['name'] = name
        if platform:
            params['platform'] = platform
        return self._query('sources/sources/', params)

    def feed_list(self, source_id: Optional[int] = None,
                  modified_since: Optional[Union[dt.datetime, int, float]] = None,
                  modified_before: Optional[Union[dt.datetime, int, float]] = None,
                  limit: Optional[int] = 0, offset: Optional[int] = 0) -> Dict:
        params: Dict[Any, Any] = dict(limit=limit, offset=offset)
        if source_id:
            params['source_id'] = source_id

        def epoch_param(t, param):
            if t is None:
                return        # parameter not set
            if isinstance(t, dt.datetime):
                params[param] = t.timestamp()  # get epoch time
            elif isinstance(t, (int, float)):
                params[param] = t
            else:
                raise ValueError(param)

        epoch_param(modified_since, 'modified_since')
        epoch_param(modified_before, 'modified_before')

        return self._query('sources/feeds/', params)


class SearchApi(BaseApi):
    PROVIDER = "onlinenews-mediacloud"

    def _prep_default_params(self, query: str, start_date: dt.date, end_date: dt.date,
                             collection_ids: Optional[List[int]] = [], source_ids: Optional[List[int]] = [],
                             platform: Optional[str] = None):
        params: Dict[Any, Any] = dict(start=start_date.isoformat(), end=end_date.isoformat(), q=query,
                                      platform=self.PROVIDER)
        if len(source_ids):
            params['ss'] = ",".join([str(sid) for sid in source_ids]),
        if len(collection_ids):
            params['cs'] = ",".join([str(cid) for cid in collection_ids]),
        return params

    def story_count(self, query: str, start_date: dt.date, end_date: dt.date, collection_ids: Optional[List[int]] = [],
                    source_ids: Optional[List[int]] = [], platform: Optional[str] = None) -> Dict:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        results = self._query('search/total-count', params)
        return results['count']

    def story_count_over_time(self, query: str, start_date: dt.date, end_date: dt.date,
                              collection_ids: Optional[List[int]] = [], source_ids: Optional[List[int]] = [],
                              platform: Optional[str] = None) -> List[Dict]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        results = self._query('search/count-over-time', params)
        for d in results['count_over_time']['counts']:
            d['date'] = dt.date.fromisoformat(d['date'][:10])
        return results['count_over_time']['counts']

    def story_list(self, query: str, start_date: dt.date, end_date: dt.date, collection_ids: Optional[List[int]] = [],
                   source_ids: Optional[List[int]] = [], platform: Optional[str] = None,
                   expanded: Optional[bool] = None, pagination_token: Optional[str] = None,
                   sort_field: Optional[str] = None, sort_order: Optional[str] = None,
                   page_size: Optional[int] = None) -> tuple[Dict, Optional[str]]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        if expanded:
            params['expanded'] = 1
        if pagination_token:
            params['pagination_token'] = pagination_token
        if sort_field:
            params['sort_field'] = sort_field
        if sort_order:
            params['sort_order'] = sort_order
        if page_size:
            params['page_size'] = page_size
        results = self._query('search/story-list', params)
        for s in results['stories']:
            s['publish_date'] = dt.date.fromisoformat(s['publish_date'][:10]) if s['publish_date'] else None
            s['indexed_date'] = dt.date.fromisoformat(s['indexed_date'][:10]) if s['indexed_date'] else None
        return results['stories'], results['pagination_token']

    def story(self, story_id: str) -> Dict:
        params = dict(storyId=story_id, platform=self.PROVIDER)
        results = self._query('search/story', params)
        return results['story']

    def words(self, query: str, start_date: dt.date, end_date: dt.date, collection_ids: Optional[List[int]] = [],
              source_ids: Optional[List[int]] = [], platform: Optional[str] = None,
              limit: Optional[int] = None) -> List[Dict]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        if limit:
            params['limit'] = limit
        results = self._query('search/words', params)
        return results['words']

    def sources(self, query: str, start_date: dt.date, end_date: dt.date, collection_ids: Optional[List[int]] = [],
                source_ids: Optional[List[int]] = [], platform: Optional[str] = None,
                limit: Optional[int] = None) -> List[Dict]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        if limit:
            params['limit'] = limit
        results = self._query('search/sources', params)
        return results['sources']

    def languages(self, query: str, start_date: dt.date, end_date: dt.date, collection_ids: Optional[List[int]] = [],
                  source_ids: Optional[List[int]] = [], platform: Optional[str] = None,
                  limit: Optional[int] = None) -> List[Dict]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        if limit:
            params['limit'] = limit
        results = self._query('search/languages', params)
        return results['languages']
