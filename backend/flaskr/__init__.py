import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET, POST, PATCH, DELETE, OPTIONS")
        return response

    @app.route("/categories")
    def get_categories():
        query = Category.query.all()
        categories = [category.format() for category in query]
        return jsonify({
            "success": True,
            "categories": categories,
            "status": 200
        }), 200

    @app.route("/questions")
    def get_questions():
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * 10
        end = start + 10
        query = Question.query.all()
        categories = [category.format() for category in Category.query.all()]
        questions = [que.format() for que in query]
        return jsonify({
            "success": True,
            "questions": questions[start:end],
            "totalQuestions": len(questions),
            "categories": categories,
            "status": 200
        }), 200

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                "success": True,
                "message": "Successfully delete question"
            }), 200
        except:
            abort(400)

    @app.route("/questions", methods=["POST"])
    def create_question():
        req = request.get_json()
        question = req.get("question")
        answer = req.get("answer")
        difficulty = req.get("difficulty")
        category = req.get("category")
        question = Question(question=question, answer=answer,
                            difficulty=difficulty, category=category)

        try:
            question.insert()
            return jsonify({
                "success": True,
                "message": "A new question has been created",
                "question": question.format()
            }), 200
        except:
            abort(400)

    @app.route("/questions/search", methods=["POST"])
    def search_for_questions():
        questions = [que.format() for que in Question.query.filter(Question.question.ilike(
            '%' + request.get_json().get('searchTerm', '') + '%')).all()]

        return jsonify({
            "questions": questions,
            "totalQuestions": len(questions)
        }), 200

    @app.route("/categories/<int:category_id>/questions")
    def get_questions_on_a_category(category_id):
        query = Question.query.filter(Question.category == category_id)
        questions = [que.format()
                     for que in query]

        return jsonify({
            "questions": questions,

        }), 200

    @app.route("/quizzes", methods=["POST"])
    def play_game():
        res = request.get_json()
        previous_questions = res.get("previous_questions")
        quiz_category = res.get("quiz_category")
        questions = Question.query.filter(
            Question.id.notin_(previous_questions))
        category = quiz_category.get("id")
        if(category == 0):
            question = questions.first()
        else:
            question = questions.filter(
                Question.category == category).first()

        if question:
            question = question.format()

        return jsonify({
            "question": question
        }), 200

    @app.errorhandler(404)
    def not_found():
        return jsonify({
            "success": True,
            "error": 404,
            "message": "Not Found"
        }), 404

    @app.errorhandler(422)
    def unprocesseable_code():
        return jsonify({
            "success": True,
            "error": 422,
            "message": "unprocesseable"
        }), 422

    return app
