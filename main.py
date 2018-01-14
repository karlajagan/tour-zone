from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fsfsdfsdfsd'

class Blog(db.Model):

    blog_id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(100))
    blog = db.Column(db.String(300))
    
    def __init__(self, blog_title, blog):
        self.blog_title = blog_title
        self.blog = blog
        
@app.route('/blog', methods=['GET'])
def index():

    blog_id = request.args.get('blog_id', '')
    if blog_id == "":
        blogs = Blog.query.order_by(Blog.blog_id.desc()).all()
        return render_template('display_blogs.html', title="Build a Blog Project", 
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
        new_blog = Blog(blog_title,blog)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/blog?blog_id='+str(new_blog.blog_id))

if __name__ == '__main__':
    app.run()