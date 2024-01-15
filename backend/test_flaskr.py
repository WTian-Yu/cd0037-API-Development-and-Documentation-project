import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question
from settings import TEST_DB_NAME, TEST_DB_USER, TEST_DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = TEST_DB_NAME
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            TEST_DB_USER,
            TEST_DB_PASSWORD,
            "localhost:5432",
            self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "This is a new question",
            'answer': "This is a new anwer",
            'category': 3,
            'difficulty': 5
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # get categories
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    # Can't think about test categories fail in this senario
    # if we use empty table, we can't test the following cases
    # So I write another test script(test_flastkr_empty_table.py) to test it
    # before insert data

    # get questions
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["current_category"], None)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))

    def test_404_if_get_questions_page_invalid(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    # delete delete by id
    def test_delete_question(self):
        res = self.client().delete('/questions/4')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 4).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 4)
        self.assertEqual(question, None)

    def test_404_if_delete_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")

    # get specific category questions
    def test_get_specific_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["current_category"], 1)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])

    def test_404_if_get_specific_category_questions_not_exist(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Processable")

    # create new question
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        create_id = data["created"]

        # check new created question in db is the same as the added question
        question = Question.query.filter(
            Question.id == create_id).one_or_none()
        self.assertTrue(question)
        self.assertEqual(question.question, self.new_question['question'])
        self.assertEqual(question.answer, self.new_question['answer'])
        self.assertEqual(question.category, self.new_question['category'])
        self.assertEqual(question.difficulty, self.new_question['difficulty'])

    def test_400_if_create_new_question_input_invalid(self):
        res = self.client().post("/questions", json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Processable")

    # search questions
    def test_search_questions(self):
        res = self.client().post("/questions", json={"searchTerm": "body"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["current_category"], None)
        self.assertEqual(len(data["questions"]), 1)
        self.assertEqual(data["total_questions"], 1)

    def test_404_if_search_questions_input_empty(self):
        res = self.client().post("/questions", json={"searchTerm": ""})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Not Processable")

    # get quizzes question
    def test_get_quizzes_question(self):
        res = self.client().post("/quizzes",
                                 json={"previous_questions": [1, 4, 20, 15],
                                       'quiz_category': 1})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_400_if_quizzes_question_input_invalid(self):
        res = self.client().post("/quizzes",
                                 json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Bad Request")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
