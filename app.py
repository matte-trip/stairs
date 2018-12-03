from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DecimalRangeField
from wtforms import StringField, IntegerField, SubmitField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
import uuid
import os
import shutil

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'C0fUTr5*iB5o&uWi-r@&'

app.config[
    'UPLOAD_FOLDER'] = 'C:\Users\Matteo\Desktop\Drive\Information Systems\Housr - Information Systems\stairs\uploads'
app.config[
    'STATIC_FOLDER'] = 'C:\Users\Matteo\Desktop\Drive\Information Systems\Housr - Information Systems\stairs\static'

app.config['available_cities'] = [("TURIN", "Turin")]
app.config['boolean_choice'] = [("NO", "No"), ("YES", "Yes")]

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
# Users not logged in who try to access a private page will be redirected to this view
login_manager.login_view = 'login_registration'


# ======================================================================================================================
# MODELS
# ======================================================================================================================

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
    study_field = db.Column('study_field', db.String(50))
    university = db.Column('university', db.String(50))
    bio = db.Column('bio', db.String(140))
    interests = db.Column('interests', db.String(140))
    languages = db.Column('languages', db.String(50))

    # Habits
    habits = db.Column('habits', db.String(8))

    # Other fields
    photo_id = db.Column('photo_id', db.Integer)
    phone_number = db.Column('phone_number', db.String(10))

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


class Residence(db.Model):
    __tablename__ = 'houses'

    # Id field
    houses_id = db.Column('houses_id', db.String(8), primary_key=True, unique=True, nullable=False)

    city = db.Column('city', db.String(30), nullable=False)
    street = db.Column('street', db.String(50), nullable=False)
    civic = db.Column('civic', db.Integer)
    neighbourhood = db.Column('neighbourhood', db.String(50), nullable=False)  # SELECTOR OR NOT????????????????????????
    amenities = db.Column('amenities', db.String(8))  # NULLABLE OR NOT?????????????????????????????????????????????????
    description = db.Column('description', db.String(1000), nullable=False)
    house_rules = db.Column('house rules', db.String(1000), nullable=False)


# ======================================================================================================================
# FORMS
# ======================================================================================================================

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
    city = SelectField('City', choices=app.config['available_cities'], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    registration_button = SubmitField('Register')

    @staticmethod
    def validate_username(email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email does not exist')


class EditPrivateDataForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    city = SelectField('City', choices=app.config['available_cities'], validators=[DataRequired()])
    phone_number = StringField('Phone Number')
    password = PasswordField('Password Verification', validators=[DataRequired()])
    submit_button = SubmitField('Submit')


class EditPublicDataForm(FlaskForm):
    age = IntegerField('Age')
    study_field = StringField('Study Field')
    university = StringField('University')
    bio = TextAreaField('Bio')
    interests = TextAreaField('Interests')
    languages = TextAreaField('languages')
    save_button = SubmitField('Save')


class EditSlidersDataForm(FlaskForm):
    # yes or no
    smoking_habits = DecimalRangeField('Do You Smoke?')
    past_experience = DecimalRangeField('Do you have past experience of housesharing?')
    do_sports = DecimalRangeField('Do you practice sports?')
    pet_friendly = DecimalRangeField('Are you pet friendly?')
    # how much do you like ...
    eat_together = DecimalRangeField('Consume meals with housemates')
    ideal_week_end1 = DecimalRangeField('Stay at home and chill')
    ideal_week_end2 = DecimalRangeField('Hangout with friends')
    house_parties = DecimalRangeField('House parties')
    # i'm used to
    invite_friends = DecimalRangeField('Invite friends at home')
    overnight_guests = DecimalRangeField('Have overnight guests')
    play_music = DecimalRangeField('Play music without headphones')
    time_at_home = DecimalRangeField('Spend most of my time at home')
    save_habits = SubmitField('Save')
# ======================================================================================================================
# VIEWS
# ======================================================================================================================

@login_manager.user_loader
def get_user(email):
    return User.query.filter_by(email=email).first()


@app.before_first_request
def setup_db():
    db.create_all()


@app.route('/')
def home():
    # a. Keeps track of user position and shows his pro_pic
    global last_url
    last_url = ''

    if current_user.is_authenticated:
        pro_pic = current_user.user_id + str(current_user.photo_id) + ".png"
    else:
        pro_pic = ""
    # a_end

    global errors_in_login_registration
    errors_in_login_registration = 0

    return render_template('homepage.html',
                           is_auth=current_user.is_authenticated,
                           pro_pic=pro_pic)


@app.route('/login_registration', methods=['GET', 'POST'])
def login_registration():
    # b. Sends away the user if he tries to come to login/register once already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # b_end

    global errors_in_login_registration

    login_form = LoginForm()
    if login_form.validate_on_submit():
        existing_user = get_user(login_form.login_email.data)
        if existing_user:
            if existing_user.check_password(login_form.login_password.data):
                login_user(existing_user)
                return redirect("http://127.0.0.1:5000/" + last_url)
            else:
                errors_in_login_registration = 1
                return redirect(url_for('login_registration'))
        else:
            errors_in_login_registration = 1
            return redirect(url_for('login_registration'))

    registration_form = RegistrationForm()
    if registration_form.password.data != registration_form.password2.data:
        errors_in_login_registration = 3
        return redirect(url_for('login_registration'))
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
            new_user.city = registration_form.city.data
            new_user.password = registration_form.password.data
            new_user.user_id = uuid.uuid4().hex[::4].capitalize()
            new_user.photo_id = 0
            new_user.habits = "0000000000"
            default_image_destination_path = new_user.user_id + "0.png"
            shutil.copy(os.path.join(app.config['STATIC_FOLDER'], 'user-default.png'),
                        os.path.join(app.config['UPLOAD_FOLDER'], default_image_destination_path))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect("http://127.0.0.1:5000/" + last_url)

    return render_template('login_registration.html',
                           login_form=login_form,
                           registration_form=registration_form,
                           error=errors_in_login_registration)


@app.route('/user', methods=['GET', 'POST'])
@login_required
def personal_page():
    global errors_in_private_page
    global show_wrong_password_box

    personal_profile_form = EditPrivateDataForm()
    bio_form = EditPublicDataForm()
    if personal_profile_form.validate_on_submit():
        if current_user.check_password(personal_profile_form.password.data):
            current_user.email = personal_profile_form.email.data
            current_user.first_name = personal_profile_form.first_name.data
            current_user.last_name = personal_profile_form.last_name.data
            current_user.city = personal_profile_form.city.data
            current_user.phone_number = personal_profile_form.phone_number.data
            db.session.commit()
            return redirect(url_for('personal_page'))
        else:
            errors_in_private_page = 1
            redirect(url_for('personal_page'))
    elif bio_form.validate_on_submit():
        current_user.age = bio_form.age.data
        current_user.study_field = bio_form.study_field.data
        current_user.university = bio_form.university.data
        current_user.bio = bio_form.bio.data
        current_user.interests = bio_form.interests.data
        current_user.languages = bio_form.languages.data
        db.session.commit()
        return redirect(url_for('personal_page'))

    habits_form = EditSlidersDataForm()
    if request.method == 'GET' or errors_in_private_page:
        show_wrong_password_box = 0
        if errors_in_private_page:
            show_wrong_password_box = 1
        errors_in_private_page = 0

        personal_profile_form.email.data = current_user.email
        personal_profile_form.first_name.data = current_user.first_name
        personal_profile_form.last_name.data = current_user.last_name
        personal_profile_form.city = current_user.city
        personal_profile_form.phone_number = current_user.phone_number

        bio_form.age.data = current_user.age
        bio_form.study_field.data = current_user.study_field
        bio_form.university.data = current_user.university
        bio_form.bio.data = current_user.bio
        bio_form.interests.data = current_user.interests
        bio_form.languages.data = current_user.languages

    image_name = current_user.user_id + str(current_user.photo_id) + ".png"

    return render_template('private_profile.html',
                           personal_profile_form=personal_profile_form,
                           bio_form=bio_form,
                           image_name=image_name,
                           error=show_wrong_password_box,
                           habits_form=habits_form)


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
        # check if user has selected file
        if profile_picture.filename == '':
            print 'No selected file'
            return redirect(request.url)
        if profile_picture:
            current_user.photo_id += 1
            db.session.commit()
            filename = current_user.user_id + str(current_user.photo_id) + ".png"
            # saving new image to /uploads
            profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # deleting old image associated to the user
            filename = current_user.user_id + str(current_user.photo_id - 1) + ".png"
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('personal_page'))

    return render_template('upload.html')


@app.route('/habits', methods=['GET', 'POST'])
@login_required
def habits():
    habits_form = EditSlidersDataForm()
    if request.method == 'POST':
        habits_list = [str(habits_form.smoking_habits.data), str(habits_form.past_experience.data),
                       str(habits_form.eat_together.data), str(habits_form.do_sports.data),
                       str(habits_form.house_parties.data), str(habits_form.invite_friends.data),
                       str(habits_form.overnight_guests.data), str(habits_form.play_music.data),
                       str(habits_form.ideal_week_end1.data), str(habits_form.pet_friendly.data),
                       str(habits_form.ideal_week_end2.data), str(habits_form.time_at_home.data)]
        current_user.habits = "".join(habits_list)
        db.session.commit()
        return redirect(url_for('personal_page'))

    return render_template('habits.html',
                           habits_form=habits_form)


@app.route('/u/<user_id>')
def u(user_id):
    # a. Keeps track of user position and shows his pro_pic
    global last_url
    last_url = "u/" + user_id

    if current_user.is_authenticated:
        pro_pic = current_user.user_id + str(current_user.photo_id) + ".png"
    else:
        pro_pic = ""
    # a_end

    user = User.query.filter_by(user_id=user_id.capitalize()).first_or_404()
    user_image_name = user.user_id + str(user.photo_id) + ".png"

    habits_form = EditSlidersDataForm()

    return render_template('public_profile.html',
                           user=user,
                           image_name=user_image_name,
                           is_auth=current_user.is_authenticated,
                           pro_pic=pro_pic,
                           habits_form=habits_form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("http://127.0.0.1:5000/" + last_url)


@app.errorhandler(404)
def page_not_found(e):
    print e
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    print e
    return render_template('500.html'), 500


# @app.route('/results')
# def search_results(search):
#     results = []
#     search_string = search.data['search']
#     if search_string:
#         if search.data['select'] == 'Artist':
#             qry = db_session.query(Album, Artist).filter(
#                 Artist.id==Album.artist_id).filter(
#                     Artist.name.contains(search_string))
#             results = [item[0] for item in qry.all()]
#         elif search.data['select'] == 'Album':
#             qry = db_session.query(Album).filter(
#                 Album.title.contains(search_string))
#             results = qry.all()
#         elif search.data['select'] == 'Publisher':
#             qry = db_session.query(Album).filter(
#                 Album.publisher.contains(search_string))
#             results = qry.all()
#         else:
#             qry = db_session.query(Album)
#             results = qry.all()
#     else:
#         qry = db_session.query(Album)
#         results = qry.all()
#     if not results:
#         flash('No results found!')
#         return redirect('/')
#     else:
#         # display results
#         table = Results(results)
#         table.border = True
#         return render_template('results.html', table=table)

# @app.route('/listing')
# def listing():
#     user = User()
#     user.email = "gino"
#     user.first_name = "gino"
#     user.last_name = "gino"
#     user.password = "gino"
#     return render_template('listing.html', user=user)

@app.route('/results')
def search_results():
    # a. Keeps track of user position and shows his pro_pic
    global last_url
    last_url = "results/"

    if current_user.is_authenticated:
        pro_pic = current_user.user_id + str(current_user.photo_id) + ".png"
    else:
        pro_pic = ""
    # a_end
    # this is a fake house ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    new_house = Residence()
    new_house.houses_id = uuid.uuid4().hex[::4].capitalize()
    new_house.city = "Turino"
    new_house.street = "Via Guido"
    new_house.civic = 232
    return render_template('results.html',
                           is_auth=current_user.is_authenticated,
                           pro_pic=pro_pic)
                          # user=user,# ask mat if this is a
                          # image_name=user_image_name,
                          # habits_form=habits_form)
    # this is a fake house ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # -insert the correct data in the return
    # -insert this into the HTML verify the html code for reference


@app.route('/h/<house_id>')
def u(user_id):
    # a. Keeps track of user position and shows his pro_pic
    global last_url
    last_url = "u/" + user_id

    if current_user.is_authenticated:
        pro_pic = current_user.user_id + str(current_user.photo_id) + ".png"
    else:
        pro_pic = ""
    # a_end

    user = User.query.filter_by(user_id=user_id.capitalize()).first_or_404()
    user_image_name = user.user_id + str(user.photo_id) + ".png"

    habits_form = EditSlidersDataForm()

    return render_template('listing.html',
                           house=house,
                           )


@app.route('/h_edit/<house_id>')
@login_required
def u(house_id):
    # a. Keeps track of user position and shows his pro_pic
    global last_url
    last_url = "h/" +house_id_id

    if current_user.is_authenticated:
        pro_pic = current_user.user_id + str(current_user.photo_id) + ".png"
    else:
        pro_pic = ""
    # a_end

    user = User.query.filter_by(user_id=user_id.capitalize()).first_or_404()
    user_image_name = user.user_id + str(user.photo_id) + ".png"

    habits_form = EditSlidersDataForm()

    return render_template('public_profile.html',
                           user=user,
                           image_name=user_image_name,
                           is_auth=current_user.is_authenticated,
                           pro_pic=pro_pic,
                           habits_form=habits_form)


@app.route('/upload_house_image/<house_id>', methods=['GET', 'POST'])  # lucas changed ths
@login_required
def upload_house_image(house_id):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print 'No file part'
            return redirect(request.url)
        house_picture = request.files['file']
        # check if user has selected file
        if house_picture.filename == '':
            print 'No selected file'
            return redirect(request.url)
        if house_picture:

            db.session.commit()
            filename = "'\'" + house_id + "\(1).png"
            # saving new image to /uploads
            house_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # deleting old image associated to the user
            return redirect(url_for('personal_page'))

    return render_template('upload.html')


# ======================================================================================================================
# GLOBAL VARIABLES
# ======================================================================================================================
errors_in_login_registration = 0
# 1 is wrong email/password in login
# 2 is user already registered in registration
# 3 password and password2 do not match

errors_in_private_page = 0
# 1 wrong password, user not allowed to change sensitive information
show_wrong_password_box = 0
# 1 wrong password box message showed

last_url = ''
# used to keep track of the last page the user was visiting (public pages)
# in order to redirect him there after login/logout

#   smoking_habits = "10000000"
#       vegetarian = "01000000"
#     eat_together = "00900000"
#        do_sports = "00090000"
#    house_parties = "00009000"
#   invite_friends = "00000900"
#    stays_in_room = "00000090"
# overnight_guests = "00000009"

initial___amenities = "00000000"
amenities______beds = "10000000"
amenities_____baths = "01000000"
amenities______lift = "00100000"
amenities_____floor = "00010000"
amenities____washer = "00001000"
amenities__bath_tub = "00000100"
amenities____shower = "00000010"
amenities_workplace = "00000001"

# ======================================================================================================================

if __name__ == '__main__':
    app.run(debug=True)
