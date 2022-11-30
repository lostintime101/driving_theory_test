from flask import Flask, render_template, request
import random
import time
import json
import threading

YEAR = time.localtime().tm_year
NUMBER_OF_QUESTIONS = 6
TIME_FOR_TEST = (NUMBER_OF_QUESTIONS * 60)

# timer variables
my_timer = TIME_FOR_TEST
time_is_up = False
timer_reset = False

# creates score, current question and score tracker (tracker records which questions were answered right or wrong)
score = 0
current_quest = -1
questions = []
question_bank = []

app = Flask(__name__)

# countdown timer function
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

countdown_thread = threading.Thread(target=countdown)

# TODO remove this test at end
@app.route('/jumbo/')
def jumbo():
    return render_template("modals.html",
                           year=YEAR,
                           total_quest = NUMBER_OF_QUESTIONS,
                           total_correct="10",
                           pass_fail="PASS",
                           percent_score="90",
                           total_time="15:04",
                           time_remain="00:44",
                           time_per_quest="5.5",
                           time_up=False,
                           dump=question_bank
                           )


@app.route('/')
def home():
    global current_quest, score, questions, question_bank, time_is_up
    score = 0
    current_quest = -1
    time_is_up = False

    # creates question selection -- an array of distinct random ints
    # 1st step (1/3) to creating question bank
    questions = []
    for i in range(200):
        num = random.randint(1, 150)
        if num not in questions:
            questions.append(num)
        if len(questions) >= NUMBER_OF_QUESTIONS:
            break

    print(questions)

    key_list = ["question", "true_answer", "users_answer", "true_txt", "true_pic", "user_txt", "user_pic", "quest_txt",
                "quest_pic"]
    n = len(questions)
    question_bank = []
    for i in range(n):
        # 2nd step (2/3), we set a blank template for each question with "true_answer"=5 and "users_answer"=0, so they don't ==
        # as real info is added to the bank later both will update to 1-4
        question_bank.append(
            {key_list[0]: questions[i], key_list[1]: 5, key_list[2]: 0, key_list[3]: "none", key_list[4]: "none",
             key_list[5]: "none", key_list[6]: "none", key_list[7]: "none", key_list[8]: "none"})
    print(question_bank)

    return render_template("cover.html", year=YEAR, questions=NUMBER_OF_QUESTIONS, time=(int(TIME_FOR_TEST / 60)))


# basic question page template
@app.route('/exam/', methods=['GET', 'POST'])
def exam():
    global NUMBER_OF_QUESTIONS, current_quest, score, my_timer, question_bank, time_is_up, timer_reset

    # start countdown timer if not already started
    try:
        countdown_thread.start()
    except RuntimeError:
        pass

    # collect answer submitted from previous question
    # this is 3rd step (3/3) in creation of question bank
    if request.method == 'POST':
        data = request.form
        answer = data["Answer"]
        # answer = 0 means user clicked previous or next button, no change to scores
        if answer != "0":
            correct = data["Correct"]
            user_pic = data["User_pic"]
            user_txt = data["User_txt"]

            question_bank[current_quest]["users_answer"] = answer
            question_bank[current_quest]["true_answer"] = correct
            question_bank[current_quest]["user_pic"] = user_pic
            question_bank[current_quest]["user_txt"] = user_txt

    # check for time up. If so, send to results page
    if time_is_up:
        current_quest = NUMBER_OF_QUESTIONS

    # moves to next question
    current_quest += 1

    # check if last question was final question
    if current_quest >= NUMBER_OF_QUESTIONS:

        # calculates score + pass/fail using the data in the question bank
        for i in range(NUMBER_OF_QUESTIONS):

            if question_bank[i]["users_answer"] == question_bank[i]["true_answer"]:
                score += 1

        percent_s = int((score / NUMBER_OF_QUESTIONS) * 100)
        pass_fail = "FAIL"
        if percent_s >= 90:
            pass_fail = "PASS"

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

        total_time = TIME_FOR_TEST - my_timer

        # calculates time per question
        time_per_quest = int(total_time / NUMBER_OF_QUESTIONS)

        # calculates time taken in minutes
        seconds = total_time % 60
        mins = int((total_time - seconds) / 60)
        seconds = str(seconds)
        if len(seconds) == 1:
            seconds = "0" + seconds
        total_time = str(mins) + ":" + str(seconds)

        #stops the timer
        timer_reset = True

        return render_template("results.html",
                               year=YEAR,
                               total_quest=NUMBER_OF_QUESTIONS,
                               total_correct=score,
                               pass_fail=pass_fail,
                               percent_score=percent_s,
                               total_time=total_time,
                               time_remain=time_remain,
                               time_per_quest=time_per_quest,
                               time_up=time_up,
                               dump=question_bank
                               )

    # collects all data for new question from the json file
    q = question_bank[current_quest]["question"]
    with open("static/questions.json", "r", encoding = "utf-8") as f:
        dict = json.load(f)
        question = dict["quiz"][f"q{q}"]

    quest = current_quest + 1
    q_text = question["question"]["text"]
    q_pic = question["question"]["picture"]
    a1_txt = question["options"]["1"]["text"]
    a1_pic = question["options"]["1"]["picture"]
    a2_txt = question["options"]["2"]["text"]
    a2_pic = question["options"]["2"]["picture"]
    a3_txt = question["options"]["3"]["text"]
    a3_pic = question["options"]["3"]["picture"]
    a4_txt = question["options"]["4"]["text"]
    a4_pic = question["options"]["4"]["picture"]
    correct = question["answer"]["number"]

    question_bank[current_quest]["true_pic"] = question["options"][correct]["picture"]
    question_bank[current_quest]["true_txt"] = question["options"][correct]["text"]
    question_bank[current_quest]["quest_txt"] = q_text
    question_bank[current_quest]["quest_pic"] = q_pic

    # serves all new question data to template
    return render_template("question.html",
                           year=YEAR,
                           total=NUMBER_OF_QUESTIONS,
                           question=quest,
                           question_text=q_text,
                           question_pic=q_pic,
                           answer1_text=a1_txt,
                           answer1_pic=a1_pic,
                           answer2_text=a2_txt,
                           answer2_pic=a2_pic,
                           answer3_text=a3_txt,
                           answer3_pic=a3_pic,
                           answer4_text=a4_txt,
                           answer4_pic=a4_pic,
                           correct_ans=correct,
                           seconds=my_timer,
                           progress= int((quest / NUMBER_OF_QUESTIONS) * 100)
                           )


# question page template exclusively for when user navigates back using the previous button
@app.route('/exam/p', methods=['GET', 'POST'])
def previous_exam():
    global current_quest, my_timer, time_is_up, score, question_bank

    # check for time up. If so, send to results page
    #TODO issue here, this is not enough info to display proper results page
    if time_is_up == True:
        return render_template("results.html",
                               year=YEAR,
                               total=NUMBER_OF_QUESTIONS,
                               seconds=my_timer
                               )

    # returns to previous question
    current_quest -= 1
    q = question_bank[current_quest]["question"]

    # collects all data for new question from the json file
    with open("static/questions.json", "r", encoding = "utf-8") as f:
        dict = json.load(f)
        question = dict["quiz"][f"q{q}"]

    quest = current_quest + 1
    q_text = question["question"]["text"]
    q_pic = question["question"]["picture"]
    a1_txt = question["options"]["1"]["text"]
    a1_pic = question["options"]["1"]["picture"]
    a2_txt = question["options"]["2"]["text"]
    a2_pic = question["options"]["2"]["picture"]
    a3_txt = question["options"]["3"]["text"]
    a3_pic = question["options"]["3"]["picture"]
    a4_txt = question["options"]["4"]["text"]
    a4_pic = question["options"]["4"]["picture"]
    correct = question["answer"]["number"]

    # serves all question data to template
    return render_template("question.html",
                           year=YEAR,
                           total=NUMBER_OF_QUESTIONS,
                           question=quest,
                           question_text=q_text,
                           question_pic=q_pic,
                           answer1_text=a1_txt,
                           answer1_pic=a1_pic,
                           answer2_text=a2_txt,
                           answer2_pic=a2_pic,
                           answer3_text=a3_txt,
                           answer3_pic=a3_pic,
                           answer4_text=a4_txt,
                           answer4_pic=a4_pic,
                           correct_ans=correct,
                           seconds=my_timer,
                           progress=int((quest / NUMBER_OF_QUESTIONS) * 100)
                           )


if __name__ == "__main__":
    app.run(debug=True)

# TODO deploy to the web

# TODO add about page

# TODO missing picture 81.4.jpg

# TODO what if user, uses backpage or forwardpage to navigate?
# TODO BUG if exam times out, then retake, time won't reset or display

# TODO mini-test / full simulation options


# TODO hero video on cover page - tried twice can't get it to autoplay