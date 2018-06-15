import json
import unittest

from api.factory import create_app
from config import API_BASE_PATH, TestingConfig


class RoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=TestingConfig)
        self.client = self.app.test_client()

    def test_get_movie_id(self):
        response = self.client.get(f'{API_BASE_PATH}/movies/m0')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.get_data())
        self.assertEqual(response_data['id'], 'm0')
        self.assertEqual(response_data['title'], "10 things i hate about you")
        self.assertCountEqual(response_data['genres'], ['comedy', 'romance'])
        self.assertEqual(len(response_data['characters']), 12)
        self.assertEqual(len(response_data['conversations']), 201)

    def test_get_movie_id_404(self):
        response = self.client.get(f'{API_BASE_PATH}/movies/m999')
        self.assertEqual(response.status_code, 404)

    def test_get_movies_pagination(self):
        response = self.client.get(f'{API_BASE_PATH}/movies')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.get_data())
        self.assertEqual(len(response_data['results']), 5)
        self.assertIn('m0', [m['id'] for m in response_data['results']])
        self.assertNotIn('m10', [m['id'] for m in response_data['results']])
        self.assertTrue('next' in response_data['links'])
        self.assertFalse('prev' in response_data['links'])
        self.assertDictEqual(
            response_data['meta'],
            {
                'page': 1,
                'start': 0,
                'limit': 5,
                'total_pages': 4,
                'total_items': 20
            }
        )

    def test_get_movies_pagination_404(self):
        response = self.client.get(f'{API_BASE_PATH}/movies?start=20')
        self.assertEqual(response.status_code, 404)
