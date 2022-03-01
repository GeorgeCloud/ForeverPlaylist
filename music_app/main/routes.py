"""Import packages and modules."""
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from datetime import date, datetime
from music_app.models import User
from music_app.main.forms import *

# Import app and db from events_app package so that we can run app
from music_app.extensions import app, bcrypt, db

main = Blueprint("main", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/')
def homepage():
    all_users = User.query.all()
    return render_template('home.html', all_users=all_users)
