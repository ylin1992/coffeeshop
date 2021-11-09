import os
from re import T
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from sqlalchemy.sql.base import _DialectArgView

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
    except Exception as e:
        print(e)
        abort(500)
    if drinks is None or len(drinks) == 0:
        abort(404)
    
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })



@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    '''
        @TODO: add permissions
    '''
    try:
        drinks = Drink.query.all()
    except Exception as e:
        print(e)
        abort(500)
    if drinks is None or len(drinks) == 0:
        abort(404)
    
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })



@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(jwt):
    '''
        recipe is in the form of str( '[{...},{...}]')
        @TODO: add permissions
    '''
    para = request.get_json()
    print(request.get_json())
    if para is None:
        abort(400)
    title = para['title'] if 'title' in para else None
    recipe = json.dumps(para['recipe']) if 'recipe' in para else None
    print("title: ", title)
    print("recipe: ", recipe)
    if title is None or recipe is None:
        abort(400)

    try:
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
    except Exception as e:
        print(e)
        abort(422)
    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinkby_id(jwt, drink_id):
    '''
        @TODO: add permissions
    '''
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    print(drink.long())

    data = request.get_json()
    print(data)
    if ('title' not in data and 'recipe' not in data):
        abort(400)
    try:
        for k in data:
            if k == 'title':
                drink.title = data[k]
            elif k == 'recipe':
                drink.recipe = json.dumps(data[k])
        drink.update()
    except Exception as e:
        print(e)
        abort(400)
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)
    print(drink.long())
    try:
        drink.delete()
    except Exception as e:
        print(e)
        abort(500)
    return jsonify({
        "success": True,
        "delete": drink_id
    })

# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Resource not found'
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal error'
    }), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401

@app.errorhandler(AuthError)
def process_AuthError(error):
    res = jsonify(error.error)
    res.status_code = error.status_code

    return res