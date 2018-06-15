from flask import Blueprint, request, jsonify, url_for
from sqlalchemy import inspect

from config import API_BASE_PATH
from db.models import (
    Character,
    Conversation,
    Genre,
    Line,
    Movie,
)

bp = Blueprint('routes', __name__, url_prefix=API_BASE_PATH)


def collect_movie_data(movie):
    data = object_as_dict(movie)
    related_data = {
        'characters': [object_as_dict(char) for char in movie.characters],
        'conversations': [c.id for c in movie.conversations],
        'genres': [g.name for g in movie.genres],
    }
    data.update(related_data)
    return data


def object_as_dict(obj):
    """
    Convert sqlalchemy row object to python dict.

    Reference: https://stackoverflow.com/a/37350445/8074325
    """
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


@bp.route('/characters/<string:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.get_or_404(character_id)
    return jsonify(object_as_dict(character))


@bp.route('/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    return jsonify(object_as_dict(conversation))


@bp.route('/conversations/<int:conversation_id>/lines', methods=['GET'])
def get_conversation_lines(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    return jsonify([object_as_dict(l) for l in conversation.lines])


@bp.route('/genres/<int:genre_id>', methods=['GET'])
def get_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    return jsonify(object_as_dict(genre))


@bp.route('/lines/<string:line_id>', methods=['GET'])
def get_line(line_id):
    line = Line.query.get_or_404(line_id)
    return jsonify(object_as_dict(line))


@bp.route('/movies/<string:movie_id>', methods=['GET'])
def get_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return jsonify(collect_movie_data(movie))


@bp.route('/movies', methods=['GET'])
def get_movies():
    limit = request.args.get('limit', 5, type=int)
    start = request.args.get('start', 0, type=int)
    page_number = int(start / limit) + 1

    paginated = Movie.query.paginate(page=page_number, per_page=limit)
    movies_data = [collect_movie_data(m) for m in paginated.items]

    meta_data = {
        'page': page_number,
        'start': start,
        'limit': limit,
        'total_pages': paginated.pages,
        'total_items': paginated.total
    }

    links = {}
    if paginated.has_next:
        next_ = start + limit
        links['next'] = url_for('.get_movies', limit=limit, start=next_)
    if paginated.has_prev:
        prev = start - limit
        links['prev'] = url_for('.get_movies', limit=limit, start=prev)

    return jsonify({'results': movies_data, 'meta': meta_data, 'links': links})
