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
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
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


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

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


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

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

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
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
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
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
'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

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