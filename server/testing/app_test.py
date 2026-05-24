import flask
import pytest
from app import app
from models import db, User

app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'

class TestApp:
    '''Flask API in app.py'''

    def test_logs_user_in(self):
        '''logs user in by username and adds user_id to session at /login.'''
        with app.test_client() as client:
            client.get('/clear')

            # FIX: Ensure a user exists in the database memory space before pulling it
            with app.app_context():
                user = User.query.first()
                if not user:
                    user = User(username="testuser")
                    db.session.add(user)
                    db.session.commit()
                    # Refresh the object state
                    db.session.refresh(user)

            response = client.post('/login', json={
                'username': user.username
            })
            response_json = response.get_json()

            assert(response.content_type == 'application/json')
            assert(response.status_code == 200)
            assert(response_json['id'] == user.id)
            assert(response_json['username'] == user.username)
            assert(flask.session.get('user_id') == user.id)

    def test_logs_user_out(self):
        '''removes user_id from session at /logout.'''
        with app.test_client() as client:
            client.get('/clear')

            with app.app_context():
                user = User.query.first()
                if not user:
                    user = User(username="testuser")
                    db.session.add(user)
                    db.session.commit()
                    db.session.refresh(user)

            client.post('/login', json={
                'username': user.username
            })

            response = client.delete('/logout')
            
            assert(response.status_code == 204)
            assert(not response.data)

    def test_checks_session(self):
        '''checks session for user_id at /check_session.'''
        with app.test_client() as client:
            client.get('/clear')

            with app.app_context():
                user = User.query.first()
                if not user:
                    user = User(username="testuser")
                    db.session.add(user)
                    db.session.commit()
                    db.session.refresh(user)

            client.post('/login', json={
                'username': user.username
            })

            logged_in_response = client.get('/check_session')
            logged_in_json = logged_in_response.get_json()

            assert(logged_in_response.content_type == 'application/json')
            assert(logged_in_response.status_code == 200)
            assert(logged_in_json['id'])
            assert(logged_in_json['username'])

            client.delete('/logout')

            logged_out_response = client.get('/check_session')
            logged_out_json = logged_out_response.get_json()

            assert(logged_out_response.status_code == 401)
            assert(logged_out_json == {})

