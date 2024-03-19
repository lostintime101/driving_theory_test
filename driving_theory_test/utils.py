from datetime import datetime

from flask_jwt_extended import set_access_cookies, create_access_token


def format_duration(value: float):
    return datetime.fromtimestamp(value).strftime("%Mm %Ssec")


def update_user_token(
        resp,
        claims: dict,
        exam_type=None,
        training_mode=None,
        number_of_questions=None,
        end_exam=None,
        answers=None,
        current_index=None,
        score=None,
        time_elapsed=None,
        start_time=None,
        time_remaining=None,
):
    exam_data = {
        "exam_type": exam_type or claims.get("exam_type"),
        "training_mode": training_mode or claims.get("training_mode"),
        "number_of_questions": number_of_questions or claims.get("number_of_questions"),
        "end_exam": end_exam or claims.get("end_exam"),
        "answers": answers or claims.get("answers"),
        "current_index": current_index if current_index is not None else claims.get("current_index", 0),
        "score": score or claims.get("score"),
        "time_elapsed": time_elapsed or claims.get("time_elapsed"),
        "start_time": start_time or claims.get("start_time"),
        "time_remaining": time_remaining or claims.get("time_remaining"),
    }
    set_access_cookies(resp, create_access_token(claims.get("sub"), additional_claims=exam_data))
