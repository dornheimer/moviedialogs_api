import json
from collections import defaultdict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.blueprints.routes import object_as_dict
from config import Config
from db.models import Movie
from tests.data import TESTDATA_PATH


def get_movies(session, num_movies):
    movies = defaultdict(dict)
    for m_id in range(num_movies):
        current_id = f"m{m_id}"
        movie = session.query(Movie).get(current_id)

        movies[m_id]['movie_data'] = object_as_dict(movie)
        movies[m_id]['movie_characters'] = [object_as_dict(c) for c in movie.characters]
        movies[m_id]['movie_conversations'] = [object_as_dict(k) for k in movie.conversations]
        movies[m_id]['movie_genres'] = [object_as_dict(g) for g in movie.genres]
        movies[m_id]['movie_lines'] = [object_as_dict(l) for l in movie.lines]

    return movies


def export_as_json(movies):
    with open(TESTDATA_PATH, 'w') as f:
        json.dump(movies, f, indent=2)


def main():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    movies = get_movies(session, 20)
    export_as_json(movies)


if __name__ == '__main__':
    main()
