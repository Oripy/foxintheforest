"""WTF forms definition for Register and Login pages"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_babel import lazy_gettext as _l

from foxy.models import User

class RegistrationForm(FlaskForm):
    """Registration Form:
        username: Unique username
        password: hashed password
        confirm_password: should be the same as password
    """
    username = StringField(_l('Username'),
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    confirm_password = PasswordField(_l('Confirm Password'),
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Sign Up'))

    def validate_username(self, username):
        """Function to check the unicity of the username"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_l('Username already exists.'))

class LoginForm(FlaskForm):
    """Registration Form:
        username: Unique username
        password: hashed password
        remember: checkmark to stay logged-in
    """
    username = StringField(_l('Username'),
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Login'))
