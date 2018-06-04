from flask import Blueprint, jsonify
from werkzeug.http import HTTP_STATUS_CODES

bp = Blueprint('errors', __name__)


def error_response(status):
    message = HTTP_STATUS_CODES[status]
    return jsonify({'status': status, 'body': {'error_message': message}}), status


@bp.app_errorhandler(400)
def bad_request(error):
    return error_response(400)


@bp.app_errorhandler(404)
def not_found(error):
    return error_response(404)
