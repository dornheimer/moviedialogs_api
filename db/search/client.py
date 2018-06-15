import json
import time

from flask import abort
from sqlalchemy import case
from elasticsearch.helpers import bulk


class ESClient:
    def __init__(self, client, settings):
        self.client = client
        self.settings = self._load_settings(settings)

    def _load_settings(self, settings_json):
        with open(settings_json) as f:
            return json.load(f)

    def initialize_model(self, model):
        if not self.index_exists(model):
            self.build_search_index(model)
            # Sleep to make index searchable
            time.sleep(1)

    def create_index(self, model):
        self.client.indices.create(index=model.__tablename__, body=self.settings)

    def index_exists(self, model):
        return self.client.indices.exists(model.__tablename__)

    def delete_index(self, model):
        self.client.indices.delete(index=model.__tablename__)

    def query_index(self, index, query, start, limit):
        if self.client is None:
            return [], 0
        body = {
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['*']
                }
            },
            'from': start,
            'size': limit
        }
        search = self.client.search(
            index=index,
            doc_type=index,
            body=body
        )
        ids = [hit['_id'] for hit in search['hits']['hits']]
        return ids, search['hits']['total']

    def search(self, model, query, start, limit):
        ids, total = self.query_index(model.__tablename__, query, start, limit)
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
