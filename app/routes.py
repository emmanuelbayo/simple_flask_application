from flask import Blueprint,render_template,request,redirect,url_for,flash,session
import re
from app import mysql
from app import bcrypt
from app import db, mail
from .models import User
from flask_mail import Message

home = Blueprint('home',__name__)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9]+@[a-zA-z0-9]+\.[a-zA-Z]*$')
NAME_REGEX  = re.compile(r'^[a-zA-Z]*$')
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9]*$')

@home.route('/', methods=['GET','POST'])
def login():
    
    if 'user' in session:
        return redirect(url_for('home.dashboard'))

    title='Login'
    errors = {
            'email':[],
            'password':[]
        }
    
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        error = False
        error_login = False
            
        if not EMAIL_REGEX.match(email):
            errors['email'].append('Email must be only alphanumeric characters.')
            error=True
        
        if len(email)<8:
            errors['email'].append('Email must be at least 8 characters.')
            error=True
        
        if len(password)<8:
            errors['password'].append('Password must be at least 8 characters.')
            error = True
            
        
        if error == False:
            query_user = "SELECT * FROM users WHERE email = :email LIMIT 1"
            query_data = {'email':email}
            user_login = mysql.query_db(query_user,query_data)

            if len(user_login)<1:
                flash('Email not registered','danger')
                error_login = True
            
            elif not bcrypt.check_password_hash(user_login[0]['password'], password):
                flash("Email/password does not match", 'danger')
                error_login = True

            if error_login == True:
                return redirect(url_for('home.login'))
            
            else :
                print("You are logged")
                session['user']=user_login[0]
                return redirect(url_for('home.dashboard'))
                
    return render_template('auth/login.html',title=title,errors_e=errors['email'],errors_p=errors['password'])

@home.route('/register',methods=['GET','POST'])
def register():

    if 'user' in session:
        return redirect(url_for('home.dashboard'))

    title='Register'

    errors ={
        'username':[],
        'firstname':[],
        'lastname':[],
        'email':[],
        'password_confirm':[]
        }

    if request.method =='POST':
        
        username = request.form['username']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        error=False

        if not NAME_REGEX.match(firstname):
            errors['firstname'].append('Names must be alphabetic characters.')
            error=True
        if not NAME_REGEX.match(lastname):
            errors['lastname'].append('Names must be alphabetic characters.')
            error=True
        if not USERNAME_REGEX.match(username):
            errors['username'].append('username must be alphanumeric characters.')
            error=True
        if len(firstname)<2:
            errors['firstname'].append('First name must be at least 2 characters.')
            error=True
        if len(lastname)<2:
            errors['lastname'].append('Last name must be at least 2 characters.')
            error=True
        if not EMAIL_REGEX.match(email):
            errors['email'].append('Email must be only alphanumeric characters.')
            error=True
        if len(email)<8:
            errors['email'].append('Email must be at least 8 characters.')
            error=True
        if len(password)<8 or len(password_confirm)<8 :
            errors['password_confirm'].append('Password must be at least 8 characters.')
            error=True
        if password != password_confirm:
            errors['password_confirm'].append('Password must match!')
            error=True

        if error == False:
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            
            data = {
                'username':username,
                'firstname':firstname,
                'lastname':lastname,
                'email':email,
                'image_profile':'default.jpeg',
                'password':password_hash
            }
            query_email="SELECT * FROM users WHERE email = :email LIMIT 1"
            data_email={
                'email':email
            }
            result = mysql.query_db(query_email,data_email)
            if result:
                flash('This email is already used','danger')
            else:
                user = User(username=username,firstname=firstname,lastname=lastname,email=email,password=password_hash)
                db.session.add(user)
                db.session.commit()
                flash('your account has been created','success')
    return render_template('auth/register.html',title=title,errors_u=errors['username'],
            errors_f=errors['firstname'],errors_l=errors['lastname'],
            errors_e=errors['email'],errors_p=errors['password_confirm'])


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='test.application.flask.2020@gmail.com',
                  recipients=[user.email])
    msg.html = render_template('mail.html',token=token,username=user.username)
    mail.send(msg)

@home.route('/reset_password',methods=['GET','POST'])
def forgot_password():
    title='Password forgot'
    error = False
    errors_e = []
    if 'user' in session:
        return redirect(url_for('home.dashboard'))
    if request.method == 'POST':
        email = request.form['email']

        if len(email)<8 :
            errors_e.append('Email must be at least 8 characters.')
            error = True
        
        if not EMAIL_REGEX.match(email):
            errors_e.append('Email must be only alphanumeric characters.')
            error = True
        
        if error == False:
            user = User.query.filter_by(email=email).first()
            if not user:
                flash('Email not registered','danger')
                return redirect(url_for('home.forgot_password'))
            else:
                send_reset_email(user)
                flash('An email has been sent with instructions to reset your password.', 'info')
                return redirect(url_for('home.login'))

    return render_template('auth/email.html',title=title)

@home.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    title='Reset password'
    errors_p=[]
    error = False
    if 'user' in session:
        return redirect(url_for('home.dashboard'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('home.forgot_password'))
    if request.method == 'POST':
        password = request.form['password']
        password_confirm = request.form['password_confirm']

        if len(password)<8 or len(password_confirm)<8:
            errors_p.append('Password must be at least 8 characters.')
            error = True
        if password != password_confirm:
            errors_p.append('Password must match!')
            error = True
        
        if error == False:
            hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user.password = hash_password
            db.session.commit()
            flash('Your password has been updated! You are now able to log in', 'success')
            return redirect(url_for('home.login'))
    return render_template('auth/reset.html',title=title,errors_p=errors_p)

@home.route('/dashboard')
def dashboard():
    title = 'Dashboard'
    if not 'user' in session:
        flash('You must be connected to access at this page !','info')
        return redirect(url_for('home.login'))
    return render_template('home/dashboard.html',title=title,
            username=session['user']['username'],session=session,user='user')

@home.route('/logout')
def logout():
    if not 'user' in session:
        flash('User already logged out','info')
        return redirect(url_for('home.login'))
    session.pop('user')
    flash('You are logged out !','success')
    return redirect(url_for('home.login'))