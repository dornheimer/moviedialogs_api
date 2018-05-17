import json
from sqlalchemy import case
from elasticsearch.helpers import bulk


class ESClient:
    def __init__(self, client, settings):
        self.client = client
        self.settings = self._load_settings(settings)

    def _load_settings(self, settings_json):
        with open(settings_json) as f:
            return json.load(f)

    def create_index(self, model):
        self.client.indices.create(index=model.__tablename__, body=self.settings)

    def query_index(self, index, query, page, per_page):
        if self.client is None:
            return [], 0
        body = {
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['*']
                }
            },
            'from': (page - 1) * per_page,
            'size': per_page
        }
        search = self.client.search(
            index=index,
            doc_type=index,
            body=body
        )
        print(search)
        ids = [hit['_id'] for hit in search['hits']['hits']]
        return ids, search['hits']['total']

    def search(self, model, query, page, per_page):
        ids, total = self.query_index(model.__tablename__, query, page, per_page)
        if total == 0:
            return ids, total
        # Get objects from returned ids and enforce the same order as the ES query
        whens = {id: i for i, id in enumerate(ids)}
        return model.query.filter(model.id.in_(ids)).order_by(case(whens, value=model.id)), total

    def bulk_add_to_index(self, model):
        if self.client is None:
            return
        index = model.__tablename__
        docs_gen = (
            {
                '_index': index,
                '_type' : index,
                '_id'   : obj.id,
                '_source': ESClient.preprocess_obj(obj),
            }
            for obj in model.query
        )
        bulk(self.client, docs_gen)

    def build_search_index(self, model):
        self.create_index(model)
        self.bulk_add_to_index(model)

    @staticmethod
    def preprocess_obj(obj):
        data = {}
        for field in obj.__searchable__:
            data[field] = getattr(obj, field)
        return data
