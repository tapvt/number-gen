from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

Base = declarative_base()

def generate_prefixed_number(prefix, model_class, db_session):
    """
    Generate a unique prefixed number for a given model class.

    Args:
        prefix (str): Prefix (typically last two digits of year)
        model_class (type): SQLAlchemy model class to check for uniqueness
        db_session (sqlalchemy.orm.Session): Database session to query

    Returns:
        str: A unique prefixed number
    """
    # Determine the prefix based on the model
    number_prefix = 'C-' if model_class.__name__ == 'Customer' else 'O-'

    # Get the last record's number for this prefix
    last_record = db_session.query(model_class).filter(
        model_class.order_number.startswith(number_prefix + prefix) if model_class.__name__ == 'Order'
        else model_class.customer_number.startswith(number_prefix + prefix)
    ).order_by(
        model_class.id.desc()
    ).first()

    if last_record:
        # Extract the numeric part and increment
        last_number = (last_record.order_number if model_class.__name__ == 'Order'
                       else last_record.customer_number)
        numeric_part = int(last_number.split('-')[1][4:])
        new_number = f"{number_prefix}{prefix}{numeric_part + 1:05d}"
    else:
        # First number for this prefix
        new_number = f"{number_prefix}{prefix}00001"

    return new_number

class User(Base, UserMixin):
    """
    User model for authentication and user management.
    Inherits from UserMixin to provide default implementations
    for Flask-Login required methods.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    def set_password(self, password):
        """
        Hash and set the user's password.

        Args:
            password (str): Plain text password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check if the provided password is correct.

        Args:
            password (str): Plain text password to check

        Returns:
            bool: True if password is correct, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        """
        Explicitly define is_active method for Flask-Login.

        Returns:
            bool: Always returns True unless specific deactivation logic is added
        """
        return True

class Customer(Base):
    """
    Customer model to track generated customer numbers.
    """
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    customer_number = Column(String(10), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Order(Base):
    """
    Order model to track generated order numbers.
    """
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    order_number = Column(String(10), unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
