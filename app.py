# import libraries
from flask import Flask, session, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import sqlite3 as sql
from forms import *
import datetime
# -----------------

# create flask app
app = Flask(__name__)
app.config.from_object('config')

# connect sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///E:\\my_file\\Projectes\\flaskBlog\\blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# create user table in blog.db to assign users in it
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    posts = db.relationship('Post', backref='user')

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    def to_json(self):
        dict = {k:v for k,v in self.__dict__.items() if k != '_sa_instance_state'}
        return dict
    
# create post table in blog.db to contain all posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(1500), nullable=False)
    content = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)
    
# create the login page
@app.route('/login', methods=['POST', 'GET'])
def login(): # an exisiting user
    form = Myform()
    message = ''
    if request.method == 'POST':
        session.pop('logged_in', None)
        if form.validate_on_submit():
            getemail = request.form.get('email')
            getpassword = request.form.get('password')
            all_emails = [i[0] for i in User.query.with_entities(User.email).all()]
            if str(getemail) in all_emails:
                user = User.query.filter_by(email=getemail).first()
                password = user.password

                if password == str(getpassword):
                    the_dict = user.to_json()
                    session['logged_in'] = the_dict

                    message = 'hello %s' %str(the_dict['name'])
                    return redirect(url_for('dashboard'))
                else:
                    message = 'password is not correct!'
            else:
                message = 'email not registered!'
    return render_template('login.html', form=form, message=message)

# create the main page that will show all posts that have been published
@app.route('/')
def index():
    name, message = '', ''
    posts = Post.query.all()
    all_post = []
    if posts:
        if len(posts) <=6:
            for post in posts:
                date_posted = post.date_posted.strftime("%d %B, %Y")
                if len(str(post.content)) <=145:
                    limit_content = str(post.content)
                else:
                    limit_content = str(post.content)[:145]+'....'
                all_post.append([post.title,post.content, post.user.name,date_posted, limit_content, post.id])
        else:
            for i in range(0, 6+1):
                post = posts[i]
                date_posted = post.date_posted.strftime("%d %B, %Y")
                if len(str(post.content)) <=145:
                    limit_content = str(post.content)
                else:
                    limit_content = str(post.content)[:145]+'....'
                all_post.append([post.title,post.content, post.user.name, date_posted, limit_content, post.id])
    else:
        message = 'No post has been sent yet!'
    current_user = session.get('logged_in', False)
    if current_user:
        name = current_user['name']
    return render_template('index2.html', posts=all_post, user=name, message=message)

@app.route('/post<int:postid>')
def post(postid):
    post = Post.query.filter_by(id=postid).first()
    return render_template('post.html', post=post)

@app.route('/posts<int:userid>')
def posts(userid):
    message= ''
    user_posts = Post.query.filter_by(user_id=userid).all()
    all_post = []
    if user_posts:
        for post in user_posts:
            date_posted = post.date_posted.strftime("%d %B, %Y")
            if len(str(post.content)) <=145:
                limit_content = str(post.content)
            else:
                limit_content = str(post.content)[:145]+'....'
            all_post.append([post.title,post.content, post.user.name, date_posted, limit_content, post.id])
    else:
        message = 'You have not sent any post yet!'
    return render_template('posts.html', posts=all_post, message=message)

# create dashboard to enable the user to publish and delete posts
@app.route('/dash', methods=['POST', 'GET'])
def dashboard():
    current_user = session.get('logged_in', False)
    if current_user:
        name = current_user['name']
        user = User.query.filter_by(name=name).first()
        print(user.name, user.id)
        return render_template('dash.html', user=user)
    else:
        meassage = 'Login First Please!'
        return redirect(url_for('login', meassage=meassage))

# create add post page to add new posts
@app.route('/addpost', methods=['POST', 'GET'])
def addPost():
    form = Addform()
    message = ''
    if request.method == 'POST':
        if form.validate_on_submit():
            title = request.form.get('title')
            content = request.form.get('content')
            current_user = session.get('logged_in', False)
            if current_user:
                try:
                    user = User.query.filter_by(id=current_user['id']).first()
                    post = Post(title=title, content=content, user=user)
                    db.session.add(post)
                    db.session.commit()
                    message = 'Post send successfully'
                except Exception as e:
                    raise 'Sorry there is somethine wrong happend!'
            else:
                message = 'User not found!'
    return render_template('add.html', message=message, form=form)

# create delete post page to delete posts
@app.route('/delpost<int:postid>', methods=['POST', 'GET', 'DELETE'])
def deletePost(postid):
    # form = Delform()
    message = ''
    # if request.method == 'POST':
        # if form.validate_on_submit():
        #     post_id = request.form.get('number')
    if session.get('logged_in', False):
        post = Post.query.filter_by(id=postid).first()
        user_id = session['logged_in']['id']

        if post.user_id == user_id:
            Post.query.filter_by(id=postid).delete()
            db.session.commit()
            message = 'Post deleted successfully'
        else:
            message = 'You can not delete this post!'
    else:
        message = 'Something went wrong!'
    return render_template('del.html', message=message)

# create logout page to pop the user from session
@app.route('/logout')
def logout():
    current_user = session.get('logged_in', False)
    if current_user:
        session.pop('logged_in', None)
    return redirect(url_for('index'))

# create register page to assign new user to database
@app.route('/register', methods=['POST', 'GET'])
def register(): # add new user to database
    message = ''
    status = False
    form = Regform()
    if request.method == 'POST':
        if form.validate_on_submit():
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')

            all_emails = [i[0] for i in User.query.with_entities(User.email).all()]
            if email not in all_emails:
                new_user = User(name, email, password)
                db.session.add(new_user)
                db.session.commit()
                message = 'New user resigsted'
                status = True
            else:
                message = 'The email is already registed!'
                # sleep(5)
                # return redirect(url_for('register'))
    return render_template('reg.html', form=form, message=message, status=status)


if __name__ == '__main__':
    app.run(debug=True)   
