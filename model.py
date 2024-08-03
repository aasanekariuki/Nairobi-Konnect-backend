from sqlalchemy import Integer, MetaData,Time, Date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from flask_bcrypt import check_password_hash

# initialize metadata
metadata = MetaData()

db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False) 
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    bookings = db.relationship('Booking', back_populates='user')
    products = db.relationship('Product', back_populates='seller')
    orders = db.relationship('Order', back_populates='buyer')
    comments = db.relationship('Comment', back_populates='user')
    reviews = db.relationship('Review', back_populates='user')

class BusOperator(db.Model, SerializerMixin):
    __tablename__ = 'bus_operators'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    contact_info = db.Column(db.Text)
    buses = db.relationship('Bus', back_populates='operator')

class Bus(db.Model, SerializerMixin):
    __tablename__ = 'buses'
    id = db.Column(db.Integer, primary_key=True)
    operator_id = db.Column(db.Integer, db.ForeignKey('bus_operators.id'))
    bus_number = db.Column(db.String, nullable=False, unique=True)
    seat_capacity = db.Column(db.Integer, nullable=False)
    current_location = db.Column(Integer)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    operator = db.relationship('BusOperator', back_populates='buses')
    schedules = db.relationship('Schedule', back_populates='bus')

class Route(db.Model, SerializerMixin):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String, nullable=False)
    destination = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    schedules = db.relationship('Schedule', back_populates='route')

class Schedule(db.Model, SerializerMixin):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'))
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'))
    departure_time = db.Column(Time, nullable=False)
    arrival_time = db.Column(Time, nullable=False)
    date = db.Column(Date, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    bus = db.relationship('Bus', back_populates='schedules')
    route = db.relationship('Route', back_populates='schedules')
    bookings = db.relationship('Booking', back_populates='schedule')

class Booking(db.Model, SerializerMixin):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'))
    seat_number = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.Boolean, default=False)
    ticket_number = db.Column(db.String, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', back_populates='bookings')
    schedule = db.relationship('Schedule', back_populates='bookings')

class Product(db.Model, SerializerMixin):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    available_quantity = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    location = db.Column(Integer)
    shop_name = db.Column(db.String, nullable=False)
    seller = db.relationship('User', back_populates='products')
    order_items = db.relationship('OrderItem', back_populates='product')

class Order(db.Model, SerializerMixin):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    status = db.Column(db.String, default='pending')
    buyer = db.relationship('User', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order')

class OrderItem(db.Model, SerializerMixin):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')

class Comment(db.Model, SerializerMixin):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    entity_id = db.Column(db.Integer)  # ID of the entity being commented on
    entity_type = db.Column(db.String, nullable=False)  # 'accommodation', 'retail_shop', 'bus', 'product'
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', back_populates='comments')

class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bus_id = db.Column(db.Integer, nullable=True)
    shop_id = db.Column(db.Integer, nullable=True)
    product_id = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', back_populates='reviews')

class RetailShop(db.Model, SerializerMixin):
    __tablename__ = 'retail_shops'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(Integer)
    contact_info = db.Column(db.Text)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    reviews = db.relationship('Review', back_populates='shop')

class Payment(db.Model, SerializerMixin):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False)
    transaction_id = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    booking = db.relationship('Booking', back_populates='payments')
    order = db.relationship('Order', back_populates='payments')
