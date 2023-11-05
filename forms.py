from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField, RadioField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from models import User, TriviaPack, Question

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class TriviaPackForm(FlaskForm):
    title = SelectField('Category', choices=[
        ('entertainment', 'Entertainment'),
        ('art', 'Art'),
        ('science', 'Science'),
        ('sport', 'Sport'),
        ('geography', 'Geography'),
        ('history', 'History'),
        ('custom', 'Custom')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Create')

class TriviaQuestionForm(FlaskForm):
    content = TextAreaField('Question Content', validators=[DataRequired()])
    correct_answer = StringField('Correct Answer', validators=[DataRequired()])
    incorrect_answer1 = StringField('Incorrect Answer 1', validators=[DataRequired()])
    incorrect_answer2 = StringField('Incorrect Answer 2', validators=[DataRequired()])
    incorrect_answer3 = StringField('Incorrect Answer 3', validators=[DataRequired()])
    add_more_questions = BooleanField('Add more questions after this one')
    submit = SubmitField('Add Question')

class AnswerForm(FlaskForm):
    answer = RadioField('Choices', validators=[DataRequired()])
    submit = SubmitField('Submit Answer')

