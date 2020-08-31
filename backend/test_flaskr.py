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
        self.database_path = "postgresql://{}:{}@{}/{}".format('udacity', 'udacity', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        # Define data to be used in testcases
        self.new_correct_question = {
            'question': 'What is the most beautiful country in the world?',
            'answer': 'Egypt',
            'category': 3,
            'difficulty': 2
        }

        self.new_wrong_question = {
            'question': 'What is the most beautiful country in the world?',
            'answer': 'Egypt',
            'category': 3
        }

        self.searchterm_found = {'searchTerm':'Who'}
        
        self.searchterm_unfound = {'searchTerm':'hwo'}

        self.quiz_science = {
            'previous_questions':[],
            'quiz_category':{
                'type': 'Science',
                'id': 1
            }
        }

        self.quiz_wrong_format = {
            'previous':[],
            'quiz_category':{
                'type': 'Science',
                'id': 1
            }
        }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    def test_get_questions(self):
        """ Successful test to get questions """
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    
    def test_get_questions_with_unavailable_page_number(self):
        """ Error test to get questions with unavailable page number """
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'Resource not Found')
    
    
    def test_delete_existing_question(self):
        """ Successful test to delete existing questions """
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_question_id'], 2)
    
    
    def test_delete_non_existing_question(self):
        """ Error test to delete non existing questions """
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not Found')
    
     
    def test_create_new_question(self):
        """ Successful test to create new questions """
        res = self.client().post('/questions', json=self.new_correct_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['message'])

    def test_create_new_wrong_question(self):
        """ Error test to create new questions with wrong format """
        res = self.client().post('/questions', json=self.new_wrong_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'Unprocessable Entity')

    def test_search_with_available_word(self):
        """ Successful test to search with a word that return questions """
        res = self.client().post('/search', json=self.searchterm_found)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    def test_search_with_unavailable_word(self):
        """ Error test to search with a word that not return questions """
        res = self.client().post('/search', json=self.searchterm_unfound)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not Found')

    def test_get_questions_with_category(self):
        """ Successful test to get questions with specific category """
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']))

    def test_get_questions_with_unavailable_category(self):
        """ Error test to get questions with unavailable category """
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not Found')

    def test_get_questions_with_category_unavailable_page_number(self):
        """ Error test to get questions with available category but with wrong page number"""
        res = self.client().get('/categories/1/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not Found')

    def test_quiz(self):
        """ Successful test to play a quiz"""
        res = self.client().post('/quizzes', json=self.quiz_science)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
    
    def test_quiz_wrong_request_format(self):
        """ Error test to play a quiz with wrong format """
        res = self.client().post('/quizzes', json=self.quiz_wrong_format)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'Unprocessable Entity')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()