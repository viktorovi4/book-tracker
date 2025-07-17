from flask import Flask
from .extensions import db, login_manager
from .config import Config


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from .models import Book, User
        db.create_all()
        from .routes import init_routes
        init_routes(app)

    return app