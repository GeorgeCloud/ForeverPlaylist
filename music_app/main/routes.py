"""Import packages and modules."""
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime
from music_app.models import User, Playlist, SongEntry
from music_app.main.forms import *

# Import app and db from events_app package so that we can run app
from music_app.extensions import app, bcrypt, db
from music_app.main.forms import PlaylistForm, SongEntryForm

main = Blueprint("main", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/', methods=['GET'])
def homepage():
    all_users = User.query.all()
    all_playlists = Playlist.query.all()
    return render_template('home.html', all_users=all_users, playlists=all_playlists)
    # return render_template('home.html')

@main.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    return render_template('profile.html', user=user)

@main.route('/create_playlist', methods=['GET', 'POST'])
@login_required
def create_playlist():
    form = PlaylistForm()

    if form.validate_on_submit():
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
    form = SongEntryForm()

    # if request.method == 'GET':
    #     return render_template('playlist_show.html', playlist=playlist, form)

    if form.validate_on_submit():
        song_entry = SongEntry()
        song_entry.title = form.title.data

        song_entry.video_url = form.video_url.data
        song_entry.playlist_id = playlist_id

        db.session.add(song_entry)
        db.session.commit()
        return redirect(request.referrer)

    return render_template('playlist_show.html', playlist=playlist, form=form)
