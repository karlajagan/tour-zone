from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpw@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fsfsdfsdfsd'

class Blog(db.Model):

    blog_id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(100))
    blog = db.Column(db.String(300))
    date_stamp = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, blog_title, blog, date_stamp, owner):
        self.blog_title = blog_title
        self.blog = blog
        self.date_stamp = date_stamp
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login') 

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('logged in')
            return redirect('/blog')
        else:
            flash('User password is incorrect, or user does not exist', 'error')

    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(email=email).first()
        
        if not existing_user:
            new_user = User(email,password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/blog')
        else:
            return '<h1>Duplicate user </h1>'

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')
        
@app.route('/blog', methods=['GET'])
def index():

    blog_id = request.args.get('blog_id', '')
    if blog_id == "":
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

    return render_template('add-a-blog.html', title="Add a Blog", 
        blog_title="" , blog="" , title_error="" , blog_error="")


@app.route('/newpost', methods=['POST'])
def added_blog():

    owner = User.query.filter_by(email=session['email']).first()
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