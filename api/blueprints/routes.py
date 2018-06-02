from flask import Blueprint, request, jsonify
from sqlalchemy import inspect

from config import API_BASE_PATH
from db.models import (
    Character,
    Conversation,
    Genre,
    Line,
    Movie,
)

bp = Blueprint('routes', __name__)


def object_as_dict(obj):
    """
    Convert sqlalchemy row object to python dict.

    Reference: https://stackoverflow.com/a/37350445/8074325
    """
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


@bp.route(f'{API_BASE_PATH}/characters/<string:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get_or_404(character_id)
    return jsonify(object_as_dict(character))


@bp.route(f'{API_BASE_PATH}/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    return jsonify(object_as_dict(conversation))


@bp.route(f'{API_BASE_PATH}/genres/<int:genre_id>', methods=['GET'])
def get_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    return jsonify(object_as_dict(genre))


@bp.route(f'{API_BASE_PATH}/lines/<string:line_id>', methods=['GET'])
def get_line(line_id):
    line = Line.query.get_or_404(line_id)
    return jsonify(object_as_dict(line))


@bp.route(f'{API_BASE_PATH}/movies/<string:movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    data = object_as_dict(movie)
    related_data = {
        'characters': [char.id for char in movie.characters],
        'genres': [g.name for g in movie.genres],
    }
    data.update(related_data)
    return jsonify(data)


@bp.route(f'{API_BASE_PATH}/movies', methods=['GET'])
def get_movies():
    limit = request.args.get('limit', 5, type=int)
    start = request.args.get('start', 0, type=int)
    page_number = int(start / limit) + 1
    paginated = Movie.query.paginate(page=page_number, per_page=limit)

    movies = paginated.items
    movies_data = []
    for m in movies:
        data = object_as_dict(m)
        related_data = {
            'characters': [char.id for char in m.characters],
            'genres': [g.name for g in m.genres],
        }
        data.update(related_data)
        movies_data.append(data)

    meta_data = {
        'page': page_number,
        'start': start,
        'limit': limit,
        'total_pages': paginated.pages,
        'total_items': paginated.total
    }

    links = {}
    if paginated.has_next:
        links['next'] = f'{API_BASE_PATH}/movies?limit={limit}&start={start+limit}'
    if paginated.has_prev:
        links['prev'] = f'{API_BASE_PATH}/movies?limit={limit}&start={start-limit}'

    return jsonify({'results': movies_data, 'meta': meta_data, 'links': links})
