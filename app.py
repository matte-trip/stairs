from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

import uuid

from flask_bootstrap import Bootstrap

# Create the application object
app = Flask(__name__)

# from flask_bootstrap import Bootstrap
#
#
# # unused probably
bootstrap = Bootstrap(app)
#
# # used to secure connection client-side
app.config['SECRET_KEY'] = 'my secret key'
#
# # position of database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
# creation of database with SQLAlchemy
db = SQLAlchemy(app)

# login manager initializing
login_manager = LoginManager(app)
# this is the login view users will be redirected to if they are not logged in and they try to access a private page
login_manager.login_view = 'login_registration'


# GONNA HAVE TO USE THIS???
# user_manager = UserManager(app, db, User)


# =========================================== MODELS ===========================================


# Define User data-model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # User Id field
    user_id = db.Column('user_id', db.String(8), nullable=False)

    # User Authentication fields
    email = db.Column('email', db.String(255), primary_key=True, nullable=False, unique=True)
    password_hash = db.Column('password', db.String(255), nullable=False)

    # User fields
    first_name = db.Column('first_name', db.String(50), nullable=False)
    last_name = db.Column('last_name', db.String(50), nullable=False)

    # Bio fields
    age = db.Column('age', db.Integer)
    university = db.Column('university', db.String(50), nullable=False)
    bio = db.Column('bio', db.String(140), nullable=False)
    interests = db.Column('interests', db.String(140), nullable=False)

    def get_id(self):
        return self.email

    @property
    def password(self):
        raise StandardError('Password is write-only')

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# =========================================== FORMS ===========================================

class LoginForm(FlaskForm):
    login_email = StringField('Email', validators=[DataRequired()])
    login_password = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Login')

    @staticmethod
    def validate_username(email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email does not exist')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    register = SubmitField('Register')

    @staticmethod
    def validate_username(email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email does not exist')


class EditProfileForm(FlaskForm):
    email = StringField('Email')
    first_name = StringField('First name')
    last_name = StringField('Last name')
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[EqualTo('password')])
    submit = SubmitField('Submit')


class EditBioForm(FlaskForm):
    age = IntegerField('Age')
    university = StringField('University')
    bio = TextAreaField('Bio')
    interests = TextAreaField('Interests')
    save = SubmitField('Save')


# =========================================== VIEWS ===========================================

# This is needed by LoginManager to retrieve a User instance based on its ID (email)
@login_manager.user_loader
def get_user(email):
    return User.query.filter_by(email=email).first()


# @login_manager.user_loader
# def get_id(email):
#     return User.query.filter_by(user_id=email).first()


@app.before_first_request
def setup_db():
    db.create_all()


# Use decorators to link the function to a url
@app.route('/')
def home():
    return render_template('homepage.html')


@app.route('/login_registration', methods=['GET', 'POST'])
def login_registration():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        # we are certain user exists because of the username validator of LoginForm
        existing_user = get_user(login_form.login_email.data)
        if existing_user.check_password(login_form.login_password.data):
            # login the user, then redirect to his user page
            login_user(existing_user)
            return redirect(url_for('personal_page'))

    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        new_user = User()
        new_user.email = registration_form.email.data
        new_user.first_name = registration_form.first_name.data
        new_user.last_name = registration_form.last_name.data
        new_user.password = registration_form.password.data
        new_user.user_id = uuid.uuid4().hex[::4].capitalize()
        # add new user to db
        db.session.add(new_user)
        # commit changes to db
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('personal_page'))

    return render_template('login_registration.html', login_form=login_form, registration_form=registration_form)


@app.route('/user', methods=['GET', 'POST'])
@login_required
def personal_page():
    personal_profile_form = EditProfileForm()
    bio_form = EditBioForm()
    if personal_profile_form.validate_on_submit():
        if current_user.check_password(personal_profile_form.password.data):
            current_user.email = personal_profile_form.email.data
            current_user.first_name = personal_profile_form.first_name.data
            current_user.last_name = personal_profile_form.last_name.data
            current_user.password = personal_profile_form.password.data
            db.session.commit()
            return redirect(url_for('personal_page'))
    elif request.method == 'GET':
        personal_profile_form.email.data = current_user.email
        personal_profile_form.first_name.data = current_user.first_name
        personal_profile_form.last_name.data = current_user.last_name
        bio_form.age.data = current_user.age
        bio_form.university.data = current_user.university
        bio_form.bio.data = current_user.bio
        bio_form.interests.data = current_user.interests
    if bio_form.validate_on_submit():
        current_user.age = bio_form.age.data
        current_user.university = bio_form.university.data
        current_user.bio = bio_form.bio.data
        current_user.interests = bio_form.interests.data
        db.session.commit()
        return redirect(url_for('personal_page'))
    return render_template('personal_page.html', personal_profile_form=personal_profile_form, bio_form=bio_form)


@app.route('/u/<user_id>')
def u(user_id):
    user = User.query.filter_by(user_id=user_id.capitalize()).first()
    return render_template('newprofile.html', user=user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# Start the server with run() method
if __name__ == '__main__':
    app.run(debug=True)
