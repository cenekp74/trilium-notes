from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, DateField, IntegerField,
    FieldList, FormField, SubmitField,
    PasswordField, BooleanField
)
from wtforms.validators import DataRequired, Optional, NumberRange


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')