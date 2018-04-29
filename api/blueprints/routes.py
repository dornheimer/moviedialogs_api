from flask import Blueprint, request, jsonify
from config import API_BASE_PATH
from sqlalchemy import inspect
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
    return jsonify({'character': object_as_dict(character)})


@bp.route(f'{API_BASE_PATH}/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    return jsonify({'conversation': object_as_dict(conversation)})


@bp.route(f'{API_BASE_PATH}/genres/<int:genre_id>', methods=['GET'])
def get_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    return jsonify({'genre': object_as_dict(genre)})


@bp.route(f'{API_BASE_PATH}/lines/<string:line_id>', methods=['GET'])
def get_line(line_id):
    line = Line.query.get_or_404(line_id)
    return jsonify({'line': object_as_dict(line)})


@bp.route(f'{API_BASE_PATH}/movies/<string:movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    data = object_as_dict(movie)
    related_data = {
        'characters': [char.id for char in movie.characters],
        'genres': [g.name for g in movie.genres],
    }
    data.update(related_data)
    return jsonify({'movie': data})


@bp.route(f'{API_BASE_PATH}/movies', methods=['GET'])
def get_movies():
    page = request.args.get('page', 1, type=int)
    movies = Movie.query.paginate(page, per_page=10).items
    movies_data = {}
    for m in movies:
        data = object_as_dict(m)
        related_data = {
            'characters': [char.id for char in m.characters],
            'genres': [g.name for g in m.genres],
        }
        data.update(related_data)
        movies_data[m.id] = data
    return jsonify({'movies': movies_data})
