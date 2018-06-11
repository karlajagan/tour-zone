from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tour-zone:tourzonepw@localhost:3306/tour-zone'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'fsfsdfsdfsd'

# from model import db, Blog, User

db = SQLAlchemy(app)


class Tour(db.Model):

    tour_id = db.Column(db.Integer, primary_key=True)
    tour = db.Column(db.String(100), nullable=False)
    attraction = db.Column(db.String(500))
    difficulty_level = db.Column(db.Integer)
    availability = db.Column(db.String(200))
    min_age = db.Column(db.Integer)
    max_age = db.Column(db.Integer)
    date_stamp = db.Column(db.DateTime)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))

    def __init__(self, tour, attraction, difficulty_level, availability,
                 min_age, max_age, date_stamp, provider, city):
        self.tour = tour
        self.attraction = attraction
        self.difficulty_level = difficulty_level
        self.availability = availability
        self.min_age = min_age
        self.max_age = max_age
        self.date_stamp = date_stamp
        self.provider = provider
        self.city = city


class Provider(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    primary_phone = db.Column(db.Integer, nullable=False)
    street_address = db.Column(db.String(100), nullable=False)
    driver_license = db.Column(db.String(50))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    tours = db.relationship('Tour', backref='provider')

    def __init__(self, name, last_name,
                 username, email, password, primary_phone,
                 street_address, driver_license, city):
        self.name = name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = password
        self.primary_phone = primary_phone
        self.street_address = street_address
        self.driver_license = driver_license
        self.city = city


class City(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    state = db.Column(db.String(60))
    country = db.Column(db.String(60))
    tours = db.relationship('Tour', backref='city')
    providers = db.relationship('Provider', backref='city')

    def __init__(self, name, state, country):
        self.name = name
        self.state = state
        self.country = country


def is_space(word):
    if ' ' in word:
        return True
    else:
        return False


def validate_field(field, text):
    error = ""
    if field == "" and text != "Email ":
        error = text + "must not be empty"
    elif is_space(field):
        error = text + "should not contain spaces"
        field = ""
    else:
        if len(field) <= 3 or len(field) >= 40:
            error = text + "must have between 3 and 40 characters"
            field = ""
    return error


def validate_email_re(field):
    pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    if pattern.match(field):
        return ""
    else:
        return "email not valid"


@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'tour_list']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        provider = Provider.query.filter_by(username=username).first()
        if provider and provider.password == password:
            session['username'] = username
            return redirect('/tour')
        else:
            flash('Provider password is incorrect, or provider does not exist', 'error')

    if session.get('username') is not None:
        del session['username']

    return render_template('login.html', title = "Provider Login")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if session.get('username') is not None:
        del session['username']
    if request.method == 'POST':
        
        name = request.form['name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        primary_phone = request.form['primary_phone']
        street_address = request.form['street_address']
        driver_license = request.form['driver_license']
        city_id = request.form['city_id']

        name_error = ''
        last_name_error = ''        
        username_error = ''
        password_error = ''
        validate_error = ''
        email_error = ''
        primary_phone_error = ''
        street_address_error = ''
        driver_license_error = ''
        # city_id_error = ''

        existing_provider = Provider.query.filter_by(username=username).first()
        
        if not existing_provider:

            name_error = validate_field(name,"Name ")
            last_name_error = validate_field(last_name,"Last Name")            
            username_error = validate_field(username,"Username ")   
            password_error = validate_field(password,"Password ")          
            validate_error = validate_field(verify,"Password ")
            primary_phone_error = validate_field(primary_phone,"Primary phone")
            # TODO change validation of city
            # city = "ciudad"
            # city_id_error = validate_field(city,'City ')
            
            if verify != password:
                validate_error = "The passwords are not matching"
                password = ""
                verify = ""

            if email != '':
                email_error = validate_field(email,"Email ")
                if email_error == "":
                    email_error = validate_email_re(email)
                    if email_error != "":
                        email = ""
            if not username_error and not password_error and \
               not validate_error and not email_error:
                primary_phone = int(primary_phone)
                city_id = int(city_id)
                city = City.query.filter_by(id=city_id).first()
      
                new_provider = Provider(name,last_name, username, 
                    email, password, primary_phone, street_address, 
                    driver_license, city)
                db.session.add(new_provider)
                db.session.commit()
                password = ""
                # befor verify was val_password
                verify = ""
                # session['username'] = username
                return redirect('/login')           
            else:
                return render_template('register.html', 
                    title="Register", name_error = name_error,
                    last_name_error = last_name_error,
                    username_error = username_error,
                    password_error =password_error, 
                    validate_error=validate_error,
                    email_error=email_error, 
                    primary_phone_error = primary_phone_error,
                    street_address_error = street_address_error,
                    driver_license_error = driver_license_error,
                    username = username,
                    password = "", verify = "",
                    email = email)
# city_id_error = "",   
            
        else:
            return '<h1>Duplicate Provider </h1>'

    return render_template('register.html', 
                    title="Register", username_error = '',
                    password_error ='', 
                    validate_error='',
                    email_error='', username = '',
                    password = '', verify = '',
                    email = '')   


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')


@app.route("/", methods=['GET'])
def index():
    if session.get('username') is not None:
        flash('logged in as '+session['username'])
    else:
        flash('not logged in') 
    tours = Tour.query.all()
    return render_template("display_tours.html", title = "all Tours", tours=tours)


@app.route('/tour', methods=['GET', 'POST'])
def tour_list():
    # add all the blogs from a specific author
    tour_id = request.args.get('tour_id', '')
 
    username = ''
    if session.get('username') is not None:
        flash('logged in as '+session['username'])
    else:
        flash('not logged in')       
        # username = session['username']
    username_arg = request.args.get('provider', '')
    if username_arg != '':
        username = username_arg

    if username != '':
        provider = Provider.query.filter_by(username=username).first()
        tours = Tour.query.order_by(Tour.tour_id.desc()).filter_by(provider=provider).all()
        return render_template('display_tours.html', title="The Best Tours Online", 
            tours=tours)
    if tour_id == '':
        tours = Tour.query.order_by(Tour.tour_id.desc()).all()
        return render_template('display_tours.html', title="The Best Tours Online", 
            tours=tours)        
    else:
        tour_id = int(tour_id)
        tour = Tour.query.get(tour_id)
        return render_template('display_tour.html', tour=tour.tour, 
            attractions=tour.attraction)
    

@app.route('/newpost', methods=['GET'])
def add_tour():
    flash('logged in as '+session['username'])
    return render_template('add-a-tour.html', title="Add a Tour", 
        tour="" , attraction="" , difficulty_level="", availability="",
        min_age="" , max_age="" , date_stamp="" , Provider_id ="",
        city_id = "", tour_error="" , attraction_error="")


@app.route('/newpost', methods=['POST'])
def added_tour():

    provider = Provider.query.filter_by(username=session['username']).first()
    city = City.query.filter_by()
    date_stamp = datetime.datetime.now()
    tour = request.form['tour']
    attraction = request.form['attraction']
    difficulty_level = request.form['difficulty_level']
    availability = request.form['availability']
    min_age = request.form['min_age']
    min_age = int(min_age)
    max_age = request.form['max_age']
    max_age = int(max_age)
    city_id = int(request.form['city_id'])
    city = City.query.filter_by(id=city_id).first()
    tour_error = ""
    attraction_error = ""
    if tour == "" or attraction == "":
        if tour == "":
            tour_error = "Please fill in the name of the tour"
        if attraction == "":
            attraction_error = "Please fill in the attractions covered"
        return render_template('add-a-tour.html',title="Add a Tour", 
            tour = tour, attraction = attraction, difficulty_level = difficulty_level,
            availability = availability, min_age = min_age, max_age = max_age,
            city_id = city_id,
            tour_error = tour_error, 
            attraction_error = attraction_error)
        
    else:

        new_tour = Tour(tour, attraction, difficulty_level, availability,
            min_age, max_age, date_stamp, provider, city)
        db.session.add(new_tour)
        db.session.commit()

        return redirect('/tour?tour_id='+str(new_tour.tour_id))


if __name__ == '__main__':
    app.run()
