import datetime as dt
import importlib.metadata
import logging
import warnings
from typing import Any, Dict, List, Optional, Union

from requests import Session
from requests_ratelimiter import LimiterSession

import mediacloud
import mediacloud.error
from mediacloud.types import (Collection, CountOverTimePoint, JSONObj,
                              LanguageCount, OffsetPage, PaginationToken,
                              Source, SourceCount, SourceIntervalAttention,
                              SourceWeekAttention, Story, StoryCount,
                              VersionInfo)

logger = logging.getLogger(__name__)

# Identify the version of this package that's running
try:
    VERSION = "v" + importlib.metadata.version('mediacloud')
except importlib.metadata.PackageNotFoundError:
    VERSION = "dev"


class BaseApi:

    # Default applied to all queries made to main server. You can alter this on
    # your instance if you want to bail out more quickly, or know you have longer
    # running queries
    TIMEOUT_SECS = 60

    # Default rate limit for API requests. Admins with higher rate limits can
    # override this on their subclass or instance before creating the session.
    # This is only an upper bound on the value returned by the api_params method.
    RATE_LIMIT_PER_MINUTE = 10

    # tests honor MC_API_BASE_URL environment variable
    BASE_API_URL = "https://search.mediacloud.org/api/"

    USER_AGENT_STRING = f"mediacloud {VERSION}"

    def __init__(self, auth_token: Optional[str] = None):
        if not auth_token:
            raise mediacloud.error.MCException("No api key set - nothing will work without this")
        self._headers = {
            'Authorization': f'Token {auth_token}',
            'Accept': 'application/json',
            "User-Agent": self.USER_AGENT_STRING,
        }
        # better performance to put all HTTP through this one object;
        self._session: Session | None = None  # made on demand

        # saved rate limit used to create _session,
        self._per_minute = -1                # initially not valid

    def _make_session(self) -> None:
        """
        make session object on demand, to allow user manipulation of
        BASE_API_URL and RATE_LIMIT_PER_MINUTE after instantiation but
        before first call.  COULD check for changes BASE_API_URL and
        RATE_LIMIT_PER_MINUTE after the fact (by saving the values
        used to create the current session, but that seems a bit much)
        """
        # make temporary Session object for api_params call
        self._session = Session()
        self._session.headers.update(self._headers)

        try:
            raw = self.api_params()
            per_minute = self._parse_rate_limit(raw)
        except:
            per_minute = 2      # old default

        self._session.close()
        self._session = LimiterSession(per_minute=per_minute)
        self._session.headers.update(self._headers)
        self._per_minute = per_minute

    def _parse_rate_limit(self, raw: JSONObj) -> int:
        # :return: rate limit in requests per minute
        # tries not to crash, and to handle bad data gracefully
        pp = raw.get('params', {})
        if VERSION[0] == 'v' and (apc := pp.get('api-python-client')):
            try:
                apci = [int(x) for x in apc.split('.')]
                vers = [int(x) for x in VERSION[1:].split('.')]
                # maybe only compare first two parts (ignore fixes)??
                if apci > vers:
                    warnings.warn(
                        f"New mediacloud.api library version available: {apc}")
            except ValueError:
                pass

        # only support per minute: per hour rates would allow LARGE bursts
        # django-ratelimit allows 10/5m, but django-smart-ratelimit may not??
        per_minute = self.RATE_LIMIT_PER_MINUTE
        if (qr := pp.get('query-rate')) and isinstance(qr, str):
            sr = qr.split('/')  # split rate
            if len(sr) == 2 and sr[0].isdigit() and sr[1] == 'm':
                # use RATE_LIMIT_PER_MINUTE as upper bound
                per_minute = min(int(sr[0]), per_minute)
        return per_minute

    def user_profile(self) -> JSONObj:
        # :return: basic info about the current user, including their roles
        return self._query('auth/profile')

    def version(self) -> VersionInfo:
        """
        returns dict with (at least):
        GIT_REV, now (float epoch time), version
        """
        return self._query('version')

    def _query(self, endpoint: str, params: Optional[Dict] = None, method: str = 'GET') -> JSONObj:
        """
        Centralize making the actual queries here for easy maintenance and testing of HTTP comms
        """
        if not self._session:
            self._make_session()  # create on first call
            assert self._session  # to quiet mypy

        endpoint_url = self.BASE_API_URL + endpoint
        if method == 'GET':
            r = self._session.get(endpoint_url, params=params, timeout=self.TIMEOUT_SECS)
        elif method == 'POST':
            r = self._session.post(endpoint_url, json=params, timeout=self.TIMEOUT_SECS)
        elif method == "DELETE":
            r = self._session.delete(endpoint_url, params=params, timeout=self.TIMEOUT_SECS)
        elif method == "PATCH":
            r = self._session.patch(endpoint_url, json=params, timeout=self.TIMEOUT_SECS)
        else:
            raise RuntimeError(f"Unsupported method of '{method}'")

        status_class = r.status_code // 100
        if r.text:
            try:
                j = r.json()
            except:
                # here with non/bad json response
                j = {
                    "status": "bad-response",
                    "note": f"bad JSON: {r.text}" # for APIResponseError
                }
                status_class = 99
        else:
            # Here with 429 error from older servers
            j = {
                "status": "empty",
                "note": "empty-response" # for APIResponseError
            }
            status_class = 99

        if status_class != 2:  # create operations return 201
            raise mediacloud.error.APIResponseError(r, params, j)

        return j

    def api_params(self) -> JSONObj:
        # :return: api parameters from server
        return self._query('search/api-params')


class DirectoryApi(BaseApi):

    PLATFORM_ONLINE_NEWS = "online_news"
    PLATFORM_YOUTUBE = "youtube"
    PLATFORM_TWITTER = "twitter"
    PLATFORM_REDDIT = "reddit"

    def collection(self, collection_id: int) -> Collection:

        return self._query(f'sources/collections/{collection_id}/', None)

    def collection_list(self, platform: Optional[str] = None, name: Optional[str] = None,
                        limit: Optional[int] = 0, offset: Optional[int] = 0, source_id: Optional[int] = None) -> OffsetPage:
        params: Dict[Any, Any] = dict(limit=limit, offset=offset)
        if name:
            params['name'] = name
        if platform:
            params['platform'] = platform
        if source_id:
            params['source_id'] = source_id
        return self._query('sources/collections/', params)

    def source(self, source_id: int) -> Source:
        return self._query(f'sources/sources/{source_id}/', None)

    def source_list(self, platform: Optional[str] = None, name: Optional[str] = None,
                    collection_id: Optional[int] = None,
                    limit: Optional[int] = 0, offset: Optional[int] = 0) -> OffsetPage:
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
                  limit: Optional[int] = 0, offset: Optional[int] = 0, return_details: bool = False) -> JSONObj:
        params: Dict[str, Any] = dict(limit=limit, offset=offset)
        if source_id:
            params['source_id'] = source_id

        def epoch_param(t: Union[dt.datetime, int, float], param: str) -> None:
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

        if return_details:
            return {'results': self._query('sources/feeds/details/', params)['feeds']}

        return self._query('sources/feeds/', params)


class SearchApi(BaseApi):
    PROVIDER = "onlinenews-mediacloud"

    def _prep_default_params(self, query: str, start_date: dt.date, end_date: dt.date,
                             collection_ids: Optional[List[int]] = [], source_ids: Optional[List[int]] = [],
                             platform: Optional[str] = None) -> Dict[str, Any]:

        if isinstance(start_date, dt.datetime):
            start_date = start_date.date()
            warnings.warn("start_date was passed as datetime, but expected as date, and has been recast")

        if isinstance(end_date, dt.datetime):
            end_date = end_date.date()
            warnings.warn("end_date was passed as datetime, but expected as date, and has been recast")

        params: Dict[str, Any] = dict(start=start_date.isoformat(), end=end_date.isoformat(), q=query,
                                      platform=(platform or self.PROVIDER))

        if (len(source_ids) + len(collection_ids)) == 0:
            warnings.warn("No sources or collections specified. This is a *BAD IDEA*. Pick a collection.")

        if len(source_ids):
            params['ss'] = ",".join([str(sid) for sid in source_ids]),
        if len(collection_ids):
            params['cs'] = ",".join([str(cid) for cid in collection_ids]),
        return params

    def story_count(self, query: str, start_date: dt.date, end_date: dt.date, collection_ids: Optional[List[int]] = [],
                    source_ids: Optional[List[int]] = [], platform: Optional[str] = None) -> StoryCount:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        results = self._query('search/total-count', params)
        return results['count']

    def story_count_over_time(self, query: str, start_date: dt.date, end_date: dt.date,
                              collection_ids: Optional[List[int]] = [], source_ids: Optional[List[int]] = [],
                              platform: Optional[str] = None) -> List[CountOverTimePoint]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        results = self._query('search/count-over-time', params)
        for d in results['count_over_time']['counts']:
            d['date'] = dt.date.fromisoformat(d['date'][:10])
        return results['count_over_time']['counts']

    def stories_by_source_week(self, query: str, start_date: dt.date, end_date: dt.date,
                               collection_ids: Optional[List[int]] = [], source_ids: Optional[List[int]] = [],
                               platform: Optional[str] = None) -> List[SourceWeekAttention]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        results = self._query('search/count-by-source-week', params)
        return results['source-week-attention']

    def stories_by_source_over_interval(self, query: str, start_date: dt.date, end_date: dt.date,
                                        collection_ids: Optional[List[int]] = [], source_ids: Optional[List[int]] = [],
                                        platform: Optional[str] = None, interval: Optional[str] = None) -> List[SourceIntervalAttention]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        if interval:
            params['interval'] = interval
        results = self._query('search/count-by-source-over-interval', params)
        return results['source-interval-attention']

    def story_list(self, query: str, start_date: dt.date, end_date: dt.date, collection_ids: Optional[List[int]] = [],
                   source_ids: Optional[List[int]] = [], platform: Optional[str] = None,
                   expanded: bool = False, pagination_token: Optional[str] = None,
                   sort_order: Optional[str] = None, page_size: Optional[int] = None,
                   randomized: bool = False) -> tuple[List[Story], PaginationToken]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        if expanded:
            params['expanded'] = 1
        if randomized:
            params['randomize'] = 1
        if pagination_token:
            params['pagination_token'] = pagination_token
        if sort_order:
            params['sort_order'] = sort_order
        if page_size:
            params['page_size'] = page_size
        results = self._query('search/story-list', params)
        self._dates_str2objects(results['stories'])
        return results['stories'], results['pagination_token']

    def _dates_str2objects(self, stories: List[Story]) -> None:
        # _in place_ translation from ES date str to python data/datetime objects to save memory
        for s in stories:
            s['publish_date'] = dt.date.fromisoformat(s['publish_date'][:10]) if s['publish_date'] else None
            s['indexed_date'] = dt.datetime.fromisoformat(s['indexed_date']) if s['indexed_date'] else None

    def story_sample(self, query: str, start_date: dt.date, end_date: dt.date, collection_ids: Optional[List[int]] = [],
                     source_ids: Optional[List[int]] = [], platform: Optional[str] = None,
                     limit: Optional[int] = None, expanded: bool = False) -> List[Story]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        if limit:
            params['limit'] = limit
        fields = ['indexed_date', 'publish_date', 'id', 'language', 'media_name', 'media_url', 'title', 'url']
        if expanded:  # STILL UNSUPPORTED: admins can query full text if they choose to
            fields.append('text')
        params['fields'] = fields  # gets passed down to ES in MC client
        results = self._query('search/sample', params)
        self._dates_str2objects(results['sample'])
        return results['sample']

    def story(self, story_id: str) -> Story:
        params = dict(storyId=story_id, platform=self.PROVIDER)
        results = self._query('search/story', params)
        return results['story']

    def words(self, query: str, start_date: dt.date, end_date: dt.date, collection_ids: Optional[List[int]] = [],
              source_ids: Optional[List[int]] = [], platform: Optional[str] = None,
              limit: Optional[int] = None) -> List[JSONObj]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        if limit:
            params['limit'] = limit
        results = self._query('search/words', params)
        return results['words']

    def sources(self, query: str, start_date: dt.date, end_date: dt.date, collection_ids: Optional[List[int]] = [],
                source_ids: Optional[List[int]] = [], platform: Optional[str] = None,
                limit: Optional[int] = None) -> List[SourceCount]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        if limit:
            params['limit'] = limit
        results = self._query('search/sources', params)
        return results['sources']

    def languages(self, query: str, start_date: dt.date, end_date: dt.date, collection_ids: Optional[List[int]] = [],
                  source_ids: Optional[List[int]] = [], platform: Optional[str] = None,
                  limit: Optional[int] = None) -> List[LanguageCount]:
        params = self._prep_default_params(query, start_date, end_date, collection_ids, source_ids, platform)
        if limit:
            params['limit'] = limit
        results = self._query('search/languages', params)
        return results['languages']
