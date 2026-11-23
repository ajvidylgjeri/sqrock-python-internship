from flask import Flask

from .config import Config
from .models import db
from .utils import error, rate_limit


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    from .routes.auth import bp as auth_bp
    from .routes.catalog import bp as catalog_bp
    from .routes.cart import bp as cart_bp
    from .routes.orders import bp as orders_bp
    for bp in (auth_bp, catalog_bp, cart_bp, orders_bp):
        app.register_blueprint(bp, url_prefix="/api")

    app.before_request(rate_limit)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(404)
    def nf(_):
        return error("Resource not found", 404)

    @app.errorhandler(405)
    def na(_):
        return error("Method not allowed", 405)

    @app.errorhandler(500)
    def se(_):
        return error("Internal server error", 500)

    with app.app_context():
        db.create_all()
    return app
