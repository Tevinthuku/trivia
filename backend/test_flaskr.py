import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def createQuestion(self):
        question = {
            "category": 1,
            "question": "How",
            "answer": "Now",
            "difficulty": 1
        }
        return self.client().post("/questions", data=json.dumps(question),
                                  content_type="application/json")

    def getNumberOfQuestions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        return data.get("totalQuestions")

    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["categories"]), 6)

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(data["status"], 200)
        self.assertEqual(len(data["questions"]), 10)

    def test_delete_specific_question(self):
        res = self.createQuestion()
        data = json.loads(res.data)
        question = data.get("question")
        question_id = question.get("id")
        original_number_of_questions = self.getNumberOfQuestions()
        res = self.client().delete(f'/questions/{question_id}')
        self.assertEqual(res.status_code, 200)
        number_of_questions = self.getNumberOfQuestions()
        self.assertEqual(number_of_questions, (original_number_of_questions-1))

    def test_delete_nonexistent_question(self):
        res = self.client().delete("/questions/10000")
        self.assertEqual(res.status_code, 400)

    def test_question_creation(self):
        original_number_of_questions = self.getNumberOfQuestions()
        res = self.createQuestion()
        new_number_of_questions = self.getNumberOfQuestions()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(new_number_of_questions,
                         (original_number_of_questions+1))

    def test_question_creation_with_failure(self):
        question = {
            "question": "How",
            "difficulty": 1
        }
        res = self.client().post("/questions", data=json.dumps(question),
                                 content_type="application/json")

        self.assertEqual(res.status_code, 400)

    def test_questions_on_a_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)
        self.assertTrue(len(data["questions"]))

    def test_failure_on_questions_on_a_category_that_doesnt_exist(self):
        res = self.client().get("/categories/999/questions")
        data = json.loads(res.data)
        self.assertFalse(len(data["questions"]))

    def test_search(self):
        self.createQuestion()
        term = {
            "searchTerm": "How"
        }
        res = self.client().post("/questions/search", data=json.dumps(term),
                                 content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(len(data.get("questions")))

    def test_no_search_results(self):
        term = {
            "searchTerm": "HakunaMatata"
        }
        res = self.client().post("/questions/search", data=json.dumps(term),
                                 content_type="application/json")
        data = json.loads(res.data)
        self.assertEqual(len(data.get("questions")), 0)

    def test_play_game_successfully(self):
        req = {
            "previous_questions": [],
            "quiz_category": {
                "id": 4
            }
        }
        res = self.client().post("/quizzes", data=json.dumps(req),
                                 content_type="application/json")
        data = json.loads(res.data)
        self.assertTrue(len(data["question"]))

    def test_end_of_game(self):
        data = {
            # to make sure I exhaust all questions
            "previous_questions": list(range(1, 1000)),
            "quiz_category": {
                "id": 0
            }
        }
        res = self.client().post("/quizzes", data=json.dumps(data),
                                 content_type="application/json")
        data = json.loads(res.data)
        self.assertFalse((data["question"]))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
