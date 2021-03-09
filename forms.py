from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,TextAreaField
from wtforms.validators import ValidationError, InputRequired, Optional, Email, Length
import email_validator
from models import User


def AvailableEmail(form, field):
    email = field.data
    if User.query.filter_by(email_address=email).one_or_none() != None:
        raise ValidationError(
            f'The email address "{email}" is already associated with an account.')


def AvailableUsername(form, field):
    username = field.data
    if User.query.filter_by(username=username).one_or_none() != None:
        raise ValidationError(
            f'The username "{username}" is already associated with an account.')


class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(
        min=6, max=20, message="Must be between 6 and 20 characters."), AvailableUsername])
    password = PasswordField("Password", validators=[InputRequired(), Length(
        min=12, message="Must be at least 12 characters.")])
    email_address = StringField("Email address", validators=[
        InputRequired(), Email(message="Must be in proper email format."), AvailableEmail])
    first_name = StringField("First name", validators=[InputRequired(), Length(
        max=30, message="First name must be between 1 and 30 characters.")])
    last_name = StringField("Last name", validators=[InputRequired(), Length(
        max=30, message="Last name must be between 1 and 30 characters.")])


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), Length(
        max=100, message="Cannot exceed 100 characters.")])
    content = TextAreaField("Content", validators=[InputRequired()])
