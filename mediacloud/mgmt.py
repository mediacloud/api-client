"""
Directory Management API

Nod to Monty Python
It's not Camelot, only a model...

update/patch methods not yet tested!!!
"""

from mediacloud.api import BaseApi


class DirectoryManagementApi(BaseApi):

    ################ CollectionsViewSet

    def collection_create(self, params: dict) -> dict:
        # XXX take discrete args, create dict?
        # XXX require name!
        # possible others: notes
        # bools: public, featured, managed, monitored
        return self._query(f'sources/collections/', params, "POST")

    def collection_update(self, collection_id: int, params: dict) -> dict:
        # XXX take discrete args, create dict?
        return self._query(f'sources/collections/{collection_id}/', params, "PATCH")

    # for testing/cleanup:
    def _collection_delete(self, collection_id: int) -> dict:
        return self._query(f'sources/collections/{collection_id}/', None, "DELETE")

    ################ SourcesViewSet

    def source_create(self, params: dict) -> dict:
        # XXX take discrete args, create dict?
        # XXX require name, label, homepage?
        # back end defaults: platform
        # optional: url_search_string, notes, media_type, pub_{state,country}, primary_language
        return self._query('sources/sources/', params, "POST")

    def source_update(self, source_id: int, params: dict) -> dict:
        # XXX take discrete args, create dict?
        return self._query(f'sources/sources/{source_id}/', params, "PATCH")

    # for testing/cleanup:
    def source_delete(self, source_id: int) -> dict:
        return self._query(f'sources/sources/{source_id}/', None, "DELETE")

    ################ SourcesCollectionsViewSet

    def source_collection_list(self, source_id: int) -> dict:
        # XXX belongs in DirectoryApi??
        # XXX take either source_id or collection_id!!!
        return self._query(f'sources/sources-collections/{source_id}/', None, "GET")

    # mcweb sourcesCollectionsApi.js calls this createSourceCollectionAssociation
    def source_collection_create(self, source_id: int, collection_id: int) -> dict:
        params = { 'source_id': source_id, 'collection_id': collection_id }
        return self._query('sources/sources-collections/', params, "POST")

    # mcweb sourcesCollectionsApi.js calls this deleteSourceCollectionAssociation
    def source_collection_delete(self, source_id: int, collection_id: int) -> dict:
        return self._query(f'sources/sources-collections/{source_id}/?collection_id={collection_id}', "DELETE")
