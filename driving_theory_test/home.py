from flask import Blueprint, render_template

bp = Blueprint("home", __name__, url_prefix="/")


@bp.route("/")
def home():
    return render_template("home/cover.html")


@bp.route("/about")
def about():
    return render_template("home/about.html")
