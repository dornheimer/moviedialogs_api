from elasticsearch import Elasticsearch
from flask import Flask
from werkzeug.utils import find_modules, import_string

from api import fdb, migrate # pylint: disable=cyclic-import
from db.search import ESClient


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    fdb.init_app(app)
    migrate.init_app(app, fdb)

    configure_elasticsearch(app)
    register_blueprints(app)

    return app


def register_blueprints(app):
    """Register all blueprint modules.

    Reference: Armin Ronacher, "Flask for Fun and for Profit" (PyBay 2016).
    """
    for name in find_modules('api.blueprints'):
        mod = import_string(name)
        if hasattr(mod, 'bp'):
            app.register_blueprint(mod.bp)
    return None


def configure_elasticsearch(app):
    es_client = Elasticsearch(app.config['ELASTICSEARCH_URL']) \
        if app.config['ELASTICSEARCH_URL'] else None
    es_settings = app.config['ELASTICSEARCH_SETTINGS']
    app.elasticsearch = ESClient(es_client, es_settings)
