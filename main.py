from flask import Flask, render_template, redirect, flash, url_for, session, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm as Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Length
from config import DevConfig
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config.from_object(DevConfig)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

tags = db.Table('post_tags',
    db.Column('post_id', db.Integer(), db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer(), db.ForeignKey('tag.id'))
)

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
            return "<Tag - id={} title={}".format(self.id, self.title)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255),nullable=False)
    text = db.Column(db.String(255))
    date = db.Column(db.DateTime(), default=datetime.now)
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))
    def __repr__(self):
        return "<Comment- text={}".format(self.text[:15] )


class CommentForm(Form):
    name = StringField('Name',validators=[DataRequired(), Length(max=255)])
    text = TextAreaField(u'Comment',validators=[DataRequired()])


def sidebar_data():
    recent = Post.query.order_by(
        Post.publish_date.desc()
    ).limit(5).all()

    top_tags = db.session.query(
        Tag, func.count(tags.c.post_id).label('total')
    ).join(
        tags
    ).group_by(Tag).limit(5).all() #.order_by('total DESC')#
    return recent, top_tags

blog_blueprint = Blueprint(
    'blog',
    __name__,
    template_folder='templates/blog',
    url_prefix='/blog'
)


@app.route('/')
def index():
    return redirect(url_for('blog.home'))


@blog_blueprint.route('/')
@blog_blueprint.route('/<int:page>')
def home(page=1):
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page,app.config['POST_PER_PAGE'],False)
    recent,top_tags=sidebar_data()
    return render_template('home.html', posts=posts, recent=recent, top_tags=top_tags)


@blog_blueprint.route('/post/<int:post_id>', methods=('GET','POST'))
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        comment=Comment()
        comment.name = form.name.data
        comment.text=form.text.data
        comment.post_id=post_id
        try:
            db.session.add(comment)
            db.session.commit()
        except Exception as e:
            flash('Error adding your comment: %s' % str(e), 'error')
            db.session.rollback()
        else:
            flash('Comment added', 'info')
        return redirect(url_for('post', post_id=post_id))

    post = Post.query.get_or_404(post_id)
    tags = post.tags
    post.user = User.query.get_or_404(post.user_id) #hack
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()
    return render_template('post.html',post=post,tags=tags,comments=comments,recent=recent,top_tags=top_tags,form=form)


@blog_blueprint.route('/posts_by_tag/<string:tag_name>')
def posts_by_tag(tag_name):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template('tag.html',tag=tag,posts=posts,recent=recent,top_tags=top_tags)


@blog_blueprint.route('/posts_by_user/<string:username>')
def posts_by_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.publish_date.desc()).all()
    recent,top_tags=sidebar_data()
    return render_template('user.html', user=user,posts=posts,recent=recent,top_tags=top_tags)


@blog_blueprint.before_request
def before_request():
     session['page_loads']  = session.get('page_loads',0)+1
     print(' before reqeust ----------------------------- {}'.format(session.get('page_loads')))

@blog_blueprint.teardown_request
def teardown_request(exception=None):
     print(' teardown_request -----------------------------')

@blog_blueprint.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404

app.register_blueprint(blog_blueprint)
if __name__ == '__main__':
    app.run()
