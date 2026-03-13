"""
Directory Management API

Nod to Monty Python
It's not Camelot, only a model...

update/patch methods not yet tested!!!

ALL arguments are keyword only, for safety!
"""
from typing import TypeAlias

from mediacloud.api import BaseApi

_EMPTY = object()

_Params: TypeAlias = dict


class DirectoryManagementApi(BaseApi):  # XXX maybe extend DirectoryApi???
    """
    Class for Directory Management
    """

    def _params(self, what: str, kws: dict, params: list[str]) -> _Params:
        """
        helper for _{collection,source}_params helpers
        """
        ret: _Params = {}
        kwcopy = kws.copy()
        for p in params:
            v = kwcopy.pop(p, _EMPTY)
            if v is not _EMPTY:
                ret[p] = v
        if kwcopy:
            extra = ",".join(kwcopy.keys())
            raise ValueError(f"Unknown {what} params {extra}")
        return ret

    ################ CollectionsViewSet

    def _collection_params(self, kws: dict) -> _Params:
        """
        helper for collection_{create,update}
        """
        return self._params("collection", kws,
                            ['name', 'note', 'public', 'featured', 'managed', 'monitored'])

    def collection_create(self, **kwargs) -> dict:
        params = self._collection_params(kwargs)
        if 'name' not in params or not params['name']:
            raise ValueError("collection_create must have 'name'")
        return self._query('sources/collections/', params, "POST")

    def collection_update(self, *, collection_id: int, **kwargs) -> dict:
        params = self._collection_params(**kwargs)
        if not params:
            raise ValueError("no parameters for collection_update?")
        return self._query(f'sources/collections/{collection_id}/', params, "PATCH")

    # for testing/cleanup:
    def collection_delete(self, collection_id: int) -> dict:
        return self._query(f'sources/collections/{collection_id}/', None, "DELETE")

    ################ SourcesViewSet

    def _source_params(self, kws: dict) -> _Params:
        """
        helper for source_{create,update}
        """
        return self._params("source", kws,
                            ['name', 'label', 'homepage', 'platform',
                             'url_search_string', 'notes', 'media_type',
                             'pub_state', 'pub_country', 'primary_language'])

    def source_create(self, **kwargs) -> dict:
        params = self._source_params(kwargs)
        for p in ['name', 'homepage']:
            if p not in params:
                raise ValueError(f"source_create requires '{p}'")
        return self._query('sources/sources/', params, "POST")

    def source_update(self, *, source_id: int, **kwargs) -> dict:
        params = self._source_params(kwargs)
        if not params:
            raise ValueError("no parameters for source_update?")
        return self._query(f'sources/sources/{source_id}/', params, "PATCH")

    # for testing/cleanup:
    def source_delete(self, source_id: int) -> dict:
        return self._query(f'sources/sources/{source_id}/', None, "DELETE")

    ################ SourcesCollectionsViewSet

    def source_collection_list(self, *,
                               source_id: int | None = None,
                               collection_id: int | None = None) -> dict:
        if source_id and collection_id:
            raise ValueError("source_collection_list got both source_id and collection_id")
        if source_id:
            endpoint = f'sources/sources-collections/{source_id}/'
        else:
            endpoint = f'sources/sources-collections/{collection_id}/?collection=1'  # XXX untested
        return self._query(endpoint, None, "GET")

    # mcweb sourcesCollectionsApi.js calls this createSourceCollectionAssociation
    def source_collection_create(self, *, source_id: int, collection_id: int) -> dict:
        params = {'source_id': source_id, 'collection_id': collection_id}
        return self._query('sources/sources-collections/', params, "POST")

    # mcweb sourcesCollectionsApi.js calls this deleteSourceCollectionAssociation
    # XXX endpoint seems to take collection=bool query parameter??
    # (if not set to true, expects collection_id parameter??)
    def source_collection_delete(self, *, source_id: int, collection_id: int) -> dict:
        return self._query(f'sources/sources-collections/{source_id}/?collection_id={collection_id}', "DELETE")
