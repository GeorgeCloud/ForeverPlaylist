from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from wtforms.validators import DataRequired, Length, ValidationError
from music_app.models import User

class PlaylistForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Create Playlist')


class SongEntryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    video_url = StringField('Video URL', validators=[DataRequired()])
    submit = SubmitField('Add Song')
