from flask import Flask
from flask_migrate import Migrate
from mysqlconnection import MySQLConnector
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask.ext.babel import Babel
import config_mail
import os

config_mail.setvar()

app = Flask(__name__)

mysql = MySQLConnector(app)

app.config['SECRET_KEY'] = 'fa047641f3e506c87466579192ea25d7'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD')

mail = Mail(app)

bcrypt = Bcrypt(app)

db = mysql.get_db()

def create_app():
    
    migrate = Migrate(app,db)

    from app import models

    from .routes import home as home_blueprint

    app.register_blueprint(home_blueprint)

    return app