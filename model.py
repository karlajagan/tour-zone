
from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

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