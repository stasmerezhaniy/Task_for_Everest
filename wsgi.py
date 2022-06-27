import time

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, redirect, render_template, url_for
from flask_admin import Admin
from flask_admin import helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user, Security, SQLAlchemyUserDatastore, UserMixin
import datetime
from celery import Celery
from celery.result import AsyncResult


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///admin.db'
app.config['SECRET_KEY'] = 'mysecret'
app.config['FLASK_ADMIN_SWATCH'] = 'sandstone'
app.config['SECURITY_PASSWORD_SALT'] = "none"
app.config['SECURITY_POST_LOGIN_VIEW'] = '/admin/'
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/admin/'
app.config['SECURITY_POST_REGISTER_VIEW'] = '/admin/'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# app.config['CELERY_BROKER_URL'] = 'redis://localhost'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost'

# app.config.update(CELERY_CONFIG={
#     'broker_url': 'redis://localhost',
#     'result_backend': 'redis://localhost',
# })
# celery = Celery(app.config, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)

db = SQLAlchemy(app)

roles_users_table = db.Table('roles_users',
                            db.Column('users_id', db.Integer(), db.ForeignKey('users.id')),
                            db.Column('roles_id', db.Integer(), db.ForeignKey('roles.id')))


class Items(db.Model):
    # __tablename__ = 'Items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    color =db.Column(db.String(30))
    waight = db.Column(db.Integer)
    price = db.Column(db.Integer)
    char = db.Column(db.String(100))


class Address(db.Model):
    def __init__(self, id=None, country=None, city=None, address=None):
        self.id = id
        self.country = country
        self.city = city
        self.address = address

    id = db.Column('id', db.Integer, primary_key=True)
    country = db.Column('country', db.Unicode)
    city = db.Column('city', db.Unicode)
    address = db.Column('address', db.Unicode)
    # column_filters = ['country', 'city', 'address']

    # def __init__(self):
    #     column_filters = ('country', 'city', 'address')


class FilterAddress(ModelView):
    column_filters = ['country', 'city', 'address']


class Roles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(80))
    active = db.Column(db.Boolean())

    roles = db.relationship('Roles', secondary=roles_users_table, backref='user', lazy=True)


user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
security = Security(app, user_datastore)


# @app.before_first_request
def create_user():
    # db.drop_all()
    db.create_all()
    user_datastore.create_user(email='admin', password='admin')
    db.session.commit()


admin = Admin(app, name='Admin', base_template='my_master.html', template_mode='bootstrap3')


class UserModelView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and
                current_user.is_authenticated)

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('security.login'))

    column_list = ['email', 'password']


admin.add_view(UserModelView(Users, db.session))


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        get_url=url_for,
        h=admin_helpers
    )


@app.route('/')
def index():
    return render_template('index.html')

REDIS_URL = 'redis://redis:6379/0'
BROKER_URL = 'amqp://admin:mypass@rabbit//'

CELERY = Celery('tasks',
                backend=REDIS_URL,
                broker=BROKER_URL)

CELERY.conf.accept_content = ['json', 'msgpack']
CELERY.conf.result_serializer = 'msgpack'


def get_job(job_id):
    return AsyncResult(job_id, app=CELERY)


@CELERY.task()
def image_demension():
    time.sleep(60)
    location = datetime.datetime.now()
    print(location)

    return location


admin.add_view(ModelView(Items, db.session))
admin.add_view(FilterAddress(Address, db.session))

if __name__ == '__main__':

    db.create_all()
    items = Items()
    db.session.add(items)


    app.run(debug=True)