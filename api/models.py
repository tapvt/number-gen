from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from api.database import Base


class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    customer_number = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_number = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)


def generate_prefixed_number(prefix, model):
    """
    Generate a number with year prefix and auto-increment.

    :param prefix: Prefix (typically last two digits of year)
    :param model: SQLAlchemy model to check against
    :return: Unique number as string
    """
    from api.database import db_session

    # Get the last record's number for this prefix
    last_record = db_session.query(model).filter(
        model.order_number.startswith(prefix) if model.__name__ == 'Order'
        else model.customer_number.startswith(prefix)
    ).order_by(
        model.id.desc()
    ).first()

    if last_record:
        # Extract the numeric part and increment
        last_number = (last_record.order_number if model.__name__ == 'Order'
                       else last_record.customer_number)
        numeric_part = int(last_number[2:])
        new_number = f"{prefix}{numeric_part + 1:04d}"
    else:
        # First number for this prefix
        new_number = f"{prefix}0001"

    return new_number
