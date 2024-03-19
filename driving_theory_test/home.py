from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

bp = Blueprint("home", __name__, url_prefix="/")


@bp.route("/")
def home():
    return render_template("home/cover.html")


@bp.route("/about")
def about():
    return render_template("home/about.html")
