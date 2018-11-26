from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
import uuid
import os
import shutil

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'secret_key'

app.config[
    'UPLOAD_FOLDER'] = 'C:\Users\Matteo\Desktop\Drive\Information Systems\Project - Information Systems\stairs\uploads'
app.config[
    'STATIC_FOLDER'] = 'C:\Users\Matteo\Desktop\Drive\Information Systems\Project - Information Systems\stairs\static'

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['available_cities'] = [("TURIN", "Turin")]

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
# Users not logged in who try to access a private page will be redirected to this view
login_manager.login_view = 'login_registration'


# =========================================== MODELS ===========================================

# Define User data-model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    # User Id field
    user_id = db.Column('user_id', db.String(8), nullable=False)

    # User Authentication fields
    email = db.Column('email', db.String(50), primary_key=True, nullable=False, unique=True)
    password_hash = db.Column('password', db.String(50), nullable=False)

    # User fields
    first_name = db.Column('first_name', db.String(50), nullable=False)
    last_name = db.Column('last_name', db.String(50), nullable=False)
    city = db.Column('city', db.String(30), nullable=False)

    # Bio fields
    age = db.Column('age', db.Integer)
    study_field = db.Column('study_field', db.String(50), nullable=False)
    university = db.Column('university', db.String(50), nullable=False)
    bio = db.Column('bio', db.String(140), nullable=False)
    interests = db.Column('interests', db.String(140), nullable=False)

    # Other fields
    photo_id = db.Column('photo_id', db.Integer)

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

    def print_user(self):
        print "Email: " + self.email + " ID: " + self.user_id


# =========================================== FORMS ===========================================

class LoginForm(FlaskForm):
    login_email = StringField('Email', validators=[DataRequired()])
    login_password = PasswordField('Password', validators=[DataRequired()])
    login_button = SubmitField('Login')

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
    city = SelectField('City', choices=app.config['available_cities'], validators=[DataRequired()])
    registration_button = SubmitField('Register')

    @staticmethod
    def validate_username(email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email does not exist')


class EditPrivateDataForm(FlaskForm):
    email = StringField('Email')
    first_name = StringField('First name')
    last_name = StringField('Last name')
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[EqualTo('password')])
    city = SelectField('City', choices=app.config['available_cities'], validators=[DataRequired()])
    submit_button = SubmitField('Submit')


class EditPublicDataForm(FlaskForm):
    age = IntegerField('Age')
    study_field = StringField('Study Field')
    university = StringField('University')
    bio = TextAreaField('Bio')
    interests = TextAreaField('Interests')
    save_button = SubmitField('Save')


# =========================================== VIEWS ===========================================

@login_manager.user_loader
def get_user(email):
    return User.query.filter_by(email=email).first()


@app.before_first_request
def setup_db():
    db.create_all()


@app.route('/')
def home():
    global errors_in_login_registration
    errors_in_login_registration = 0
    return render_template('homepage.html')


@app.route('/login_registration', methods=['GET', 'POST'])
def login_registration():
    global errors_in_login_registration
    login_form = LoginForm()
    if login_form.validate_on_submit():
        # User existence check by login_manager.user_loader
        existing_user = get_user(login_form.login_email.data)
        if existing_user:
            if existing_user.check_password(login_form.login_password.data):
                login_user(existing_user)
                return redirect(url_for('personal_page'))
            else:
                errors_in_login_registration = 1
                return redirect(url_for('login_registration'))
        else:
            errors_in_login_registration = 1
            return redirect(url_for('login_registration'))

    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        e_user = get_user(registration_form.email.data)
        if e_user:
            errors_in_login_registration = 2
            return redirect(url_for('login_registration'))
        else:
            new_user = User()
            new_user.email = registration_form.email.data
            new_user.first_name = registration_form.first_name.data
            new_user.last_name = registration_form.last_name.data
            new_user.password = registration_form.password.data
            new_user.user_id = uuid.uuid4().hex[::4].capitalize()
            new_user.city = registration_form.city.data
            new_user.photo_id = 0
            destination_path = new_user.user_id + str(new_user.photo_id) + ".png"
            shutil.copy(os.path.join(app.config['STATIC_FOLDER'], 'user-icon.png'),
                        os.path.join(app.config['UPLOAD_FOLDER'], destination_path))
            # Add new user to db
            db.session.add(new_user)
            # Commit changes to db
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('personal_page'))
    print errors_in_login_registration
    return render_template('login_registration.html', login_form=login_form, registration_form=registration_form,
                           error=errors_in_login_registration)


@app.route('/user', methods=['GET', 'POST'])
@login_required
def personal_page():
    personal_profile_form = EditPrivateDataForm()
    bio_form = EditPublicDataForm()
    image_name = current_user.user_id + str(current_user.photo_id) + ".png"
    if personal_profile_form.validate_on_submit():
        if current_user.check_password(personal_profile_form.password.data):
            current_user.email = personal_profile_form.email.data
            current_user.first_name = personal_profile_form.first_name.data
            current_user.last_name = personal_profile_form.last_name.data
            current_user.password = personal_profile_form.password.data
            current_user.city = personal_profile_form.city.data
            db.session.commit()
            return redirect(url_for('personal_page'))
    elif bio_form.validate_on_submit():
        current_user.age = bio_form.age.data
        current_user.study_field = bio_form.study_field.data
        current_user.university = bio_form.university.data
        current_user.bio = bio_form.bio.data
        current_user.interests = bio_form.interests.data
        db.session.commit()
        return redirect(url_for('personal_page'))
    elif request.method == 'GET':
        personal_profile_form.email.data = current_user.email
        personal_profile_form.first_name.data = current_user.first_name
        personal_profile_form.last_name.data = current_user.last_name
        personal_profile_form.city = current_user.city
        bio_form.age.data = current_user.age
        bio_form.study_field.data = current_user.study_field
        bio_form.university.data = current_user.university
        bio_form.bio.data = current_user.bio
        bio_form.interests.data = current_user.interests
    return render_template('personal_page.html', personal_profile_form=personal_profile_form, bio_form=bio_form,
                           image_name=image_name)


@app.route('/uploads/<filename>')
def send_image(filename):
    return send_from_directory("uploads", filename)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print 'No file part'
            return redirect(request.url)
        profile_picture = request.files['file']
        # if user does not select file, browser also submit an empty part without filename
        if profile_picture.filename == '':
            print 'No selected file'
            return redirect(request.url)
        if profile_picture:
            current_user.photo_id += 1
            db.session.commit()
            filename = current_user.user_id + str(current_user.photo_id) + ".png"
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('personal_page'))
    return render_template('upload.html')


@app.route('/u/<user_id>')
def u(user_id):
    user = User.query.filter_by(user_id=user_id.capitalize()).first_or_404()
    return render_template('newprofile.html', user=user,
                           image_name=current_user.user_id + str(current_user.photo_id) + ".png")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(e):
    print e
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    print e
    return render_template('500.html'), 500


# ======================================= USEFUL VARIABLES ====================================

errors_in_login_registration = 0
# 1 is wrong email/password in login
# 2 is user already registered in registration


# ========================================== START SCRIPT =====================================

# Start the server with run() method
if __name__ == '__main__':
    app.run(debug=True)
