from sqlalchemy import MetaData, Time, Date, ForeignKey, Integer, String, Text, Float, Boolean, DateTime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize metadata
metadata = MetaData()
db = SQLAlchemy(metadata=metadata)

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String, nullable=False, unique=True)
    email = db.Column(String, nullable=False, unique=True)
    password_hash = db.Column(String, nullable=False)
    role = db.Column(String, nullable=False)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    is_verified = db.Column(Boolean, default=False)
    is_active = db.Column(Boolean, default=True)
    verification_token = db.Column(String, nullable=True)
    profile_picture = db.Column(String, nullable=True)

    # Relationships
    bookings = db.relationship('Booking', back_populates='user')
    orders = db.relationship('Order', back_populates='buyer')
    comments = db.relationship('Comment', back_populates='user')
    reviews = db.relationship('Review', back_populates='user')
    seller = db.relationship('Seller', back_populates='user', uselist=False)
    passenger = db.relationship('Passenger', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'profile_picture': self.profile_picture
        }

class Driver(db.Model, SerializerMixin):
    __tablename__ = 'drivers'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String, nullable=False)
    email = db.Column(String, nullable=False, unique=True)
    contact_info = db.Column(Text, nullable=False, unique=True)

    # Relationships
    buses = db.relationship('Bus', back_populates='driver')
    routes = db.relationship('Route', back_populates='driver')

class Bus(db.Model, SerializerMixin):
    __tablename__ = 'buses'
    id = db.Column(Integer, primary_key=True)
    driver_id = db.Column(Integer, ForeignKey('drivers.id'))
    bus_number = db.Column(String, nullable=False, unique=True)
    seat_capacity = db.Column(Integer, nullable=False)
    current_location = db.Column(String)  # Updated to String for consistency
    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    driver = db.relationship('Driver', back_populates='buses')
    schedules = db.relationship('Schedule', back_populates='bus')

class Route(db.Model, SerializerMixin):
    __tablename__ = 'routes'
    id = db.Column(Integer, primary_key=True)
    driver_id = db.Column(Integer, ForeignKey('drivers.id'))  # Added driver_id ForeignKey
    origin = db.Column(String, nullable=False)
    destination = db.Column(String, nullable=False)
    description = db.Column(Text)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    driver = db.relationship('Driver', back_populates='routes')
    schedules = db.relationship('Schedule', back_populates='route')
    tickets = db.relationship('Ticket', back_populates='route')

class Schedule(db.Model, SerializerMixin):
    __tablename__ = 'schedules'
    id = db.Column(Integer, primary_key=True)
    bus_id = db.Column(Integer, ForeignKey('buses.id'))
    route_id = db.Column(Integer, ForeignKey('routes.id'))
    departure_time = db.Column(Time, nullable=False)
    arrival_time = db.Column(Time, nullable=False)
    date = db.Column(Date, nullable=False)
    available_seats = db.Column(Integer, nullable=False)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    bus = db.relationship('Bus', back_populates='schedules')
    route = db.relationship('Route', back_populates='schedules')
    bookings = db.relationship('Booking', back_populates='schedule')

class Booking(db.Model, SerializerMixin):
    __tablename__ = 'bookings'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'))
    schedule_id = db.Column(Integer, ForeignKey('schedules.id'))
    passenger_id = db.Column(Integer, ForeignKey('passengers.id'))
    seat_number = db.Column(Integer, nullable=False)
    payment_status = db.Column(Boolean, default=False)
    ticket_number = db.Column(String, nullable=False, unique=True)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='bookings')
    schedule = db.relationship('Schedule', back_populates='bookings')
    payments = db.relationship('Payment', back_populates='booking')
    passenger = db.relationship('Passenger', back_populates='bookings')

class Ticket(db.Model, SerializerMixin):
    __tablename__ = 'tickets'
    id = db.Column(Integer, primary_key=True)
    route_id = db.Column(Integer, ForeignKey('routes.id'))
    passenger_id = db.Column(Integer)
    seat_number = db.Column(String(10))
    
    # Relationships
    route = db.relationship('Route', back_populates='tickets')

class Product(db.Model, SerializerMixin):
    __tablename__ = 'products'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String, nullable=False)
    description = db.Column(Text)
    price = db.Column(Float, nullable=False)
    available_quantity = db.Column(Integer, nullable=False)
    sold_quantity = db.Column(Integer, default=0)
    image_url = db.Column(String, nullable=True)
    stall_id = db.Column(Integer, ForeignKey('stalls.id'), nullable=False)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    location = db.Column(String)  # Updated to String
    stall_name = db.Column(String, nullable=False)

    stall = db.relationship('Stall', back_populates='products')
    order_items = db.relationship('OrderItem', back_populates='product')

class Order(db.Model, SerializerMixin):
    __tablename__ = 'orders'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'))
    total_price = db.Column(Float, nullable=False)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    status = db.Column(String, default='pending')

    buyer = db.relationship('User', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order')
    payments = db.relationship('Payment', back_populates='order')

class OrderItem(db.Model, SerializerMixin):
    __tablename__ = 'order_items'
    id = db.Column(Integer, primary_key=True)
    order_id = db.Column(Integer, ForeignKey('orders.id'))
    product_id = db.Column(Integer, ForeignKey('products.id'))
    quantity = db.Column(Integer, nullable=False)
    unit_price = db.Column(Float, nullable=False)

    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')

class Comment(db.Model, SerializerMixin):
    __tablename__ = 'comments'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'))
    entity_id = db.Column(Integer)  
    entity_type = db.Column(String, nullable=False)  
    rating = db.Column(Integer, nullable=False)
    comment = db.Column(Text)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='comments')

class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'))
    bus_id = db.Column(Integer, nullable=True)
    shop_id = db.Column(Integer, ForeignKey('stalls.id'), nullable=True)  # Corrected to be nullable
    product_id = db.Column(Integer, nullable=True)
    rating = db.Column(Integer, nullable=False)
    review = db.Column(Text)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='reviews')
    stall = db.relationship('Stall', back_populates='reviews')

class Payment(db.Model, SerializerMixin):
    __tablename__ = 'payments'
    id = db.Column(Integer, primary_key=True)
    booking_id = db.Column(Integer, ForeignKey('bookings.id'))
    order_id = db.Column(Integer, ForeignKey('orders.id'))
    amount = db.Column(Float, nullable=False)
    status = db.Column(String(50), nullable=False)
    transaction_id = db.Column(String, unique=True)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    booking = db.relationship('Booking', back_populates='payments')
    order = db.relationship('Order', back_populates='payments')

class Seller(db.Model, SerializerMixin):
    __tablename__ = 'sellers'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'))
    stall_name = db.Column(String, nullable=False)
    location = db.Column(String, nullable=False)
    contact_info = db.Column(Text, nullable=False)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='seller')
    stalls = db.relationship('Stall', back_populates='seller')

class Stall(db.Model, SerializerMixin):
    __tablename__ = 'stalls'
    id = db.Column(Integer, primary_key=True)
    seller_id = db.Column(Integer, ForeignKey('sellers.id'))
    stall_name = db.Column(String, nullable=False)
    description = db.Column(Text)
    location = db.Column(String, nullable=False)
    image_url = db.Column(String, nullable=True)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())

    seller = db.relationship('Seller', back_populates='stalls')
    products = db.relationship('Product', back_populates='stall')
    reviews = db.relationship('Review', back_populates='stall')

class Passenger(db.Model, SerializerMixin):
    __tablename__ = 'passengers'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, ForeignKey('users.id'))
    contact_info = db.Column(Text, nullable=False)
    created_at = db.Column(DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='passenger')
    bookings = db.relationship('Booking', back_populates='passenger')
