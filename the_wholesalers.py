import os
from flask import Flask, render_template, request, redirect,session,url_for,g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

basedir=os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.secret_key=os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///stock.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///place_the_order.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///history.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///pending_payments.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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


#@app.before_request
#def before_request():
#    g.user=None
#    if 'user' in session :
#        g.user=session['user']
#
# @app.route('/login',methods=['GET','POST'])
# def login():
#     if request.method == 'POST':
#         session.pop('user',None)
#         if request.form['password']=='password':
#             session['user']=request.form['username']
#             return redirect(url_for('gabru'))
#     return render_template('login.html')
#


@app.route('/')
def gabru():
    #if g.user:
        return render_template('welcome.html')
    #return redirect('login')

@app.route('/about')
def about():
    #if g.user:
        return render_template('About.html')
    #return redirect('login')

@app.route('/tac')
def tac():
    #if g.user:
        return render_template('Terms_conditions.html')
    #return redirect('login')


@app.route('/order', methods=['GET', 'POST'])
def ord():
    #if g.user:
        if request.method == 'POST':
            cust_name = request.form['cust_name']
            cust_address = request.form['cust_address']
            desc = request.form['desc']
            amount = request.form['amount']

            order = Orders(cust_name=cust_name, cust_address=cust_address,desc=desc,amount=amount)
            db.session.add(order)
            db.session.commit()

        return render_template('placing_order.html')
    #return redirect('login')

@app.route('/orders', methods=['GET', 'POST'])
def ords():
    #if g.user:
        return render_template('orders.html')
    #return redirect('login')

@app.route('/placed_orders', methods=['GET', 'POST'])
def placed_ord():
    #if g.user:
        order = Orders.query.all()
        return render_template('pending_orders.html', order=order)
    #return redirect('login')

@app.route('/orders_his', methods=['GET', 'POST'])
def orders_his():
    #if g.user:
        order = History.query.all()
        return render_template('history.html', order=order)
    #return redirect('login')


@app.route('/pay/<int:id>')
def pending_payments(id):
    #if g.user:
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
    #return redirect('login')


@app.route('/his/<int:id>')
def history(id):
    #if g.user:
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
    #return redirect('login')


@app.route('/his1/<int:id>')
def history1(id):
    #if g.user:
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
    #return redirect('login')

@app.route('/pending_pay_view')
def pending_pay_view():
    #if g.user:
        order=Pending_payments.query.all()
        return render_template('pending_payments.html',order=order)
    #return redirect('login')

@app.route('/update1/<int:id>', methods=['GET', 'POST'])
def update1(id):
    #if g.user:
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
    #return redirect('login')

@app.route('/delete1/<int:id>')
def delete1(id):
    #if g.user:
        order = Orders.query.filter_by(id=id).first()
        db.session.delete(order)
        db.session.commit()
        return redirect("/placed_orders")
    #return redirect('login')


@app.route('/stock', methods=['GET', 'POST'])
def stk():
    #if g.user:
        if request.method == 'POST':
            name = request.form['name']
            qty = request.form['qty']
            stock = Stock(name=name, qty=qty)
            db.session.add(stock)
            db.session.commit()

        return render_template('stock.html')
    #return redirect('login')


@app.route('/stock_view', methods=['GET', 'POST'])
def stk_view():
    #if g.user:
        stock = Stock.query.all()
        return render_template('stock_view.html', stock=stock)
    #return redirect('login')

@app.route('/welcome_stocks', methods=['GET', 'POST'])
def welcome_stock():
    #if g.user:
        return render_template('welcome_stock.html')
    #return redirect('login')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    #if g.user:
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
    #return redirect('login')

@app.route('/delete/<int:id>')
def delete(id):
    #if g.user:
        stock = Stock.query.filter_by(id=id).first()
        db.session.delete(stock)
        db.session.commit()
        return redirect("/stock_view")
    #return redirect('login')

if __name__ == "__main__":
    app.run()
