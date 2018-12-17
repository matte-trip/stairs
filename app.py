from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, TextAreaField, SelectField, BooleanField
from wtforms.fields.html5 import DecimalRangeField
from wtforms.validators import DataRequired, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
import uuid
import os
import shutil

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'C0fUTr5*iB5o&uWi-r@&'

cities = [("0", "TURIN")]

types = [("0", "SINGLE"),
         ("1", "DOUBLE")]

types_query = [("0", "---"),
               ("1", "SINGLE"),
               ("2", "DOUBLE")]

neighbourhoods = [("0", "AURORA"),
                  ("1", "BARCA"),
                  ("2", "BARRIERA DI MILANO"),
                  ("3", "BORGATA VITTORIA"),
                  ("4", "BORGO PO"),
                  ("5", "CAMPIDOGLIO"),
                  ("6", "CENISIA"),
                  ("7", "CENTRO"),
                  ("8", "CROCETTA"),
                  ("9", "FALCHERA"),
                  ("10", "LANZO"),
                  ("11", "LINGOTTO"),
                  ("12", "LUCENTO"),
                  ("13", "MADONNA DEL PILONE"),
                  ("14", "MIRAFIORI NORD"),
                  ("15", "MIRAFIORI SUD"),
                  ("16", "NIZZA"),
                  ("17", "PARELLA"),
                  ("18", "POZZO STRADA"),
                  ("19", "SAN PAOLO"),
                  ("20", "SAN SALVARIO"),
                  ("21", "SANTA RITA"),
                  ("22", "VANCHIGLIA")]

neighbourhoods_query = [("0", "---"),
                        ("1", "AURORA"),
                        ("2", "BARCA"),
                        ("3", "BARRIERA DI MILANO"),
                        ("4", "BORGATA VITTORIA"),
                        ("5", "BORGO PO"),
                        ("6", "CAMPIDOGLIO"),
                        ("7", "CENISIA"),
                        ("8", "CENTRO"),
                        ("9", "CROCETTA"),
                        ("a", "FALCHERA"),
                        ("b", "LANZO"),
                        ("c", "LINGOTTO"),
                        ("d", "LUCENTO"),
                        ("e", "MADONNA DEL PILONE"),
                        ("f", "MIRAFIORI NORD"),
                        ("g", "MIRAFIORI SUD"),
                        ("h", "NIZZA"),
                        ("i", "PARELLA"),
                        ("j", "POZZO STRADA"),
                        ("k", "SAN PAOLO"),
                        ("l", "SAN SALVARIO"),
                        ("m", "SANTA RITA"),
                        ("n", "VANCHIGLIA")]

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
    habits = db.Column('habits', db.String(12), default="000000000000")

    # Other fields
    house_id = db.Column('house_id', db.String(8))
    photo_id = db.Column('photo_id', db.Integer, default=0)
    phone_number = db.Column('phone_number', db.String(10))
    calendar = db.Column('calendar', db.String(31), default="0000000000000000000000000000000")

    # overrides get_id in UserMixin putting email as the attribute which identifies the user instead of id
    def get_id(self):
        return self.email

    # password is a property of user, if read it raise an exception
    @property
    def password(self):
        raise StandardError('Password cannot be read')

    # password is set through this method, by generating a hash value based on the user password
    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Residence(db.Model):
    __tablename__ = 'houses'

    # Id field
    house_id = db.Column('house_id', db.String(8), primary_key=True, unique=True, nullable=False)
    house_sc = db.Column('house_sc', db.String(8), nullable=False)
    photo_id = db.Column('photo_id', db.Integer)

    type = db.Column('type', db.String(30), nullable=False)
    name = db.Column('name', db.String(30), nullable=False)
    city = db.Column('city', db.String(30), nullable=False)
    street = db.Column('street', db.String(50), nullable=False)
    civic = db.Column('civic', db.Integer)
    neighbourhood = db.Column('neighbourhood', db.String(50), nullable=False)
    amenities = db.Column('amenities', db.String(6), default="000000")
    description = db.Column('description', db.String(1000), nullable=False)
    rules = db.Column('rules', db.String(1000), nullable=False)
    bills = db.Column('bills', db.String(1000), nullable=False)
    price = db.Column('price', db.Integer)


# ======================================================================================================================
# FORMS
# ======================================================================================================================

class LoginForm(FlaskForm):
    login_email = StringField('Email', validators=[DataRequired()])
    login_password = PasswordField('Password', validators=[DataRequired()])
    login_button = SubmitField('Login')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    city = SelectField('City', choices=cities, validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
    registration_button = SubmitField('Register')


class EditPrivateDataForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    city = SelectField('City', choices=cities, validators=[DataRequired()])
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
    past_experience = DecimalRangeField('Do you have past experiences of house sharing?')
    do_sports = DecimalRangeField('Do you practice sports?')
    pet_friendly = DecimalRangeField('Are you pet friendly?')
    # how much do you like...
    eat_together = DecimalRangeField('Eating with housemates')
    ideal_week_end1 = DecimalRangeField('Staying at home and chill')
    ideal_week_end2 = DecimalRangeField('Hanging out with friends')
    house_parties = DecimalRangeField('House parties')
    # i'm used to
    invite_friends = DecimalRangeField('Invite friends at home')
    overnight_guests = DecimalRangeField('Have overnight guests')
    play_music = DecimalRangeField('Play music without headphones')
    time_at_home = DecimalRangeField('Spend most of my time at home')
    save_habits = SubmitField('Save')


class ExistingHouseForm(FlaskForm):
    house_sc = StringField('Secret House ID')
    enter_button = SubmitField('Enter')


class EditHouseForm(FlaskForm):
    type = SelectField('Type', choices=types, validators=[DataRequired()])
    city = SelectField('City', choices=cities, validators=[DataRequired()])
    neighbourhood = SelectField('Neighbourhood', choices=neighbourhoods,
                                validators=[DataRequired()])
    street = StringField('Street', validators=[DataRequired()])
    civic = IntegerField('Civic', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    rules = TextAreaField('Rules', validators=[DataRequired()])
    price = IntegerField('Price in Euros', validators=[DataRequired()])
    bills = TextAreaField('Bills')

    lift = BooleanField('Lift')
    pet_friendly = BooleanField('Pet Friendly')
    independent_heating = BooleanField('Independent Heating')
    air_conditioned = BooleanField('Air Conditioned')
    furniture = BooleanField('Furniture')
    wifi = BooleanField('Wi-Fi')

    save_information = SubmitField('Save Information')


class FilterForm(FlaskForm):
    type = SelectField('Type', choices=types_query, validators=[DataRequired()])
    neighbourhood = SelectField('Neighbourhood', choices=neighbourhoods_query, validators=[DataRequired()])

    lift = BooleanField('Lift')
    pet_friendly = BooleanField('Pet Friendly')
    independent_heating = BooleanField('Independent Heating')
    air_conditioned = BooleanField('Air Conditioned')
    furniture = BooleanField('Furniture')
    wifi = BooleanField('Wi-Fi')

    apply_filters = SubmitField('Apply Filters')


class EditCalendarForm(FlaskForm):
    c1 = BooleanField('1')
    c2 = BooleanField('2')
    c3 = BooleanField('3')
    c4 = BooleanField('4')
    c5 = BooleanField('5')
    c6 = BooleanField('6')
    c7 = BooleanField('7')
    c8 = BooleanField('8')
    c9 = BooleanField('9')
    c10 = BooleanField('10')
    c11 = BooleanField('11')
    c12 = BooleanField('12')
    c13 = BooleanField('13')
    c14 = BooleanField('14')
    c15 = BooleanField('15')
    c16 = BooleanField('16')
    c17 = BooleanField('17')
    c18 = BooleanField('18')
    c19 = BooleanField('19')
    c20 = BooleanField('20')
    c21 = BooleanField('21')
    c22 = BooleanField('22')
    c23 = BooleanField('23')
    c24 = BooleanField('24')
    c25 = BooleanField('25')
    c26 = BooleanField('26')
    c27 = BooleanField('27')
    c28 = BooleanField('28')
    c29 = BooleanField('29')
    c30 = BooleanField('30')
    c31 = BooleanField('31')

    confirm = SubmitField('Confirm')


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
    # a. Keeps track of user address
    global last_url
    last_url = ''
    # a_end

    # c2. User's pro_pic for public pages
    if current_user.is_authenticated:
        pro_pic = str(current_user.user_id) + str(current_user.photo_id) + ".png"
    else:
        pro_pic = ""
    # c2_end

    global errors_in_login_registration
    errors_in_login_registration = 0

    return render_template('homepage.html',
                           is_auth=current_user.is_authenticated,
                           pro_pic=pro_pic)


@app.route('/login_registration', methods=['GET', 'POST'])
def login_registration():
    # b. Sends away the user if he tries to go to login_registration when already logged in
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
            new_user.city = cities[int(registration_form.city.data)][1]
            new_user.password = registration_form.password.data
            new_user.user_id = uuid.uuid4().hex[::4].capitalize()
            default_image_destination_path = str(new_user.user_id) + "0.png"
            shutil.copy(os.path.join(static_folder, 'user-default.png'),
                        os.path.join(uploads_folder, default_image_destination_path))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect('user')

    return render_template('login_registration.html',

                           login_form=login_form,
                           registration_form=registration_form,
                           error=errors_in_login_registration)


@app.route('/user', methods=['GET', 'POST'])
@login_required
def personal_page():
    # c1. User's pro_pic for login_required pages
    pro_pic = str(current_user.user_id) + str(current_user.photo_id) + ".png"
    # c1_end

    global errors_in_private_page
    global show_wrong_password_box
    global errors_in_existing
    errors_in_existing = 0

    personal_profile_form = EditPrivateDataForm()
    bio_form = EditPublicDataForm()
    if personal_profile_form.validate_on_submit():
        if current_user.check_password(personal_profile_form.password.data):
            current_user.email = personal_profile_form.email.data
            current_user.first_name = personal_profile_form.first_name.data
            current_user.last_name = personal_profile_form.last_name.data
            current_user.city = cities[int(personal_profile_form.city.data)][1]
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

    availability = current_user.calendar

    days = []
    for i in range(1, 32):
        days.append(i)

    calendar_availability = zip(availability, days)

    habits_form = EditSlidersDataForm()
    if request.method == 'GET' or errors_in_private_page:
        show_wrong_password_box = 0
        if errors_in_private_page:
            show_wrong_password_box = 1
        errors_in_private_page = 0

        personal_profile_form.email.data = current_user.email
        personal_profile_form.first_name.data = current_user.first_name
        personal_profile_form.last_name.data = current_user.last_name
        personal_profile_form.city.data = current_user.city
        personal_profile_form.phone_number.data = current_user.phone_number

        bio_form.age.data = current_user.age
        bio_form.study_field.data = current_user.study_field
        bio_form.university.data = current_user.university
        bio_form.bio.data = current_user.bio
        bio_form.interests.data = current_user.interests
        bio_form.languages.data = current_user.languages

    if current_user.house_id:
        house = Residence.query.filter_by(house_id=current_user.house_id.capitalize()).first()

    else:
        house = ""

    return render_template('private_profile.html',
                           is_auth=current_user.is_authenticated,
                           pro_pic=pro_pic,

                           personal_profile_form=personal_profile_form,
                           error=show_wrong_password_box,
                           bio_form=bio_form,
                           habits_form=habits_form,

                           house=house,

                           calendar_availability=calendar_availability)


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
            filename = str(current_user.user_id) + str(current_user.photo_id) + ".png"
            # saving new image to /uploads
            # profile_picture.save(os.path.join(uploads_folder, filename))
            profile_picture.save(os.path.join(uploads_folder, filename))
            # deleting old image associated to the user
            filename = str(current_user.user_id) + str(current_user.photo_id - 1) + ".png"
            os.remove(os.path.join(uploads_folder, filename))
            return redirect(url_for('personal_page'))

    return render_template('upload.html')


@app.route('/habits', methods=['GET', 'POST'])
@login_required
def habits():
    # c1. User's pro_pic for login_required pages
    pro_pic = str(current_user.user_id) + str(current_user.photo_id) + ".png"
    # c1_end

    habits_form = EditSlidersDataForm()
    if request.method == 'POST':
        habits_list = [str(habits_form.smoking_habits.data),
                       str(habits_form.past_experience.data),
                       str(habits_form.do_sports.data),
                       str(habits_form.pet_friendly.data),
                       str(habits_form.eat_together.data),
                       str(habits_form.ideal_week_end1.data),
                       str(habits_form.ideal_week_end2.data),
                       str(habits_form.house_parties.data),
                       str(habits_form.invite_friends.data),
                       str(habits_form.overnight_guests.data),
                       str(habits_form.play_music.data),
                       str(habits_form.time_at_home.data)]
        current_user.habits = "".join(habits_list)
        db.session.commit()

        return redirect(url_for('personal_page'))

    return render_template('habits.html',
                           pro_pic=pro_pic,

                           habits_form=habits_form)


@app.route('/u/<user_id>')
def u(user_id):
    # a. Keeps track of user position and shows his pro_pic
    global last_url
    last_url = "u/" + user_id
    # a_end

    # c2. User's pro_pic for public pages
    if current_user.is_authenticated:
        pro_pic = str(current_user.user_id) + str(current_user.photo_id) + ".png"
    else:
        pro_pic = ""
    # c2_end

    user = User.query.filter_by(user_id=user_id.capitalize()).first_or_404()
    user_image_name = str(user.user_id) + str(user.photo_id) + ".png"

    habits_form = EditSlidersDataForm()

    return render_template('public_profile.html',
                           is_auth=current_user.is_authenticated,
                           pro_pic=pro_pic,

                           user=user,
                           image_name=user_image_name,
                           habits_form=habits_form)


@app.route('/s/<filters>', methods=['GET', 'POST'])
def s(filters):
    # a. Keeps track of user position and shows his pro_pic
    global last_url
    last_url = "s/" + filters
    # a_end

    # c2. User's pro_pic for public pages
    if current_user.is_authenticated:
        pro_pic = str(current_user.user_id) + str(current_user.photo_id) + ".png"
    else:
        pro_pic = ""
    # c2_end

    all_houses = Residence.query.all()

    # FILTERS:
    # filters[0] type > 0 all, 1 single, 2 double
    # filters[1] neighbourhood > 0 all, 1 aurora, .. a lanzo, .. m vanchiglia
    # filters[2] lift > 0 all, 1 yes
    # filters[3] pet_friendly
    # filters[4] independent_heating
    # filters[5] air_conditioned
    # filters[6] furniture
    # filters[7] wifi

    if filters[0] == types_query[1][0]:
        all_houses = [house for house in all_houses if house.type == types_query[1][1]]
    elif filters[0] == types_query[2][0]:
        all_houses = [house for house in all_houses if house.type == types_query[2][1]]

    for i in range(1, 24):
        if str(filters[1]) == neighbourhoods_query[i][0]:
            all_houses = [house for house in all_houses if house.neighbourhood == neighbourhoods_query[i][1]]

    if filters[2] == str(1):
        all_houses = [house for house in all_houses if house.amenities[0] == str(1)]

    if filters[3] == str(1):
        all_houses = [house for house in all_houses if house.amenities[1] == str(1)]

    if filters[4] == str(1):
        all_houses = [house for house in all_houses if house.amenities[2] == str(1)]

    if filters[5] == str(1):
        all_houses = [house for house in all_houses if house.amenities[3] == str(1)]

    if filters[6] == str(1):
        all_houses = [house for house in all_houses if house.amenities[4] == str(1)]

    if filters[7] == str(1):
        all_houses = [house for house in all_houses if house.amenities[5] == str(1)]

    filter_form = FilterForm()
    filter_list = []
    if request.method == 'POST':

        if filter_form.validate_on_submit():
            filter_list.append(filter_form.type.data)
            filter_list.append(filter_form.neighbourhood.data)

            filter_list.append(str(int(filter_form.lift.data)))
            filter_list.append(str(int(filter_form.pet_friendly.data)))
            filter_list.append(str(int(filter_form.independent_heating.data)))
            filter_list.append(str(int(filter_form.air_conditioned.data)))
            filter_list.append(str(int(filter_form.furniture.data)))
            filter_list.append(str(int(filter_form.wifi.data)))
            filters = "".join(filter_list)
            return redirect(url_for('s', filters=filters))

    else:
        filter_form.type.data = types_query[int(filters[0])][0]
        filter_form.neighbourhood.data = neighbourhoods_query[int(filters[1])][0]
        filter_form.lift.data = int(filters[2])
        filter_form.pet_friendly.data = int(filters[3])
        filter_form.independent_heating.data = int(filters[4])
        filter_form.air_conditioned.data = int(filters[5])
        filter_form.furniture.data = int(filters[6])
        filter_form.wifi.data = int(filters[7])

    return render_template('results.html',
                           is_auth=current_user.is_authenticated,
                           pro_pic=pro_pic,

                           all_houses=all_houses,
                           filter_form=filter_form)


@app.route('/house_creation', methods=['GET', 'POST'])
@login_required
def house_creation():
    # c1. User's pro_pic for login_required pages
    pro_pic = str(current_user.user_id) + str(current_user.photo_id) + ".png"
    # c1_end

    house_form = EditHouseForm()
    if house_form.validate_on_submit():
        new_house = Residence()
        new_house.house_id = uuid.uuid4().hex[::4].capitalize()
        new_house.house_sc = uuid.uuid4().hex[::4].capitalize()
        new_house.photo_id = -1

        new_house.type = types[int(house_form.type.data)][1]
        new_house.neighbourhood = neighbourhoods[int(house_form.neighbourhood.data)][1]
        new_house.name = new_house.type + " Room in " + new_house.neighbourhood
        new_house.city = cities[int(house_form.city.data)][1]
        new_house.street = house_form.street.data
        new_house.civic = house_form.civic.data
        new_house.description = house_form.description.data
        new_house.rules = house_form.rules.data
        new_house.price = house_form.price.data
        new_house.bills = house_form.bills.data

        amenities_list = [str(int(house_form.lift.data)),
                          str(int(house_form.pet_friendly.data)),
                          str(int(house_form.independent_heating.data)),
                          str(int(house_form.air_conditioned.data)),
                          str(int(house_form.furniture.data)),
                          str(int(house_form.wifi.data))]

        new_house.amenities = "".join(amenities_list)

        current_user.house_id = new_house.house_id

        db.session.add(new_house)
        db.session.commit()
        return redirect(url_for('personal_page'))

    return render_template('house_creation.html',
                           pro_pic=pro_pic,

                           house_form=house_form)


@app.route('/h_edit/<house_id>', methods=['GET', 'POST'])
@login_required
def h_edit(house_id):
    # c1. User's pro_pic for login_required pages
    pro_pic = str(current_user.user_id) + str(current_user.photo_id) + ".png"
    # c1_end

    house = Residence.query.filter_by(house_id=house_id.capitalize()).first_or_404()
    house_form = EditHouseForm()

    if house.house_id == current_user.house_id:
        if house_form.validate_on_submit():
            house.type = types[int(house_form.type.data)][1]
            house.neighbourhood = neighbourhoods[int(house_form.neighbourhood.data)][1]
            house.name = house.type + " Room in " + house.neighbourhood
            house.city = cities[int(house_form.city.data)][1]

            house.street = house_form.street.data
            house.civic = house_form.civic.data
            house.description = house_form.description.data
            house.rules = house_form.rules.data
            house.price = house_form.price.data
            house.bills = house_form.bills.data

            amenities_list = [str(int(house_form.lift.data)),
                              str(int(house_form.pet_friendly.data)),
                              str(int(house_form.independent_heating.data)),
                              str(int(house_form.air_conditioned.data)),
                              str(int(house_form.furniture.data)),
                              str(int(house_form.wifi.data))]

            house.amenities = "".join(amenities_list)

            db.session.commit()
            redirect(url_for('h_edit', house_id=house_id))

        if request.method == 'GET':
            if house.type == types[0][1]:
                house_form.type.data = types[0][0]
            elif house.type == types[1][1]:
                house_form.type.data = types[1][0]

            if house.city == cities[0][1]:
                house_form.city.data = cities[0][0]

            for i in range(0, 23):
                if house.neighbourhood == neighbourhoods[i][1]:
                    house_form.neighbourhood.data = neighbourhoods[i][0]

            house_form.street.data = house.street
            house_form.civic.data = house.civic
            house_form.description.data = house.description
            house_form.rules.data = house.rules
            house_form.price.data = house.price
            house_form.bills.data = house.bills

            house_form.lift.data = bool(int(house.amenities[0]))
            house_form.pet_friendly.data = bool(int(house.amenities[1]))
            house_form.independent_heating.data = bool(int(house.amenities[2]))
            house_form.air_conditioned.data = bool(int(house.amenities[3]))
            house_form.furniture.data = bool(int(house.amenities[4]))
            house_form.wifi.data = bool(int(house.amenities[5]))

    else:
        redirect(url_for('personal_page'))

    return render_template('private_listing.html',
                           pro_pic=pro_pic,

                           house=house,
                           house_form=house_form)


@app.route('/upload_house_image/<house_id>', methods=['GET', 'POST'])
@login_required
def upload_house_image(house_id):
    house = Residence.query.filter_by(house_id=house_id.capitalize()).first_or_404()

    if house.house_id == current_user.house_id:
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
                house.photo_id += 1
                db.session.commit()

                filename = str(house.house_id) + str(house.photo_id) + ".png"
                house_picture.save(os.path.join(uploads_folder, filename))

                return redirect(url_for('h_edit', house_id=current_user.house_id))
    else:
        return redirect(url_for('h_edit', house_id=current_user.house_id))

    return render_template('upload_house_image.html')


@app.route('/h/<house_id>')
def h(house_id):
    # a. Keeps track of user position and shows his pro_pic
    global last_url
    last_url = "h/" + house_id
    # a_end

    # c2. User's pro_pic for public pages
    if current_user.is_authenticated:
        pro_pic = str(current_user.user_id) + str(current_user.photo_id) + ".png"
    else:
        pro_pic = ""
    # c2_end

    house = Residence.query.filter_by(house_id=house_id.capitalize()).first_or_404()
    housemates = User.query.filter_by(house_id=house_id.capitalize()).all()

    user_images_list = []
    for housemate in housemates:
        user_images_list.append(str(housemate.user_id) + str(housemate.photo_id) + ".png")

    housemates_and_photos = zip(housemates, user_images_list)

    return render_template('public_listing.html',
                           is_auth=current_user.is_authenticated,
                           pro_pic=pro_pic,

                           house=house,
                           housemates=housemates,
                           user_images_list=user_images_list,
                           housemates_and_photos=housemates_and_photos,

                           lift=int(house.amenities[0]),
                           pet_friendly=int(house.amenities[1]),
                           independent_heating=int(house.amenities[2]),
                           air_conditioned=int(house.amenities[3]),
                           furniture=int(house.amenities[4]),
                           wifi=int(house.amenities[5]))


@app.route('/existing', methods=['GET', 'POST'])
@login_required
def existing():
    # c1. User's pro_pic for login_required pages
    pro_pic = str(current_user.user_id) + str(current_user.photo_id) + ".png"
    # c1_end

    global errors_in_existing

    existing_house_form = ExistingHouseForm()

    if request.method == 'POST':
        if existing_house_form.validate_on_submit():
            # here the user must enter the house secret code in order to join the house
            house_sc = existing_house_form.house_sc.data
            house = Residence.query.filter_by(house_sc=house_sc.capitalize()).first()

            if house is None:
                errors_in_existing = 1
                return redirect(url_for('existing'))
            else:
                current_user.house_id = house.house_id
                db.session.commit()
                return redirect(url_for('personal_page'))

    return render_template('existing.html',
                           is_auth=current_user.is_authenticated,
                           pro_pic=pro_pic,

                           existing_house=existing_house_form,

                           error=errors_in_existing)


@app.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar():
    # c1. User's pro_pic for login_required pages
    pro_pic = str(current_user.user_id) + str(current_user.photo_id) + ".png"
    # c1_end

    calendar_availability = EditCalendarForm()
    if request.method == 'POST':
        if calendar_availability.validate_on_submit():
            days_available = [str(int(calendar_availability.c1.data)),
                              str(int(calendar_availability.c2.data)),
                              str(int(calendar_availability.c3.data)),
                              str(int(calendar_availability.c4.data)),
                              str(int(calendar_availability.c5.data)),
                              str(int(calendar_availability.c6.data)),
                              str(int(calendar_availability.c7.data)),
                              str(int(calendar_availability.c8.data)),
                              str(int(calendar_availability.c9.data)),
                              str(int(calendar_availability.c10.data)),
                              str(int(calendar_availability.c11.data)),
                              str(int(calendar_availability.c12.data)),
                              str(int(calendar_availability.c13.data)),
                              str(int(calendar_availability.c14.data)),
                              str(int(calendar_availability.c15.data)),
                              str(int(calendar_availability.c16.data)),
                              str(int(calendar_availability.c17.data)),
                              str(int(calendar_availability.c18.data)),
                              str(int(calendar_availability.c19.data)),
                              str(int(calendar_availability.c20.data)),
                              str(int(calendar_availability.c21.data)),
                              str(int(calendar_availability.c22.data)),
                              str(int(calendar_availability.c23.data)),
                              str(int(calendar_availability.c24.data)),
                              str(int(calendar_availability.c25.data)),
                              str(int(calendar_availability.c26.data)),
                              str(int(calendar_availability.c27.data)),
                              str(int(calendar_availability.c28.data)),
                              str(int(calendar_availability.c29.data)),
                              str(int(calendar_availability.c30.data)),
                              str(int(calendar_availability.c31.data))]
            current_user.calendar = "".join(days_available)
            db.session.commit()

        return redirect(url_for('personal_page'))

    else:
        calendar_availability.c1.data = int(current_user.calendar[0])
        calendar_availability.c2.data = int(current_user.calendar[1])
        calendar_availability.c3.data = int(current_user.calendar[2])
        calendar_availability.c4.data = int(current_user.calendar[3])
        calendar_availability.c5.data = int(current_user.calendar[4])
        calendar_availability.c6.data = int(current_user.calendar[5])
        calendar_availability.c7.data = int(current_user.calendar[6])
        calendar_availability.c8.data = int(current_user.calendar[7])
        calendar_availability.c9.data = int(current_user.calendar[8])
        calendar_availability.c10.data = int(current_user.calendar[9])
        calendar_availability.c11.data = int(current_user.calendar[10])
        calendar_availability.c12.data = int(current_user.calendar[11])
        calendar_availability.c13.data = int(current_user.calendar[12])
        calendar_availability.c14.data = int(current_user.calendar[13])
        calendar_availability.c15.data = int(current_user.calendar[14])
        calendar_availability.c16.data = int(current_user.calendar[15])
        calendar_availability.c17.data = int(current_user.calendar[16])
        calendar_availability.c18.data = int(current_user.calendar[17])
        calendar_availability.c19.data = int(current_user.calendar[18])
        calendar_availability.c20.data = int(current_user.calendar[19])
        calendar_availability.c21.data = int(current_user.calendar[20])
        calendar_availability.c22.data = int(current_user.calendar[21])
        calendar_availability.c23.data = int(current_user.calendar[22])
        calendar_availability.c24.data = int(current_user.calendar[23])
        calendar_availability.c25.data = int(current_user.calendar[24])
        calendar_availability.c26.data = int(current_user.calendar[25])
        calendar_availability.c27.data = int(current_user.calendar[26])
        calendar_availability.c28.data = int(current_user.calendar[27])
        calendar_availability.c29.data = int(current_user.calendar[28])
        calendar_availability.c30.data = int(current_user.calendar[29])
        calendar_availability.c31.data = int(current_user.calendar[30])

    return render_template('private_booking.html',
                           pro_pic=pro_pic,

                           calendar_availability=calendar_availability)


@app.route('/b/<user_id>')
@login_required
def b(user_id):
    # c1. User's pro_pic for login_required pages
    pro_pic = str(current_user.user_id) + str(current_user.photo_id) + ".png"
    # c1_end

    user = User.query.filter_by(user_id=user_id.capitalize()).first_or_404()

    availability = user.calendar

    days = []
    for i in range(1, 32):
        days.append(i)

    calendar_availability = zip(availability, days)

    if user.phone_number is not None:
        phone = user.phone_number
    else:
        phone = 0

    house = Residence.query.filter_by(house_id=user.house_id.capitalize()).first_or_404()

    return render_template('public_booking.html',
                           pro_pic=pro_pic,

                           user=user,
                           calendar_availability=calendar_availability,
                           phone=phone,
                           house=house)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(e):
    if e:
        print "Error 404"
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    if e:
        print "Error 500"
    return render_template('500.html'), 500


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

errors_in_existing = 0
# 1 wrong secret code, user did not entered a valid house_sc

# paths to static and uploads folder in my os
static_folder = 'C:\\Users\\Matteo\\Desktop\\Drive\\Information Systems\\Housr - Information Systems\\stairs\\static'
uploads_folder = 'C:\\Users\\Matteo\\Desktop\\Drive\\Information Systems\\Housr - Information Systems\\stairs\\uploads'

# paths to static and uploads folder in python anywhere
static_folder_p = '/home/voq82809/mysite/static'
uploads_folder_p = '/home/voq82809/mysite/uploads'
# also to run in python anywhere redirect("http://voq82809.pythonanywhere.com/" ... at line 344

# ======================================================================================================================
# STARTUP
# ======================================================================================================================

if __name__ == '__main__':
    app.run(debug=True)
