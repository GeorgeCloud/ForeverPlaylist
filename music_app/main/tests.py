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

    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='playlists')

    title = db.Column(db.String(80), nullable=False)
    video_url = db.Column(db.String(80), nullable=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)

def create_user(username=None):
    # Creates a user with username 'me1' and password of 'password'
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(
        username=username if username else 'me1',
        password=password_hash
    )
    db.session.add(user)
    db.session.commit()

def create_playlist():
    create_user('rocky')
    user = User.query.get(1)

    p1 = Playlist(
        title='Summer 2021',
        description='Underground',
        user_id=user.id,
        user=user
    )
    db.session.add(p1)
    db.session.commit()

    s1 = SongEntry(
        title='A$AP Sundress',
        video_url='Ec3LoKpGJxY',
        playlist_id=p1.id
    )
    db.session.add(s1)
    db.session.commit()

#################################################
# Tests
#################################################

class MainTests(unittest.TestCase):

    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_homepage_logged_out(self):
        """Test that the books show up on the homepage."""
        # Set up
        create_playlist()
        create_user()

        # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that page contains all of the things we expect
        response_text = response.get_data(as_text=True)
        self.assertIn('Welcome To Forever Playlist', response_text)

        playlist = Playlist.query.get(1)
        self.assertIn(playlist.title, response_text)

        self.assertIn('Login', response_text)
        self.assertIn('Signup', response_text)

        self.assertNotIn('Logout', response_text)

    def test_homepage_logged_in(self):
        """Test that the books show up on the homepage."""
        # Set up
        create_playlist()
        create_user()
        login(self.app, 'me1', 'password')

        # # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # # Check that page contains all of the things we expect
        response_text = response.get_data(as_text=True)
        self.assertIn('Logout', response_text)

        self.assertNotIn('Login', response_text)
        self.assertNotIn('Signup', response_text)

    def test_book_detail_logged_in(self):
        """Test that the book appears on its detail page."""
        create_playlist()
        create_user()

        response = self.app.get('/playlists/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        playlist = Playlist.query.get(1)

        response_text = response.get_data(as_text=True)
        self.assertIn(playlist.title, response_text)
        self.assertIn(playlist.songs[0].title, response_text)

    def test_create_playlist(self):
        """Test creating a book."""
        # Set up
        create_playlist()
        create_user()
        login(self.app, 'me1', 'password')

        user = User.query.get(1)
        # Make POST request with data
        post_data = {
            'title': 'Good Music',
            'description': 'Summer 2022',
            'user_id': 1,
            'user': user,
            'songs': []
        }
        self.app.post('/create_playlist', data=post_data)

        # Make sure book was updated as we'd expect
        created_playlist = Playlist.query.filter_by(title='Good Music').one()
        self.assertIsNotNone(created_playlist)
        self.assertEqual(created_playlist.title, 'Good Music')

    def test_create_book_logged_out(self):
        """
        Test that the user is redirected when trying to access the create book
        route if not logged in.
        """
        # Set up
        create_playlist()
        create_user()

        # Make GET request
        response = self.app.get('/create_playlist')

        # Make sure that the user was redirecte to the login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login?next=%2Fcreate_playlist', response.location)

    def test_profile_page(self):
        create_user()
        login(self.app, 'me1', 'password')

        response = self.app.get('/profile/me1')

        user = User.query.get(1)
        response_text = response.get_data(as_text=True)
        self.assertIn(f'Welcome to me1\'s profile', response_text)
