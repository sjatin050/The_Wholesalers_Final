# A module is a collection of source files and build settings that allow you to divide your project into discrete units of functionality. 
# Your project can have one or many modules, and one module may use another module as a dependency. 
# You can independently build, test, and debug each module.

import os

from flask import Flask, render_template, request, redirect,session,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Length,EqualTo,Email
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_user,logout_user,current_user,login_required
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail,Message
# Why use itsdangerous is to ensure that your encrypted data has not been modified, because the original data 
# cannot be re solved after modification, and the content cannot be solved after timeout
# for Serializer --> https://itsdangerous.palletsprojects.com/en/2.0.x/jws/

# the __file__ name points to the filename of the current module
basedir=os.path.abspath(os.path.dirname(__file__))

# dirname is used to get the path of the specific directory
# abspath is used for normalized version of the path which can be
# directly send to the parameter of the fn

# redirect is used to redirect to the another location

# os module provides fn for creating or removing some directory
# The OS module in Python provides functions for interacting with the operating system
# OS comes under Python’s standard utility modules. This module provides a portable way of using operating system-dependent functionality. 

# render template is used for generating output from a template

# request creates a Request object based on the environment

# url_for is used to create a url to prevent the overhead of having to
# change urls throughout application
# if we do without it then url if url of something is to be changed then
# we have to do it every where the url is present
# url_for is used to call defined functions

# g is an object for storing data during the application context of a running Flask web app

# flash --> it is used to flash message on the screen

# Session is the time interval when a client logs into a server and logs out of it. 
# The data, which is needed to be held across this session, is stored in the client browser. 
# A session with each client is assigned a Session ID.

# Bcrypt--> The bcrypt is a password hashing function based on the Blowfish cipher.
# Blowfish not be used to encrypt files larger than 4 GB due to its small block size
# used functions bcrypt.generate_password_hash() and bcrypt.check_password_hash()

# FlaskForm Class. Flask provides an alternative to web forms by creating a form class in the application, 
# implementing the fields in the template and handling the data back in the application.

# Flask WTForms is a library that makes form handling easy and structured. 
# It also ensures the effective handling of form rendering, validation, and security


#__name__ is the name of the current Python module.
#  The app needs to know where it’s located to set up some paths, and __name__ is a convenient way to tell it that.
app = Flask(__name__)
# In other words: Flask is a class,and you're creating one instance of that class.


# Flask constructor takes name of the current module
# route fn tells which url to be called  with the associated fn


# The secret key is needed to keep the client-side sessions secure.
# below both ways are correct to create a Secret key
# app.secret_key=os.urandom(24)
app.config['SECRET_KEY']="ThisIsMYFirstFlaskApp"
# to use the session in flask we need to set secret key which encrypts
# the cookies and save them to browser
# by using SQLALCHEMY_DATABASE_URI we connect database to the flask
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///stock.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///place_the_order.db"
# Uniform Resource Identifier (URI)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///history.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///pending_payments.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///logindetails.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemy and Bcrypt are classes and we are making instance of these classes to use their functionalities
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)



# sqlite is database storage engine used to store and retrieve structured data from files

# sqlalchemy is the library that facilitates the communication between python programs and databases

#for sending mail for forget password
# open this for reference https://www.androidauthority.com/gmail-smtp-settings-801100/
# smtp --> Simple Mail Transfer Protocol
app.config['MAIL_SERVER']='smtp.gmail.com'
# A port in networking is a software-defined number associated to a network protocol that receives or transmits communication for a specific service. 
app.config['MAIL_PORT']='587'
# Transport Layer Security (TLS) is the successor protocol to SSL. TLS is an improved version of SSL. 
# It works in much the same way as the SSL, using encryption to protect the transfer of data and information. 
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']='the.wholesalers.app.flask@gmail.com'
app.config['MAIL_PASSWORD']='nexmijcukenuwdxi'

mail=Mail(app)
# # Route for handling the login page logic
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != 'admin' or request.form['password'] != 'admin':
#             error = 'Invalid Credentials. Please try again.'
#         else:
#             return redirect(url_for('welcome.html'))
#     return render_template('login.html', error=error)

# for reference of flask-login read this https://flask-login.readthedocs.io/en/latest/
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash(f'Please Register First',category='danger')
    return redirect(url_for('register'))

# is_authenticated , is_active , is_anonymous , get_id()
# To make implementing a user class easier, you can inherit from "UserMixin", which

class User(db.Model,UserMixin):
    # __tablename__='login'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True,nullable=False)
    image_file = db.Column(db.String(20), nullable=False,default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)

    # below code is for if we need to reset the password
    # time window is 300 seconds

    # how to generate token --> see this
    # >>> from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
    # >>> from the_wholesalers import app
    # >>> serial=Serializer(app.config['SECRET_KEY'],expires_in=120)
    # >>> token=serial.dumps({'user_id':2})       
    # >>> print(token)
    # b'eyJhbGciOiJIUzUxMiIsImlhdCI6MTY1NjgzNzE4MiwiZXhwIjoxNjU2ODM3MzAyfQ.eyJ1c2VyX2lkIjoyfQ.OTXPYN8PvjLlZ8Kq-IseaCfbWjwi0KnJadTVQdKYY1c75J7NPKaSLP5FGOZ-GK3Cn4PtC9k0Z5zxf4_Qx3YUmg'
    # >>> token=serial.dumps({'user_id':2}).decode('utf-8')
    # >>> token
    # 'eyJhbGciOiJIUzUxMiIsImlhdCI6MTY1NjgzNzIzNCwiZXhwIjoxNjU2ODM3MzU0fQ.eyJ1c2VyX2lkIjoyfQ.HO3rQvJLJz-GXZ1YgxRIM0p9UsjzrW2GtAAQJZPmAH2o7x-oxX-eu3ndOkA7V1mJHLRTG8Tq7sbM6C51wGmkjA'
    # >>> serial.loads(token)
    # {'user_id': 2}
    # >>> serial.loads(token)['user_id']
    # 2
    # >>> User.query.get(2)

    def get_token(self,expires_sec=300):
        serial=Serializer(app.config['SECRET_KEY'],expires_in=expires_sec)
        return serial.dumps({'user_id':self.id}).decode('utf-8')

# we are using staticmethod because we do'nt want to acces the functions of User class we only 
# need the things which are in token , so it it will help us to use token directly without using self
#  if staticmethod not used code will  be:
    # def verify_token(self,token):
    #     serial=Serializer(app.config['SECRET_KEY'])
    #     try:
    #         user_id=serial.loads(token)['user_id']
    #     except:
    #         return None
    #     return User.query.get(user_id)

    @staticmethod
    def verify_token(token):
        serial=Serializer(app.config['SECRET_KEY'])
        try:
            user_id=serial.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'{self.username} : {self.email} : {self.date_created.strftime("%d/%m/%Y, %H:%M:%S")}'

class RegistrationForm(FlaskForm):
    username = StringField(label='Username',validators=[DataRequired(),Length(min=3,max=20)])
    email=StringField(label='Email',validators=[DataRequired(),Email()])
    password=PasswordField(label='Password',validators=[DataRequired(),Length(min=6,max=16)])
    confirm_password=PasswordField(label='Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField(label='Sign Up',validators=[DataRequired()])

class LoginForm(FlaskForm):
    email=StringField(label='Email',validators=[DataRequired(),Email()])
    password=PasswordField(label='Password',validators=[DataRequired(),Length(min=6,max=16)])
    submit=SubmitField(label='Login',validators=[DataRequired()])

class ResetRequestForm(FlaskForm):
    email=StringField(label='Email',validators=[DataRequired(),Email()])
    submit=SubmitField(label='Reset Password',validators=[DataRequired()])

class ResetPasswordForm(FlaskForm):
    password=PasswordField(label='Password',validators=[DataRequired(),Length(min=6,max=16)])
    confirm_password=PasswordField(label='Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit=SubmitField(label='Change Password',validators=[DataRequired()])


# db.Model baseclass of all the models is db.Model

# to create new database just follow the steps :
# 1st open python environment 
# 2nd now write this--> from the_wholasalers import User   // jiska bhi database banna hai User ki jagha likh do bass
# 3rd now write this--> db.create_all() // this will create the User database

# to know what is stored in your database and display data in terminal use below commands: 
# 1st open python environment 
# 2nd now write this--> from the_wholasalers import User   // we can also use Orders, Pending_payments, History and Stock other than User
# 3rd now write this--> User.query.all()

# place_the_order.db
class Orders(db.Model):
    __tablename__='orders'
    id = db.Column(db.Integer, primary_key=True)
    cust_name = db.Column(db.String(200), nullable=False)
    cust_address = db.Column(db.String(500), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    # __init__ is a constructor
    def __init__(self,cust_name,cust_address,desc,amount):
        self.cust_name=cust_name
        self.cust_address=cust_address
        self.desc=desc
        self.amount=amount


# pending_payments.db
class Pending_payments(db.Model):
    __tablename__='pending_payments'
    id = db.Column(db.Integer, primary_key=True)
    cust_name = db.Column(db.String(200), nullable=False)
    cust_address = db.Column(db.String(500), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    def __init__(self,cust_name,cust_address,desc,amount):
        self.cust_name=cust_name
        self.cust_address=cust_address
        self.desc=desc
        self.amount=amount


# history.db
class History(db.Model):
    __tablename__='history'
    id = db.Column(db.Integer, primary_key=True)
    cust_name = db.Column(db.String(200), nullable=False)
    cust_address = db.Column(db.String(500), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    def __init__(self,cust_name,cust_address,desc,amount):
        self.cust_name=cust_name
        self.cust_address=cust_address
        self.desc=desc
        self.amount=amount


#  stock.db
class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def __init__(self, name,qty):
        self.name = name
        self.qty = qty
    

# App Routing means mapping the URLs to a specific function that will handle the logic for that URL. 
# Modern web frameworks use more meaningful URLs to help users remember the URLs and make navigation simpler.
#  Example: In our application, the URL (“/”) is associated with the root URL

# UTF-8 is one of the most commonly used encodings, and Python often defaults to using it. 
# UTF stands for “Unicode Transformation Format”, and the '8' means that 8-bit values are used in the encoding.

# GET is used to request data from a specified resource.
# POST is used to send data to a server to create/update a resource.

# render_template() is used to pass information to html files , see below fun as example


@app.route('/register',methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('gabru'))
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is None:
            user=User.query.filter_by(username=form.username.data).first()
            if user is None:
                if (form.password.data)==(form.confirm_password.data):
                    encrypted_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                    user=User(username=form.username.data,email=form.email.data,password=encrypted_password)
                    db.session.add(user)
                    db.session.commit()
                    flash(f'Account created successfully for {form.username.data}',category='success')
                    return redirect(url_for('login'))
                else:
                    flash(f'Both Passwords are not Same',category='danger')
            else:
                flash(f'username already taken',category='danger')
        else:
            flash(f'email id already registered',category='danger')

    return render_template('register.html',title="Register",form=form)

# login_user() used to make session and make it as Current_User

@app.route('/login',methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('gabru'))
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user)
            flash(f'Login Successful for {form.email.data}',category='success')
            return redirect(url_for('gabru'))
        else:
            flash(f'Login Unsuccessful for {form.email.data}',category='danger')
    return render_template('login.html',title="login",form=form)

# logout_user() used to finish current session and current_user is logged out.

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# pip install flask-mail
# used to send mail if person forgets password
def send_mail(user):
    token=user.get_token()
    msg=Message('Password Reset Request',recipients=[user.email],sender='noreply@the_wholesalers.com')
    msg.body=f''' To reset your password. Please follow the link below

    This Link will be valid for 5 minutes:
    {url_for('reset_token',token=token,_external=True)}

    if you didn't send a password reset request. Please ignore this message
    
    
    '''
    mail.send(msg)


# using this to reset Password
@app.route('/reset_password',methods=['GET', 'POST'])
def reset_request():
    form=ResetRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            send_mail(user)
            flash('Reset request sent. Check your mail.','success')
            return redirect(url_for('login'))
        else:
            flash('Invalid Credentials','danger')
    return render_template('reset_request.html',title='Reset Request',form=form,legend="Reset Password")

# we use <token> to pass a variable in url of flask
@app.route('/reset_password/<token>',methods=['GET', 'POST'])
def reset_token(token):
    user=User.verify_token(token)
    if user is None:
        flash('That is invalid token or expired. Please try again.','warning')
        return redirect(url_for('reset_request'))

    form=ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password=hashed_password
        db.session.commit()
        flash('Password changed! Please Login!','success')
        return redirect(url_for('login'))
    return render_template('change_password.html',title="Change Password",legend="Change Password",form=form)



@app.route('/')
def gabru():
    return render_template('welcome.html')

# @app.route('/')
# def gabru1():
#     # if g.user:
#         return render_template('welcome1.html')
#     # return redirect('login')


# welcome page
@app.route('/about')
def about():
    return render_template('About.html')
   

# posting about
@app.route('/tac')
def tac():
    return render_template('Terms_conditions.html')

# posting the terms and condition

@app.route('/order', methods=['GET', 'POST'])
@login_required
def ord():
        if request.method == 'POST':
            cust_name = request.form['cust_name']
            cust_address = request.form['cust_address']
            desc = request.form['desc']
            amount = request.form['amount']

            order = Orders(cust_name=cust_name, cust_address=cust_address,desc=desc,amount=amount)
            db.session.add(order)
            db.session.commit()

        return render_template('placing_order.html')


# adds the order
# order=Orders... here init fn is called which creates the instance of the Orders class
# which is further used for the addition in the orders table
# and finally placing_order.html is shown where the order is successful

@app.route('/orders', methods=['GET', 'POST'])
@login_required
def ords():
        return render_template('orders.html')
    

# if u want to order give it here

@app.route('/placed_orders', methods=['GET', 'POST'])
@login_required
def placed_ord():
        order = Orders.query.all()
        return render_template('pending_orders.html', order=order)
    


# all the current orders

@app.route('/orders_his', methods=['GET', 'POST'])
@login_required
def orders_his():
        order = History.query.all()
        return render_template('history.html', order=order)
    

# history of all the orders

# to understand it better --> open orders.html and see where /pay/{{todo.id}} is written 
@app.route('/pay/<int:id>')
@login_required
def pending_payments(id):
        order = Orders.query.filter_by(id=id).first()
        cust_name = order.cust_name
        cust_address = order.cust_address
        desc = order.desc
        amount = order.amount
        pending_payments = Pending_payments(cust_name=cust_name, cust_address=cust_address,desc=desc,amount=amount)
        db.session.add(pending_payments)
        db.session.commit()
        db.session.delete(order)
        db.session.commit()
        order = Pending_payments.query.all()
        return render_template('pending_payments.html', order=order)


# if payment is not done but the order is delivered then order goes to the pending payment table

@app.route('/his/<int:id>')
@login_required
def history(id):
        order = Orders.query.filter_by(id=id).first()

        cust_name = order.cust_name
        cust_address = order.cust_address
        desc = order.desc
        amount = order.amount

        history = History(cust_name=cust_name, cust_address=cust_address,desc=desc,amount=amount)
        db.session.add(history)
        db.session.commit()
        db.session.delete(order)
        db.session.commit()
        order = History.query.all()
        return render_template('history.html', order=order)

# deletes from the table order and adds it to the history

@app.route('/his1/<int:id>')
@login_required
def history1(id):
        order = Pending_payments.query.filter_by(id=id).first()
        cust_name = order.cust_name
        cust_address = order.cust_address
        desc = order.desc
        amount = order.amount
        history = History(cust_name=cust_name, cust_address=cust_address,desc=desc,amount=amount)
        db.session.add(history)
        db.session.commit()
        db.session.delete(order)
        db.session.commit()
        order = History.query.all()
        return render_template('history.html', order=order)

# deletes from the table pending payments and adds it to the history

@app.route('/pending_pay_view')
@login_required
def pending_pay_view():
   
        order=Pending_payments.query.all()
        return render_template('pending_payments.html',order=order)
    

@app.route('/update1/<int:id>', methods=['GET', 'POST'])
@login_required
def update1(id):
        if request.method == 'POST':
            cust_name = request.form['cust_name']
            cust_address = request.form['cust_address']
            desc = request.form['desc']
            amount = request.form['amount']
            order = Orders.query.filter_by(id=id).first()
            order.cust_name = cust_name
            order.cust_address = cust_address
            order.desc = desc
            order.amount =amount
            db.session.add(order)
            db.session.commit()
            return redirect("/placed_orders")

        order = Orders.query.filter_by(id=id).first()
        return render_template('update_order.html', order=order)

@app.route('/delete1/<int:id>')
@login_required
def delete1(id):
        order = Orders.query.filter_by(id=id).first()
        db.session.delete(order)
        db.session.commit()
        return redirect("/placed_orders")


@app.route('/stock', methods=['GET', 'POST'])
@login_required
def stk():
        if request.method == 'POST':
            name = request.form['name']
            qty = request.form['qty']
            stock = Stock(name=name, qty=qty)
            db.session.add(stock)
            db.session.commit()

        return render_template('stock.html')

# adding stock with the data entered in the html form

@app.route('/stock_view', methods=['GET', 'POST'])
@login_required
def stk_view():
        stock = Stock.query.all()
        return render_template('stock_view.html', stock=stock)
    

# query all provides the full data of the Stock table

@app.route('/welcome_stocks', methods=['GET', 'POST'])
@login_required
def welcome_stock():
        return render_template('welcome_stock.html')
   

# redirect is basically used to redirect to the other url page
# while render template is used for posting the html file on the same url


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
        if request.method == 'POST':
            name = request.form['name']
            qty = request.form['qty']
            stock = Stock.query.filter_by(id=id).first()
            stock.name =name
            stock.qty = qty
            db.session.add(stock)
            db.session.commit()
            return redirect("/stock_view")

        stock = Stock.query.filter_by(id=id).first()
        return render_template('update_stock.html', stock=stock)
    

# get is used top request the data from the server
# post is used to send the data to the server to create / update
# by default it is get
# if we want to post
# then we name and quantity will be extracted from the html form and
# then the tuple is found which is to be updated
# by using render template we generate the changed output reflected by
# the html page named update_stock.html

@app.route('/delete/<int:id>')
@login_required
def delete(id):
        stock = Stock.query.filter_by(id=id).first()
        db.session.delete(stock)
        db.session.commit()
        return redirect("/stock_view")
    

# @app.route is uses for dynamic routing , basically it creates new url
# delete is the fn used to delete the stock with id (given as parameter) from the stock table
# stock will contain all the rows of the Stock table whose id matches with the given one
# db.session is responsible for all the connections with the database
# it tells to delete stock tuple to db.session
# commit tells that the changes made are to be finalized
# redirect relocates the given url

# it is like main fun in c++
if __name__ == "__main__":
    app.run()

# debug is set for true so that if there is any error that it will debug and show it
# port is used to change and set the host
