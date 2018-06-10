from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://tour-zone:tourzonepw@localhost:3306/tour-zone'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'fsfsdfsdfsd'

#from model import db, Blog, User 

db = SQLAlchemy(app)

class Tour(db.Model):

    tour_id = db.Column(db.Integer, primary_key=True)
    tour = db.Column(db.String(100))
    attraction = db.Column(db.String(500))
    date_stamp = db.Column(db.DateTime)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'))
    
    def __init__(self, tour, attraction, date_stamp, provider):
        self.tour = tour
        self.attraction = attraction
        self.date_stamp = date_stamp
        self.provider = provider

class Provider(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    tours = db.relationship('Tour', backref='provider')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

def is_space(word):
    if ' ' in word:
        return True
    else:
        return False

def validate_field(field,text):
    error = ""
    if field == "" and text != "Email ":
        error = text+"must not be empty"
    elif is_space(field):
        error = text+"should not contain spaces"
        field = ""
    else:
        if len(field) <= 3 or len(field) >= 40:
            error = text+"must have between 3 and 40 characters"
            field = ""
    return error, field   

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

    return render_template('login.html', title = "Provider Login" )

@app.route('/register', methods=['POST', 'GET'])
def register():
    if session.get('username') is not None:
        del session['username']
    if request.method == 'POST':
        
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        validate_error = ''
        email_error = ''

        existing_provider = Provider.query.filter_by(username=username).first()
        
        if not existing_provider:

            username_error, username = validate_field(username,"Username ")
    
            password_error, password = validate_field(password,"Password ")
            
            validate_error, val_password = validate_field(verify,"Password ")
            
            if verify != password:
                validate_error = "The passwords are not matching"
                password = ""
                verify = ""

            if email != '':
                email_error, email = validate_field(email,"Email ")
                if email_error == "":
                    email_error = validate_email_re(email)
                    if email_error != "":
                        email = ""
            if not username_error and not password_error and \
                not validate_error and not email_error:                
                new_provider = Provider(username,email,password)
                db.session.add(new_provider)
                db.session.commit()
                password = ""
                val_password = ""
                # session['username'] = username
                return redirect('/login')           
            else:
                return render_template('register.html', 
                    title="Register", username_error = username_error,
                    password_error =password_error, 
                    validate_error=validate_error,
                    email_error=email_error, username = username,
                    password = "", verify = "",
                    email = email)   
            
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
    providers = Provider.query.all()
    return render_template("display_providers.html", title = "Providers", providers=providers)
        
@app.route('/tour', methods=['GET', 'POST'])
def blog_list():
    #add all the blogs from a specific author
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
        tour="" , attraction="" , tour_error="" , attraction_error="")


@app.route('/newpost', methods=['POST'])
def added_tour():

    provider = Provider.query.filter_by(username=session['username']).first()
    date_stamp = datetime.datetime.now()
    tour = request.form['tour']
    attraction = request.form['attraction']
    tour_error = ""
    attraction_error = ""
    if tour == "" or attraction == "":
        if tour == "":
            tour_error = "Please fill in the name of the tour"
        if attraction == "":
            attraction_error = "Please fill in the attractions covered"
        return render_template('add-a-tour.html',title="Add a Tour", 
            tour = tour, attraction = attraction, tour_error = tour_error, 
            attraction_error = attraction_error )
        
    else:    
        new_tour = Tour(tour, attraction, date_stamp, provider)
        db.session.add(new_tour)
        db.session.commit()

        return redirect('/tour?tour_id='+str(new_tour.tour_id))

if __name__ == '__main__':
    app.run()