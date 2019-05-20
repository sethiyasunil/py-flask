from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DevConfig
from datetime import datetime

app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    __tablename__ = 'internal_users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255),nullable=False,unique=True, index=True)
    password = db.Column(db.String(255))
    posts = db.relationship(
     'Post',
     backref='internal_users',
     lazy='dynamic'
    )

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return "<User- id={} username={} password={}>".format(self.id, self.username, self.password)


tags = db.Table('post_tags',
    db.Column('post_id', db.Integer(), db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer(), db.ForeignKey('tag.id'))
)


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255),nullable=False)
    text = db.Column(db.String(255))
    publish_date = db.Column(db.DateTime(), default=datetime.now)
    user_id = db.Column(db.Integer(), db.ForeignKey('internal_users.id'))
    comments = db.relationship(
        'Comment',
        backref='post',
        lazy='dynamic'
        )
    tags= db.relationship(
        'Tag',
        secondary=tags,
        backref=db.backref('posts', lazy='dynamic')
        )

    def __init__(self, title):
        self.title = title

    def __repr__(self):
        return "<Post- id={} title={} user_id={}>".format(self.id, self.title, self.user_id )

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255),nullable=False,unique=True)
    def __init__(self, title):
        self.title = title
    def __repr__(self):
        return "<Tag- id={} title={}>".format(self.id, self.title)

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    text = db.Column(db.String(255))
    date = db.Column(db.DateTime(), default=datetime.now)
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))
    def __repr__(self):
        return "<Comment- text={}".format(self.text[:15] )


@app.route('/')
def home():
    return '<h1>Hello world</h1>'

if __name__ == '__main__':
    app.run()
