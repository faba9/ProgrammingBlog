from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (StringField, PasswordField,
 ValidationError, SubmitField, TextAreaField, IntegerField)
from wtforms.validators import DataRequired, Length, Email

class Myform(FlaskForm):
    password = PasswordField(label='Password',
     validators=[DataRequired(), Length(min=5)])
    email = StringField(label='Email', validators=[DataRequired()])
    my_recapcha = RecaptchaField()
    submit = SubmitField('Login')

class Addform(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    content = TextAreaField(label='Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Delform(FlaskForm):
    number = IntegerField(label='Number of post', validators=[DataRequired()])
    submit = SubmitField('Submit')

class Regform(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    password = PasswordField(label='Password',
     validators=[DataRequired(), Length(min=5)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    my_recapcha = RecaptchaField()
    submit = SubmitField('Registration')
