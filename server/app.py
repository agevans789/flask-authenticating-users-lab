#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User, ArticlesSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Login(Resource):
    def post(self):
        # 1. Extract username from JSON request body
        data = request.get_json()
        username = data.get('username')
        
        # 2. Query database for user
        user = User.query.filter_by(username=username).first()
        
        if user:
            # 3. Save user_id to session and return user info
            session['user_id'] = user.id
            return make_response(jsonify(UserSchema().dump(user)), 200)
            
        return make_response(jsonify({'error': 'Unauthorized'}), 401)


class Logout(Resource):
    def delete(self):
        # 1. Clear out the authenticated user's ID
        session.pop('user_id', None)
        
        # 2. Return an empty body with a 204 No Content status
        return make_response('', 204)


class CheckSession(Resource):
    def get(self):
        # 1. Identify user using current active session cookie
        user_id = session.get('user_id')
        
        if user_id:
            user = User.query.filter_by(id=user_id).first()
            if user:
                return make_response(jsonify(UserSchema().dump(user)), 200)
                
        # 2. Return 401 if nobody is currently validated
        return make_response(jsonify({'error': 'Unauthorized'}), 401)


class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [ArticlesSchema().dump(article) for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = ArticlesSchema.dump(article)

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')

api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
