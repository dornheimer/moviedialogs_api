from flask import Flask
from werkzeug.utils import find_modules, import_string

from api import fdb, migrate


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    fdb.init_app(app)
    migrate.init_app(app, fdb)

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
