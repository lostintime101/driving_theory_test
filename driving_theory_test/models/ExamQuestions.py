import random
import csv
from pathlib import Path


class ExamQuestions:

    def __init__(self, path: str):
        self.questions_bank = {}
        with open(Path(path), 'r', encoding="UTF-8") as question_bank:
            csv_reader = csv.DictReader(question_bank, delimiter=";")
            for rows in csv_reader:
                q_id = int(rows['q_id'])
                self.questions_bank[q_id] = rows

    def get_question_id(self, q_id: int):
        return self.questions_bank.get(q_id, {})

    def get_all_questions_id(self):
        return list(self.questions_bank.keys())

    def create_question_bank(self, q_nb=50):
        questions_available = list(self.questions_bank.keys())
        assert q_nb < len(self.questions_bank)
        random.shuffle(questions_available)
        return questions_available[:q_nb]
