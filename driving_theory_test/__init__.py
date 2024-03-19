import os

from datetime import datetime, timedelta
from flask import Flask
from flask_jwt_extended import JWTManager

from .utils import format_duration, update_user_token


def create_app(*args, **kwargs):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.root_path, "question_bank.db"), YEAR=datetime.now().strftime("%Y")
    )
    from . import home, db, exam

    db.init_app(app)
    app.register_blueprint(home.bp)
    app.register_blueprint(exam.bp)
    app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)
    JWTManager(app)

    return app
