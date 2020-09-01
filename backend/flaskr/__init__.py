import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
sys.path.append('../')


QUESTIONS_PER_PAGE = 10


def get_catogires_list():
    formatted_categories = {}
    for category in Category.query.all():
        formatted_categories[category.id] = category.type

    return formatted_categories


def get_questions_list():
    formatted_questions = [question.format()
                           for question
                           in Question.query.order_by(Question.id).all()]
    return formatted_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins.
  Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, DELETE')
        return response

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories', methods=['GET'])
    def get_catogires():
        try:
            return jsonify({
                'success': True,
                'categories': get_catogires_list()
            })
        except:
            abort(422)
    '''

  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the
  bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            questions = get_questions_list()
            current_questions = questions[start:end]

            if len(current_questions) == 0:
                abort(404)

            else:
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(questions),
                    'current_category': None,
                    'categories': get_catogires_list()
                })
        except RuntimeError:
            abort(422)
    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question,
  the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            del_question = Question.query.get(question_id)
            if del_question is None:
                abort(404)
            else:
                del_question.delete()
                return jsonify({
                    'success': True,
                    'deleted_question_id': question_id
                })
        except RuntimeError:
            abort(422)
    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            new_question = Question(
                question=request.get_json()['question'],
                answer=request.get_json()['answer'],
                category=request.get_json()['category'],
                difficulty=request.get_json()['difficulty']
            )
            new_question.insert()
            return jsonify({
                'success': True,
                'message': f'New Question with id {new_question.id} added!!'
            })
        except BaseException:
            abort(422)
    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/search', methods=['POST'])
    def search_questions():
        try:
            search_word = request.get_json()['searchTerm']
            matched_questions = Question.query.filter(
                Question.question.ilike(f'%{search_word}%')).all()

            if len(matched_questions) == 0:
                abort(404)

            format_matched_questions = [
                question.format()for question in matched_questions]
            return jsonify({
                'success': True,
                'questions': format_matched_questions,
                'total_questions': len(format_matched_questions)
            })
        except RuntimeError:
            abort(422)

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def question_by_category(category_id):
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            current_category = Category.query.get(category_id)

            if current_category is None:
                abort(404)

            selected_questions = Question.query.filter(
                                                Question.category ==
                                                category_id).all()
            current_questions = selected_questions[start:end]

            if len(current_questions) == 0:
                abort(404)

            formated_selected_questions = [
                question.format() for question in current_questions]
            return jsonify({
                'success': True,
                'questions': formated_selected_questions,
                'current_category': current_category.type,
                'total_questions': len(selected_questions)
            })
        except RuntimeError:
            abort(422)
    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def quiz_play():
        try:
            category_id = request.get_json()['quiz_category']['id']
            previous_questions = request.get_json()['previous_questions']

            # Check if the ALL is selected or other categories
            if category_id == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(
                                           category=category_id).all()

            # Check if all the questions already asked
            if len(questions) == len(previous_questions):
                quiz_question = {
                    'success': True,
                    'question': None
                }
            else:
                random_index = random.randint(0, len(questions) - 1)

                if len(previous_questions) != 0:
                    while questions[random_index].id in previous_questions:
                        random_index = random.randint(0, len(questions) - 1)

                quiz_question = {
                    'success': True,
                    'question': questions[random_index].format()
                }
            return jsonify(quiz_question)
        except BaseException:
            abort(422)

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not Found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        }), 422

    return app
