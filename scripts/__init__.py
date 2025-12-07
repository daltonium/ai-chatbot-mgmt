import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    templates_dir = os.path.join(BASE_DIR, 'templates')
    static_dir = os.path.join(BASE_DIR, 'static')

    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    app.config['SECRET_KEY'] = 'mini_project_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chatbots.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from . import models  # register models
    with app.app_context():
        db.create_all()

    from .auth_routes import auth_bp
    from .bot_routes import bot_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(bot_bp)

    return app
