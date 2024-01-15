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

    # get categories fail
    def test_fail_if_get_categories_empty(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Resource Not Found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
