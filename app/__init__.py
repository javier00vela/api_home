from flask import Flask

from app.api.v1.routes import v1
from app.core.registry import registry
from app.providers import register_providers


def create_app() -> Flask:
    app = Flask(__name__)
    register_providers(registry)
    app.register_blueprint(v1, url_prefix="/api/v1")
    return app
