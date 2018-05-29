import os
import unittest

from api.factory import create_app
from config import TestingConfig
from db.models import Movie


movie_titles = [
    "a nightmare on elm street: the dream child",
    "a nightmare on elm street 4: the dream master",
]

class ES_TestingConfig(TestingConfig):
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL')


class SearchTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=ES_TestingConfig)
        self.client = self.app.test_client()

        # Set up application context for the database
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app.elasticsearch.delete_index(Movie)

    def test_search(self):
        self.app.elasticsearch.initialize_model(Movie)

        query, total = self.app.elasticsearch.search(Movie, 'nightma', 1, 10)
        self.assertEqual(total, len(movie_titles))
        self.assertTrue(all(mt in [m.title for m in query] for mt in movie_titles))
