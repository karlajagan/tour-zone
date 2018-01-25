from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpw@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fsfsdfsdfsd'

class Blog(db.Model):

    blog_id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(100))
    blog = db.Column(db.String(500))
    date_stamp = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, blog_title, blog, date_stamp, owner):
        self.blog_title = blog_title
        self.blog = blog
        self.date_stamp = date_stamp
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    blogs = db.relationship('Blog', backref='owner')

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
        if len(field) <= 3 or len(field) >= 20:
            error = text+"must have between 3 and 20 characters"
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
    allowed_routes = ['login', 'register', 'index', 'blog_list']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login') 

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/blog')
        else:
            flash('User password is incorrect, or user does not exist', 'error')

    if session.get('username') is not None:
        del session['username']

    return render_template('login.html', title = "Blog Login" )

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

        existing_user = User.query.filter_by(username=username).first()
        
        if not existing_user:

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
                new_user = User(username,email,password)
                db.session.add(new_user)
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
            return '<h1>Duplicate user </h1>'

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
    users = User.query.all()
    return render_template("display_users.html", title = "Blog authors", users=users)
        
@app.route('/blog', methods=['GET', 'POST'])
def blog_list():
    #add all the blogs from a specific author
    blog_id = request.args.get('blog_id', '')
 
    username = ''
    if session.get('username') is not None:
        flash('logged in as '+session['username'])
    else:
        flash('not logged in')       
        # username = session['username']
    username_arg = request.args.get('user', '')
    if username_arg != '':
        username = username_arg

    if username != '':
        owner = User.query.filter_by(username=username).first()
        blogs = Blog.query.order_by(Blog.blog_id.desc()).filter_by(owner=owner).all()
        return render_template('display_blogs.html', title="The Best Blogs Online", 
            blogs=blogs)
    if blog_id == '':
        blogs = Blog.query.order_by(Blog.blog_id.desc()).all()
        return render_template('display_blogs.html', title="The Best Blogs Online", 
            blogs=blogs)        
    else:
        blog_id = int(blog_id)
        blog = Blog.query.get(blog_id)
        return render_template('display_blog.html', title=blog.blog_title, 
            blog=blog.blog)
    

@app.route('/newpost', methods=['GET'])
def add_blog():
    flash('logged in as '+session['username'])
    return render_template('add-a-blog.html', title="Add a Blog", 
        blog_title="" , blog="" , title_error="" , blog_error="")


@app.route('/newpost', methods=['POST'])
def added_blog():

    owner = User.query.filter_by(username=session['username']).first()
    date_stamp = datetime.datetime.now()
    blog_title = request.form['blog_title']
    blog = request.form['blog']
    blog_error = ""
    title_error = ""
    if blog_title == "" or blog == "":
        if blog_title == "":
            title_error = "Please fill in the title"
        if blog == "":
            blog_error = "Please fill in the blog"
        return render_template('add-a-blog.html',title="Add a Blog", 
            blog_title = blog_title, blog = blog, title_error = title_error, 
            blog_error = blog_error )
        
    else:    
        new_blog = Blog(blog_title, blog, date_stamp, owner)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blog?blog_id='+str(new_blog.blog_id))

if __name__ == '__main__':
    app.run()