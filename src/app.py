from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from datetime import datetime
from database import db_session, init_db
from models import Customer, Order, User, generate_prefixed_number


# Load environment variables
load_dotenv()


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a proper secret key


# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if user already exists
        existing_user = db_session.query(User).filter_by(username=username).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(username=username)
        new_user.set_password(password)

        db_session.add(new_user)
        db_session.commit()

        flash('Registration successful')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = db_session.query(User).filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))

        flash('Invalid username or password')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/generate_customer', methods=['POST'])
@login_required
def generate_customer():
    year_prefix = datetime.now().strftime('%y')
    customer_number = generate_prefixed_number(year_prefix, Customer)

    new_customer = Customer(customer_number=customer_number)
    db_session.add(new_customer)
    db_session.commit()

    return jsonify({
        'customer_number': customer_number
    })


@app.route('/generate_order', methods=['POST'])
@login_required
def generate_order():
    year_prefix = datetime.now().strftime('%y')
    order_number = generate_prefixed_number(year_prefix, Order)

    new_order = Order(order_number=order_number)
    db_session.add(new_order)
    db_session.commit()

    return jsonify({
        'order_number': order_number
    })


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# Initialize database on startup
init_db()


# For local development
if __name__ == '__main__':
    app.run(debug=True)
