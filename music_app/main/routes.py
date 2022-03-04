"""Import packages and modules."""
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime
from music_app.models import User, Playlist
from music_app.main.forms import *

# Import app and db from events_app package so that we can run app
from music_app.extensions import app, bcrypt, db
from music_app.main.forms import PlaylistForm

main = Blueprint("main", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/', methods=['GET'])
def homepage():
    all_users = User.query.all()
    return render_template('home.html', all_users=all_users)

@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html', user=user)

@main.route('/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    form = PlaylistForm()

    if form.validate_on_submit():
        print('valid')
        new_playlist = Playlist()
        new_playlist.title = form.title.data
        new_playlist.description = form.description.data
        new_playlist.user_id = current_user.id

        db.session.add(new_playlist)
        db.session.commit()

        flash('Playlist was created successfully.')
        return redirect(url_for('main.profile', username=current_user.username))

    return render_template('create_playlist.html', form=form)


@main.route('/playlists/<playlist_id>', methods=['GET', 'POST'])
def show_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)

    return render_template('playlist_show.html', playlist=playlist)
