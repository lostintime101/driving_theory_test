import uuid
from datetime import datetime

import math
from flask import Blueprint, redirect, render_template, request, url_for, jsonify, make_response, g
from flask_jwt_extended import jwt_required, get_jwt, unset_jwt_cookies, set_access_cookies, create_access_token

from driving_theory_test.utils import format_duration, update_user_token

bp = Blueprint("exam", __name__, url_prefix="/exam")


@bp.route("/get_answer", methods=["POST"])
@jwt_required()
def get_answer():
    claims = get_jwt()
    if claims.get("training_mode"):
        answers: list = claims.get("answers")
        question = g.db.get_question_id(answers[claims.get("current_index")][0])
        return jsonify({"ans_id": question["ans_num"]})
    return make_response(jsonify({"error": "Exam mode... No cheating!"}), 400)


@bp.route("/results", methods=["GET"])
@jwt_required()
def results():
    claims = get_jwt()
    current_index = claims.get("current_index")
    answers: list = claims.get("answers")
    time_elapsed: float = claims.get("time_elapsed")
    time_remaining: float = claims.get("time_remaining")
    number_of_questions: int = int(claims.get("number_of_questions"))
    time_up = False
    if datetime.now().timestamp() > claims.get("end_exam"):
        time_up = True
    failed_questions = []
    score = 0
    #  Compute result
    for answer in answers:
        question = g.db.get_question_id(answer[0])
        if question["ans_num"] == answer[1]:
            score += 1
        else:
            wrong_answer = {
                "true_answer": question["ans_num"],
                "quest_txt": question["q_txt"],
                "quest_pic": question["q_pic"],
                "user_txt": None,
                "user_pic": None,
                "true_txt": question["ans_txt"],
                "true_pic": None,
                "q_id": question["q_id"],
            }
            if answer[1] == "1":
                wrong_answer["user_txt"] = question["a1_txt"]
                wrong_answer["user_pic"] = question["a1_pic"]
            elif answer[1] == "2":
                wrong_answer["user_txt"] = question["a2_txt"]
                wrong_answer["user_pic"] = question["a2_pic"]
            elif answer[1] == "3":
                wrong_answer["user_txt"] = question["a3_txt"]
                wrong_answer["user_pic"] = question["a3_pic"]
            elif answer[1] == "4":
                wrong_answer["user_txt"] = question["a4_txt"]
                wrong_answer["user_pic"] = question["a4_pic"]
            failed_questions.append(wrong_answer)

    percent_s = int((score / number_of_questions) * 100)
    pass_fail = "FAIL🥹"
    if percent_s >= 90:
        pass_fail = "PASS🥳"

    if not time_elapsed or not time_remaining:
        time_elapsed = datetime.now().timestamp() - float(claims.get("start_time"))
        time_remaining = float(claims.get("end_exam")) - datetime.now().timestamp()
        if time_remaining < 0:
            time_remaining = 0

    resp = make_response(
        render_template(
            "exam/results.html",
            total_quest=number_of_questions,
            total_correct=score,
            pass_fail=pass_fail,
            percent_score=percent_s,
            time_elapsed=format_duration(time_elapsed),
            time_remaining=format_duration(time_remaining),
            time_up=time_up,
            time_per_quest=math.ceil(time_elapsed / number_of_questions),
            failed_questions=failed_questions,
        )
    )
    update_user_token(
        resp,
        claims,
        answers=answers,
        current_index=current_index,
        time_elapsed=time_elapsed,
        score=score,
        time_remaining=time_remaining,
    )
    return resp


# standard question page template
@bp.route("/", methods=["GET", "POST"])
@jwt_required()
def exam():
    claims = get_jwt()
    if claims.get("score", False):
        return redirect(url_for("exam.results"))
    current_index = claims.get("current_index")
    answers: list = claims.get("answers")
    training_mode: bool = claims.get("training_mode")
    number_of_questions: int = int(claims.get("number_of_questions"))

    seconds_left = float(claims.get("end_exam")) - datetime.now().timestamp()

    # check for time up. If so, send user to results page
    if datetime.now().timestamp() > claims.get("end_exam"):
        return make_response(redirect(url_for("exam.results")))
    if current_index >= len(answers):
        # End exam
        return redirect(url_for("exam.results"))
    # update question bank with info from previous question
    if request.method == "POST":
        data = request.form
        # answer == 0 means the user clicked 'previous' or 'next' button, question bank should not be updated
        if data["Answer"] != "0":
            answers[current_index][1] = data["Answer"]
        current_index += 1
        resp = make_response(redirect(url_for("exam.exam")))
    else:
        question = g.db.get_question_id(answers[current_index][0])
        question_formatted = {
            "id": question["q_id"],
            "question_text": question["q_txt"],
            "question_pic": question["q_pic"],
            "answers": {
                "1": {"text": question["a1_txt"], "pic": question["a1_pic"]},
                "2": {"text": question["a2_txt"], "pic": question["a2_pic"]},
                "3": {"text": question["a3_txt"], "pic": question["a3_pic"]},
                "4": {"text": question["a4_txt"], "pic": question["a4_pic"]}
            },
            # User answer
            "user_ans": answers[current_index][1] if len(answers[current_index]) else 0
        }

        resp = make_response(
            render_template(
                "exam/question.html",
                total=number_of_questions,
                question=question_formatted,
                current_index=current_index,
                seconds=seconds_left,
                training_mode=training_mode,
                progress=int((current_index / number_of_questions) * 100),
            )
        )

    update_user_token(resp, claims, answers=answers, current_index=current_index)
    # serves up new question data to template
    return resp


# user navigates backwards using "previous button", revised question page template
@bp.route("/p", methods=["POST"])
@jwt_required()
def previous_exam():
    claims = get_jwt()
    current_index = claims.get("current_index")
    if current_index > 0:
        current_index -= 1
    resp = make_response(redirect(url_for("exam.exam")))
    update_user_token(resp, claims, current_index=current_index)
    return resp


@bp.route("/start_exam", methods=["POST"])
@jwt_required()
def start_exam():
    claims = get_jwt()
    resp = make_response(redirect(url_for("exam.exam")))
    update_user_token(
        resp,
        claims,
        current_index=0,
        start_time=datetime.now().timestamp(),
        end_exam=datetime.now().timestamp() + int(claims.get("number_of_questions")) * 60,
    )
    return resp


@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    resp = make_response(redirect(url_for("home.home")))
    unset_jwt_cookies(resp)
    return resp


# Pre-exam page with instructions for user
@bp.route("/pre-exam", methods=["POST"])
def pre_exam():
    data = request.form
    if "exam_type" not in data.keys():
        return redirect(url_for('home.home'))
    exam_type = data.get("exam_type")
    number_of_questions = 50 if exam_type == "Full Exam" else 10
    resp = make_response(redirect(url_for("exam.pre_exam")))
    exam_data = {
        "exam_type": exam_type,
        "training_mode": True if data.get("training_mode", False) else False,
        "number_of_questions": str(number_of_questions),
        "answers": [],
    }
    for selected_question in g.db.create_question_bank(number_of_questions):
        # Q_id, user answer
        exam_data["answers"].append(
            (
                selected_question,
                0,
            )
        )
    set_access_cookies(resp, create_access_token(uuid.uuid4().hex[:10].upper(), additional_claims=exam_data))
    return resp


@bp.route("/pre-exam", methods=["GET"])
@jwt_required()
def get_pre_exam():
    claims = get_jwt()
    if "number_of_questions" not in claims:
        return redirect(url_for('home.home'))
    return make_response(
        render_template("exam/pre-exam.html",
                        number_of_questions=claims.get("number_of_questions"))
    )
