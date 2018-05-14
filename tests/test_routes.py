import json
import unittest
from api.factory import create_app
from config import TestingConfig, API_BASE_PATH


class RoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=TestingConfig)
        self.client = self.app.test_client()

    def test_get_movie_id(self):
        response = self.client.get(f'{API_BASE_PATH}/movies/m0')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.get_data())
        self.assertEqual(response_data['movie']['id'], 'm0')
        self.assertEqual(response_data['movie']['title'], "10 things i hate about you")
        self.assertCountEqual(response_data['movie']['genres'], ['comedy', 'romance'])
        self.assertEqual(len(response_data['movie']['characters']), 12)

    def test_get_movies_pagination(self):
        response = self.client.get(f'{API_BASE_PATH}/movies')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.get_data())
        self.assertEqual(len(response_data['movies']), 10)
        self.assertIn('m0', response_data['movies'])
        self.assertNotIn('m10', response_data['movies'])
