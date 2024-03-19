import sqlite3
import random

import click
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


@click.command("init-db")
def init_db_command():
    click.echo("Initialized the database.")


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_question_id(q_id):
    db = get_db()
    cursor = db.cursor()

    rows = cursor.execute(
        "SELECT * FROM question_bank WHERE q_id = ?",
        (q_id,),
    ).fetchall()
    return rows[0]


def get_all_questions_id():
    db = get_db()
    cursor = db.cursor()

    rows = cursor.execute(
        "SELECT q_id FROM question_bank",
    ).fetchall()
    return rows


def create_question_bank(nb_q=50):
    # creates a list of distinct random ints from 1-150
    all_questions = get_all_questions_id()
    questions = []
    for _ in range(nb_q):
        selected_q = random.choices(all_questions)
        questions.append(selected_q[0][0])
        all_questions.pop(all_questions.index(selected_q[0]))

    return questions
