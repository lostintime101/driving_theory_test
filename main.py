from flask import Flask, render_template, request
import random
import time
import threading
import sqlite3

# global variables
MINI_NUMBER_OF_QUESTIONS = 10
FULL_NUMBER_OF_QUESTIONS = 50
SECONDS_PER_QUESTION = 60
YEAR = time.localtime().tm_year

TIME_FOR_MINI_TEST = (MINI_NUMBER_OF_QUESTIONS * SECONDS_PER_QUESTION)
TIME_FOR_FULL_TEST = (FULL_NUMBER_OF_QUESTIONS * SECONDS_PER_QUESTION)  # TODO rework this so it's 1 variable, time per question i.e. 60 seconds


number_of_questions = 1
time_for_test = (number_of_questions * SECONDS_PER_QUESTION)

# timer related variables
time_is_up = False
timer_reset = False

# question related variables
score = 0
current_quest = -1
questions = []
question_bank = []

# initiates app
app = Flask(__name__)

# number of seconds left
my_timer = TIME_FOR_MINI_TEST


# returns question information from SQL database
def database_call(q_id):
    db = sqlite3.connect("question_bank.db")
    cursor = db.cursor()

    rows = cursor.execute(
        "SELECT * FROM question_bank WHERE q_id = ?",
        (q_id,),
    ).fetchall()
    print(rows)

    return rows


# exam countdown timer
def countdown():
    global my_timer, time_is_up, timer_reset

    timer_reset = False

    for x in range(my_timer):
        my_timer = my_timer - 1
        time.sleep(1)
        print(my_timer)
        if timer_reset:
            return 0

    time_is_up = True
    print("TIME'S UP!")


# timer needs to run in parallel with other logic
countdown_thread = threading.Thread(target=countdown)


def create_question_bank():
    # creates a list of distinct random ints from 1-150
    for i in range(200):
        num = random.randint(1, 150)
        if num not in questions:
            questions.append(num)
        if len(questions) >= number_of_questions:
            break
    print(questions)
    key_list = ["question", "true_answer", "users_answer", "true_txt", "true_pic", "user_txt", "user_pic", "quest_txt",
                "quest_pic"]

    # list of dictionaries, 1 for each question
    # "none" values will be updated later as each question is loaded from the database and shown to the user
    # note: "true_answer"=5, "users_answer"=0 are initially set this way, so they don't equal each other
    for i in range(len(questions)):
        question_bank.append(
            {key_list[0]: questions[i], key_list[1]: 5, key_list[2]: 0, key_list[3]: "none", key_list[4]: "none",
             key_list[5]: "none", key_list[6]: "none", key_list[7]: "none", key_list[8]: "none"}
        )

    print(question_bank)
    return question_bank


@app.route('/')
def home():
    global current_quest, score, questions, question_bank, time_is_up

    # everything is reset (score, timer etc.)
    score = 0
    current_quest = -1
    time_is_up = False

    return render_template("cover.html",
                           year=YEAR,
                           full_questions=FULL_NUMBER_OF_QUESTIONS,
                           full_time=(int((FULL_NUMBER_OF_QUESTIONS * SECONDS_PER_QUESTION)/60)),
                           mini_questions=MINI_NUMBER_OF_QUESTIONS,
                           mini_time=(int((MINI_NUMBER_OF_QUESTIONS * SECONDS_PER_QUESTION)/60)))


# standard question page template
@app.route('/exam/', methods=['GET', 'POST'])
def exam():
    global number_of_questions, current_quest, score, my_timer, question_bank, time_is_up, timer_reset

    # start countdown timer if not already started (i.e. on the 1st question)
    try:
        countdown_thread.start()
    except RuntimeError:
        pass

    # update question bank with info from previous question
    if request.method == 'POST':
        data = request.form
        answer = data["Answer"]
        # answer == 0 means the user clicked 'previous' or 'next' button, question bank should not be updated
        if answer != "0":
            correct = data["Correct"]
            user_pic = data["User_pic"]
            user_txt = data["User_txt"]

            question_bank[current_quest]["users_answer"] = answer
            question_bank[current_quest]["true_answer"] = correct
            question_bank[current_quest]["user_pic"] = user_pic
            question_bank[current_quest]["user_txt"] = user_txt

    # check for time up. If so, send user to results page
    if time_is_up:
        current_quest = number_of_questions

    # moves to next question
    current_quest += 1

    # check if the last question was the final question
    if current_quest >= number_of_questions:

        # calculate score + pass/fail using the data in the question bank
        for i in range(number_of_questions):

            if question_bank[i]["users_answer"] == question_bank[i]["true_answer"]:
                score += 1

        percent_s = int((score / number_of_questions) * 100)
        pass_fail = "FAIL🥹"
        if percent_s >= 90:
            pass_fail = "PASS🥳"

        time_up = False
        # if this boolean is set to True it shows warning to user on the results page that their time ran out
        if time_is_up:
            time_up = True

        # calculates time that remained at end in minutes
        seconds = my_timer % 60
        mins = int((my_timer - seconds) / 60)
        seconds = str(seconds)
        if len(seconds) == 1:
            seconds = "0" + seconds
        time_remain = str(mins) + ":" + str(seconds)

        total_time = time_for_test - my_timer

        # calculates time per question
        time_per_quest = int(total_time / number_of_questions)

        # calculates time taken in minutes
        seconds = total_time % 60
        mins = int((total_time - seconds) / 60)
        seconds = str(seconds)
        if len(seconds) == 1:
            seconds = "0" + seconds
        total_time = str(mins) + ":" + str(seconds)

        # stops the timer
        timer_reset = True

        return render_template("results.html",
                               year=YEAR,
                               total_quest=number_of_questions,
                               total_correct=score,
                               pass_fail=pass_fail,
                               percent_score=percent_s,
                               total_time=total_time,
                               time_remain=time_remain,
                               time_per_quest=time_per_quest,
                               time_up=time_up,
                               dump=question_bank
                               )

    # collects info for new question from the sql database
    print("this is the current question", current_quest)
    q = question_bank[current_quest]["question"]
    question = database_call(q)[0]
    quest = current_quest + 1
    question_bank[current_quest]["true_pic"] = question[(int(question[11]) * 2) + 2]
    question_bank[current_quest]["true_txt"] = question[(int(question[11]) * 2) + 1]
    question_bank[current_quest]["quest_txt"] = question[1]
    question_bank[current_quest]["quest_pic"] = question[2]

    # serves up new question data to template
    return render_template("question.html",
                           year=YEAR,
                           total=number_of_questions,
                           question=quest,
                           question_text=question[1],
                           question_pic=question[2],
                           answer1_text=question[3],
                           answer1_pic=question[4],
                           answer2_text=question[5],
                           answer2_pic=question[6],
                           answer3_text=question[7],
                           answer3_pic=question[8],
                           answer4_text=question[9],
                           answer4_pic=question[10],
                           correct_ans=question[11],
                           seconds=my_timer,
                           progress=int((quest / number_of_questions) * 100)
                           )


# user navigates backwards using "previous button", revised question page template
@app.route('/exam/p', methods=['GET', 'POST'])
def previous_exam():
    global current_quest, my_timer, time_is_up, score, question_bank

    # check for time up. If so, send to results page
    # TODO issue here, this is not enough info to display proper results page
    if time_is_up:
        return render_template("results.html",
                               year=YEAR,
                               total=number_of_questions,
                               seconds=my_timer
                               )

    # returns to previous question
    current_quest -= 1
    q = question_bank[current_quest]["question"]

    # collects info for new question from the sql database
    q = question_bank[current_quest]["question"]
    question = database_call(q)[0]

    quest = current_quest + 1

    # serves all question data to template
    return render_template("question.html",
                           year=YEAR,
                           total=number_of_questions,
                           question=quest,
                           question_text=question[1],
                           question_pic=question[2],
                           answer1_text=question[3],
                           answer1_pic=question[4],
                           answer2_text=question[5],
                           answer2_pic=question[6],
                           answer3_text=question[7],
                           answer3_pic=question[8],
                           answer4_text=question[9],
                           answer4_pic=question[10],
                           correct_ans=question[11],
                           seconds=my_timer,
                           progress=int((quest / number_of_questions) * 100)
                           )


# About page
@app.route('/pre-exam/', methods=['GET', 'POST'])
def pre_exam():
    global number_of_questions, my_timer

    exam_type = ""

    if request.method == 'POST':
        data = request.form
        exam_type = data["Length"]

    if exam_type == "Full Exam":
        number_of_questions = FULL_NUMBER_OF_QUESTIONS
    else:
        number_of_questions = MINI_NUMBER_OF_QUESTIONS

    my_timer = number_of_questions * 60

    create_question_bank()

    return render_template("pre-exam.html",
                           year=YEAR,
                           minutes=number_of_questions,
                           questions=number_of_questions
                           )


# About page
@app.route('/about/')
def about():
    return render_template("about.html",
                           year=YEAR,
                           )


if __name__ == "__main__":
    app.run(debug=True)


# Urgent
# TODO BUG timer keeps resetting, timer is messed up
# TODO BUG question bank not refreshing each time when doing quick test
# TODO BUG if exam times out, then retake, time won't reset or display
# TODO missing picture 81.4.jpg / 51.4.jpg

# Non urgent
# TODO add scroll to top on results page
# TODO test for responsiveness across various devices
# TODO remove debug on live site
# TODO redo text on about page

# TODO add automated unit tests
