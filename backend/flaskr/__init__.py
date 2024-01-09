import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, questions):
    page = request.args.get("page", 1, type=int)
    start = (page-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    all_questions = [q.format() for q in questions]
    current_questions = all_questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    
    # Set up CORS. Allow '*' for origins. Delete the sample route
    CORS(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    
    # Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type, Authorization'
        )
        response.headers.add(
            'Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS'
        )
        return response

    # Endpoint to handle GET requests for all available categories.
    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.all()
        categories = {c.id:c.type for c in categories}
        return jsonify(
            {
                "success": True,
                "categories": categories
            }
        )

    # Endpoint to handle GET requests for questions
    @app.route('/questions')
    def retrieve_questions():
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)
        
        categories = Category.query.all()
        categories = {c.id:c.type for c in categories}
        
        if(len(current_questions)==0):
            abort(404)
        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(questions),
                'categories': categories,
                "current_category": None
            }
        )

    # DELETE question using a question ID.
    @app.route('/questions/<int:question_id>', methods=["DELETE"])
    def delete_question(question_id): 
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if(question is None):
                abort(404)
            question.delete()
            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                }
            )
            
        except:            
            abort(422)
    
    # Endpoint to POST a new question
    # If request body include search term do search
    @app.route("/questions", methods=["POST"])
    def create_or_search_question():
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)
        searchTerm = body.get("searchTerm", None)    

        try:
            if(searchTerm):
                questions = Question.query.order_by(Question.category).filter(
                    Question.question.ilike("%{}%".format(searchTerm))
                ).all()
                paginated_questions = paginate_questions(request, questions)
                return jsonify({'success':True
                            ,'questions':paginated_questions
                            ,'total_questions':len(questions)
                            ,'current_category':None})
            else:
                new_question = Question(
                    question=question,
                    answer=answer,
                    category=category,
                    difficulty=difficulty
                    )
                
                new_question.insert()

                return jsonify(
                    {
                        "success": True,
                        "created": new_question.id,
                    }
                )

        except:
            abort(422)

    # GET endpoint to get questions based on category.
    @app.route("/categories/<int:category_id>/questions")
    def search_specific_category_question(category_id):
        try:
            questions = Question.query.filter(Question.category == category_id).all()
            paginated_questions = paginate_questions(request, questions)            
            return jsonify({'success':True
                        ,'questions':paginated_questions
                        ,'total_questions':len(questions)
                        ,'current_category':category_id})
        except:
            abort(422)

    """
    
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    # POST endpoint to get questions to play the quiz.
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        try:
            response = request.get_json()
            previous_questions = response['previous_questions']
            quiz_category_id = response['quiz_category']
            if quiz_category_id == 0:
                remain_questions = Question.query.filter(~Question.id.in_(previous_questions)).all()
            else:
                remain_questions = Question.query.filter(~Question.id.in_(previous_questions), Question.category==quiz_category_id).all()
            if len(remain_questions) > 0:
                remain_questions = [question.format() for question in remain_questions]
                new_question = random.choice(remain_questions)
            else:
                new_question = None
            return jsonify({'success':True
                            ,'question':new_question})
        except:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    return app

