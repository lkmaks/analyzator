from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app.models import User
import string

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')

    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()
        if user is None or not user.check_password(password.data):
            raise ValidationError('Wrong username or password')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        if len(str(username.data)) < 3:
            raise ValidationError('Username is too short')
        if len(str(username.data)) > 10:
            raise ValidationError('Username is too long')

        alpha = string.ascii_letters + string.digits + '_'
        for c in str(username.data):
            if not c in alpha:
                raise ValidationError('Username contains restricted characters')

        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')


    def validate_password(self, password):
        if len(password.data) > 20:
            raise ValidationError('Password is too long (need <= 20 symbols)')
        if len(password.data) < 5:
            raise ValidationError('Password is too short (need >= 5 symbols)')


class KeywordForm(FlaskForm):
    keyword = StringField('keyword', validators=[DataRequired()])

    def validate_keyword(self, keyword):
        if not (0 < len(keyword.data) and len(keyword.data) < 20):
            raise ValidationError('bad length')
        alpha = string.ascii_letters + string.digits + '_-*&'
        for c in str(keyword.data):
            if not c in alpha:
                raise ValidationError('Username contains restricted characters')



