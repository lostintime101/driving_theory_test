import os

from datetime import datetime, timedelta
from flask import Flask, make_response, jsonify
from flask_jwt_extended import JWTManager


def create_app(*args, **kwargs):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.root_path, "question_bank.db")
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

    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    @app.errorhandler(Exception)
    def all_exception_handler(error):
        return make_response(jsonify({"error": f"Error : {error.args}"}), 400)

    return app
