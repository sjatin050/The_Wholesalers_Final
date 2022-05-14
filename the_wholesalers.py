import os
from re import M, U
from flask import Flask, render_template, request, redirect,session,url_for,g,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Length,EqualTo,Email
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_user,logout_user,current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_mail import Mail,Message

basedir=os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# app.secret_key=os.urandom(24)
app.config['SECRET_KEY']="ThisIsMYFirstFlaskApp"

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///stock.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///place_the_order.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///history.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///pending_payments.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///logindetails.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)

#for sending mail for forget password
# open this for reference https://www.androidauthority.com/gmail-smtp-settings-801100/
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']='587'
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']='the.wholesalers.mailid@gmail.com'
app.config['MAIL_PASSWORD']='J@tin123'

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

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
    def get_token(self,expires_sec=300):
        serial=Serializer(app.config['SECRET_KEY'],expires_in=expires_sec)
        return serial.dumps({'user_id':self.id}).decode('utf-8')

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



class Orders(db.Model):
    __tablename__='orders'
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



class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    def __init__(self, name,qty):
        self.name = name
        self.qty = qty

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
    # if g.user:
        return render_template('welcome.html')
    # return redirect('login')

# @app.route('/')
# def gabru1():
#     # if g.user:
#         return render_template('welcome1.html')
#     # return redirect('login')

@app.route('/about')
def about():
    # if g.user:
        return render_template('About.html')
    # return redirect('login')

@app.route('/tac')
def tac():
    # if g.user:
        return render_template('Terms_conditions.html')
    # return redirect('login')


@app.route('/order', methods=['GET', 'POST'])
def ord():
    # if g.user:
        if request.method == 'POST':
            cust_name = request.form['cust_name']
            cust_address = request.form['cust_address']
            desc = request.form['desc']
            amount = request.form['amount']

            order = Orders(cust_name=cust_name, cust_address=cust_address,desc=desc,amount=amount)
            db.session.add(order)
            db.session.commit()

        return render_template('placing_order.html')
    # return redirect('login')

@app.route('/orders', methods=['GET', 'POST'])
def ords():
    # if g.user:
        return render_template('orders.html')
    # return redirect('login')

@app.route('/placed_orders', methods=['GET', 'POST'])
def placed_ord():
    # if g.user:
        order = Orders.query.all()
        return render_template('pending_orders.html', order=order)
    # return redirect('login')

@app.route('/orders_his', methods=['GET', 'POST'])
def orders_his():
    # if g.user:
        order = History.query.all()
        return render_template('history.html', order=order)
    # return redirect('login')


@app.route('/pay/<int:id>')
def pending_payments(id):
    # if g.user:
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
    # return redirect('login')


@app.route('/his/<int:id>')
def history(id):
    # if g.user:
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
    # return redirect('login')


@app.route('/his1/<int:id>')
def history1(id):
    # if g.user:
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
    # return redirect('login')

@app.route('/pending_pay_view')
def pending_pay_view():
    # if g.user:
        order=Pending_payments.query.all()
        return render_template('pending_payments.html',order=order)
    # return redirect('login')

@app.route('/update1/<int:id>', methods=['GET', 'POST'])
def update1(id):
    # if g.user:
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
    # return redirect('login')

@app.route('/delete1/<int:id>')
def delete1(id):
    # if g.user:
        order = Orders.query.filter_by(id=id).first()
        db.session.delete(order)
        db.session.commit()
        return redirect("/placed_orders")
    # return redirect('login')


@app.route('/stock', methods=['GET', 'POST'])
def stk():
    # if g.user:
        if request.method == 'POST':
            name = request.form['name']
            qty = request.form['qty']
            stock = Stock(name=name, qty=qty)
            db.session.add(stock)
            db.session.commit()

        return render_template('stock.html')
    # return redirect('login')


@app.route('/stock_view', methods=['GET', 'POST'])
def stk_view():
    # if g.user:
        stock = Stock.query.all()
        return render_template('stock_view.html', stock=stock)
    # return redirect('login')

@app.route('/welcome_stocks', methods=['GET', 'POST'])
def welcome_stock():
    # if g.user:
        return render_template('welcome_stock.html')
    # return redirect('login')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    # if g.user:
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
    # return redirect('login')

@app.route('/delete/<int:id>')
def delete(id):
    # if g.user:
        stock = Stock.query.filter_by(id=id).first()
        db.session.delete(stock)
        db.session.commit()
        return redirect("/stock_view")
    # return redirect('login')

if __name__ == "__main__":
    app.run()
