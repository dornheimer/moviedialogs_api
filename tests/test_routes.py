import json
import unittest
from api import fdb
from api.factory import create_app
from config import TestingConfig, API_BASE_PATH
from db.models import Movie

MOVIE_DATA = {
    "characters": [],
    "genres": [],
    "id": '0',
    "imdb_rating": 6.2,
    "num_imdb_votes": 10421,
    "title": "1492: conquest of paradise",
    "year": "1992"
}


def add_movies(n=1):
    if n == 1:
        movie_data = MOVIE_DATA
        movie = Movie(**movie_data)
        fdb.session.add(movie)
        data = movie_data
    else:
        data = {}
        for i in range(n):
            movie_id = str(i)
            movie_data = MOVIE_DATA.copy()
            movie_data.update({'id': movie_id})
            movie = Movie(**movie_data)
            fdb.session.add(movie)
            data[movie_id] = movie_data
    fdb.session.commit()
    return data


class RoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config=TestingConfig)
        self.client = self.app.test_client()

        # Set up application context for the database
        self.app_context = self.app.app_context()
        self.app_context.push()
        fdb.create_all()

    def tearDown(self):
        fdb.session.remove()
        fdb.drop_all()
        self.app_context.pop()

    def test_get_movie_id(self):
        expected = add_movies()
        response = self.client.get(f'{API_BASE_PATH}/movies/0')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.get_data()), {'movie': expected})

    def test_get_movies_pagination(self):
        expected = add_movies(11)
        response = self.client.get(f'{API_BASE_PATH}/movies')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.get_data()),
            {'movies': {m_id: movie for m_id, movie in expected.items() if int(m_id) <= 9}}
        )
