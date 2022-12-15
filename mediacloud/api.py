import logging
import datetime as dt
from typing import Dict, Optional, Union
import requests
import mediacloud
import mediacloud.error


logger = logging.getLogger(__name__)


class BaseApi:

    # Default applied to all queries made to main server. You can alter this on
    # your instance if you want to bail out more quickly, or know you have longer
    # running queries
    TIMEOUT_SECS = 30

    BASE_API_URL = "https://search.mediacloud.org/api/"

    def __init__(self, auth_token=str):
        if not auth_token:
            raise mediacloud.error.MCException("No api key set - nothing will work without this")
        # Specify the auth_token to use for all future requests
        self._auth_token = auth_token
        # better performance to put all HTTP through this one object
        self._session = requests.Session()
        self._session.headers.update({'Authorization': f'Token {self._auth_token}'})

    def user_profile(self) -> Dict:
        # :return: basic info about the current user, including their roles
        return self._query('auth/profile')

    def _query(self, endpoint: str, params: Dict = None, method: str = 'GET'):
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
                        limit: Optional[int] = 0, offset: Optional[int] = 0):
        params = dict(limit=limit, offset=offset)
        if name:
            params['name'] = name
        if platform:
            params['platform'] = platform
        return self._query('sources/collections/', params)

    def source_list(self, platform: Optional[str] = None, name: Optional[str] = None,
                    collection_id: Optional[int] = None,
                    limit: Optional[int] = 0, offset: Optional[int] = 0):
        params = dict(limit=limit, offset=offset)
        if collection_id:
            params['collection_id'] = collection_id
        if name:
            params['name'] = name
        if platform:
            params['platform'] = platform
        return self._query('sources/sources/', params)

    def feed_list(self, source_id: Optional[int] = None, modified_since: Optional[Union[dt.datetime, int]] = None,
                  limit: Optional[int] = 0, offset: Optional[int] = 0):
        params = dict(limit=limit, offset=offset)
        if source_id:
            params['source_id'] = source_id
        if modified_since:  # need to send server an epoch timestamp
            params['modified_since'] = int(modified_since.timestamp()) if isinstance(modified_since, dt.datetime)\
                else modified_since
        return self._query('sources/feeds/', params)
