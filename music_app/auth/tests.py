import os
import unittest
import app

from datetime import date
from music_app.extensions import app, db, bcrypt
from music_app.models import *

"""
Run these tests with the command:
python -m unittest music_app.main.tests
"""

#################################################
# Setup
#################################################

def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def create_books():
    a1 = Author(name='Harper Lee')
    b1 = Book(
        title='To Kill a Mockingbird',
        publish_date=date(1960, 7, 11),
        author=a1
    )
    db.session.add(b1)

    a2 = Author(name='Sylvia Plath')
    b2 = Book(title='The Bell Jar', author=a2)
    db.session.add(b2)
    db.session.commit()

def create_user():
    # Creates a user with username 'me1' and password of 'password'
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='me1', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(unittest.TestCase):

    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        post_data = {
            'username': 'JohnDoe',
            'password': 'password'
        }

        self.app.post('/signup', data=post_data)

        user = User.query.filter_by(username=post_data['username']).first()

        self.assertEqual(user.username, 'JohnDoe')
        self.assertNotEqual(user.username, 'RANDOM_INCORRECT_USERNAME')

    def test_signup_existing_user(self):
        create_user()

        # same username used in above setup function
        new_user = {
            'username': 'me1',
            'password': 'password',
        }
        response = self.app.post('/signup', data=new_user)

        response_text = response.get_data(as_text=True)
        self.assertIn('Username already taken.', response_text)

    def test_login_correct_password(self):
        create_user()

        response = self.app.get('/')
        response_text = response.get_data(as_text=True)
        self.assertIn("Login", response_text)

        account = dict(
            username='me1',
            password='password'
        )

        response = self.app.post('/login', data=account, follow_redirects=True)
        response_text = response.get_data(as_text=True)
        self.assertNotIn("Login", response_text)
        self.assertIn("Logout", response_text)

    def test_login_nonexistent_user(self):
        account = dict(
            username='kf93u093j4',
            password='blahblah'
        )

        response = self.app.post('/login', data=account, follow_redirects=True)
        response_text = response.get_data(as_text=True)
        self.assertIn("Username does not exist", response_text)

    def test_login_incorrect_password(self):
        create_user()

        response = self.app.get('/')
        response_text = response.get_data(as_text=True)
        self.assertIn("Login", response_text)

        account = dict(
            username='me1',
            password='password_391823'  # incorrect password
        )

        response = self.app.post('/login', data=account, follow_redirects=True)
        response_text = response.get_data(as_text=True)

        self.assertIn("Password was incorrect", response_text)

    def test_logout(self):
        create_user()

        account = dict(
            username='me1',
            password='password'
        )

        response = self.app.post('/login', data=account, follow_redirects=True)
        response_text = response.get_data(as_text=True)
        self.assertIn("Logout", response_text)
