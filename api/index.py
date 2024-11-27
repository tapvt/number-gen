from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
from api.database import db_session, init_db
from api.models import Customer, Order, User, generate_prefixed_number
import os
import sys
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(sys.stdout),
                        logging.StreamHandler(sys.stderr)
                    ])
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='../src/templates')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret_key')

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    try:
        return db_session.query(User).get(int(user_id))
    except Exception as e:
        logger.error(f"Error loading user: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
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
        except Exception as e:
            logger.error(f"Registration error: {e}")
            logger.error(traceback.format_exc())
            db_session.rollback()
            flash('An error occurred during registration')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')

            user = db_session.query(User).filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('index'))

            flash('Invalid username or password')
        except Exception as e:
            logger.error(f"Login error: {e}")
            logger.error(traceback.format_exc())
            flash('An error occurred during login')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/generate_customer', methods=['POST'])
@login_required
def generate_customer():
    try:
        year_prefix = datetime.now().strftime('%y')
        customer_number = generate_prefixed_number(year_prefix, Customer, db_session)

        new_customer = Customer(customer_number=customer_number)
        db_session.add(new_customer)
        db_session.commit()

        return jsonify({
            'customer_number': customer_number,
            'success': True
        })
    except Exception as e:
        logger.error(f"Customer generation error: {e}")
        logger.error(traceback.format_exc())
        db_session.rollback()
        return jsonify({
            'error': 'Failed to generate customer number',
            'success': False
        }), 500

@app.route('/generate_order', methods=['POST'])
@login_required
def generate_order():
    try:
        year_prefix = datetime.now().strftime('%y')
        order_number = generate_prefixed_number(year_prefix, Order, db_session)

        new_order = Order(order_number=order_number)
        db_session.add(new_order)
        db_session.commit()

        return jsonify({
            'order_number': order_number,
            'success': True
        })
    except Exception as e:
        logger.error(f"Order generation error: {e}")
        logger.error(traceback.format_exc())
        db_session.rollback()
        return jsonify({
            'error': 'Failed to generate order number',
            'success': False
        }), 500

def handler(event, context):
    try:
        # Ensure database is initialized
        init_db()

        # Log environment variables for debugging (be cautious with sensitive info)
        logger.info(f"Environment Variables: {list(os.environ.keys())}")

        return app
    except Exception as e:
        logger.error(f"Handler initialization error: {e}")
        logger.error(traceback.format_exc())
        raise

# For local development
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
