import os
from faker import Faker
from model import db, User, Driver, Passenger, Seller, Bus, Route, Schedule, Booking, Product, Order, OrderItem, Comment, Review, RetailShop, Payment
from flask import Flask
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
fake = Faker()



def create_fake_user(role):
    username = fake.user_name()
    email = fake.email()
    password = generate_password_hash('password')
    user = User(username=username, email=email, password_hash=password, role=role)
    db.session.add(user)
    db.session.commit()
    return user

def create_fake_driver():
    name = fake.name()
    contact_info = fake.phone_number()
    driver = Driver(name=name, contact_info=contact_info)
    db.session.add(driver)
    db.session.commit()
    return driver

def create_fake_passenger(user_id):
    contact_info = fake.phone_number()
    passenger = Passenger(user_id=user_id, contact_info=contact_info)
    db.session.add(passenger)
    db.session.commit()
    return passenger

def create_fake_seller(user_id):
    shop_name = fake.company()
    location = fake.random_int(min=1, max=100)
    contact_info = fake.phone_number()
    seller = Seller(user_id=user_id, shop_name=shop_name, location=location, contact_info=contact_info)
    db.session.add(seller)
    db.session.commit()
    return seller

def create_fake_bus(driver_id):
    bus_number = fake.license_plate()
    seat_capacity = fake.random_int(min=20, max=50)
    current_location = fake.random_int(min=1, max=100)
    bus = Bus(driver_id=driver_id, bus_number=bus_number, seat_capacity=seat_capacity, current_location=current_location)
    db.session.add(bus)
    db.session.commit()
    return bus

def create_fake_route():
    origin = fake.city()
    destination = fake.city()
    description = fake.sentence()
    route = Route(origin=origin, destination=destination, description=description)
    db.session.add(route)
    db.session.commit()
    return route

def create_fake_schedule(bus_id, route_id):
    departure_time = fake.time()
    arrival_time = fake.time()
    date = fake.date()
    available_seats = fake.random_int(min=1, max=50)
    schedule = Schedule(bus_id=bus_id, route_id=route_id, departure_time=departure_time, arrival_time=arrival_time, date=date, available_seats=available_seats)
    db.session.add(schedule)
    db.session.commit()
    return schedule

def create_fake_product(seller_id):
    name = fake.bs()
    description = fake.text()
    price = fake.random_float(min=1.0, max=100.0)
    available_quantity = fake.random_int(min=1, max=100)
    location = fake.random_int(min=1, max=100)
    shop_name = fake.company()
    product = Product(name=name, description=description, price=price, available_quantity=available_quantity, seller_id=seller_id, location=location, shop_name=shop_name)
    db.session.add(product)
    db.session.commit()
    return product

def create_fake_booking(user_id, schedule_id):
    seat_number = fake.random_int(min=1, max=50)
    payment_status = fake.boolean()
    ticket_number = fake.uuid4()
    booking = Booking(user_id=user_id, schedule_id=schedule_id, seat_number=seat_number, payment_status=payment_status, ticket_number=ticket_number)
    db.session.add(booking)
    db.session.commit()
    return booking

def create_fake_order(user_id):
    total_price = fake.random_float(min=10.0, max=1000.0)
    status = 'pending'
    order = Order(buyer_id=user_id, total_price=total_price, status=status)
    db.session.add(order)
    db.session.commit()
    return order

def create_fake_order_item(order_id, product_id):
    quantity = fake.random_int(min=1, max=10)
    unit_price = fake.random_float(min=1.0, max=100.0)
    order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=quantity, unit_price=unit_price)
    db.session.add(order_item)
    db.session.commit()
    return order_item

def create_fake_comment(user_id, entity_id, entity_type):
    rating = fake.random_int(min=1, max=5)
    comment = fake.text()
    comment = Comment(user_id=user_id, entity_id=entity_id, entity_type=entity_type, rating=rating, comment=comment)
    db.session.add(comment)
    db.session.commit()
    return comment

def create_fake_review(user_id, entity_id, entity_type):
    rating = fake.random_int(min=1, max=5)
    review = fake.text()
    review = Review(user_id=user_id, entity_id=entity_id, entity_type=entity_type, rating=rating, review=review)
    db.session.add(review)
    db.session.commit()
    return review

def create_fake_payment(booking_id=None, order_id=None):
    amount = fake.random_float(min=10.0, max=1000.0)
    status = 'completed'
    transaction_id = fake.uuid4()
    payment = Payment(booking_id=booking_id, order_id=order_id, amount=amount, status=status, transaction_id=transaction_id)
    db.session.add(payment)
    db.session.commit()
    return payment

with app.app_context():
    db.create_all()

    for _ in range(10):
        user = create_fake_user('buyer')
        create_fake_passenger(user.id)
    
    for _ in range(5):
        user = create_fake_user('seller')
        create_fake_seller(user.id)
    
    for _ in range(5):
        driver = create_fake_driver()

    for _ in range(5):
        driver = create_fake_driver()
        bus = create_fake_bus(driver.id)
        route = create_fake_route()
        schedule = create_fake_schedule(bus.id, route.id)
        for _ in range(10):
            user = create_fake_user('buyer')
            create_fake_booking(user.id, schedule.id)
        
        for _ in range(10):
            user = create_fake_user('seller')
            seller = create_fake_seller(user.id)
            product = create_fake_product(seller.id)
            order = create_fake_order(user.id)
            create_fake_order_item(order.id, product.id)
    
    for _ in range(10):
        user = create_fake_user('buyer')
        create_fake_comment(user.id, fake.random_int(min=1, max=5), 'bus')
        create_fake_review(user.id, fake.random_int(min=1, max=5), 'product')

    for _ in range(10):
        booking = create_fake_booking(fake.random_int(min=1, max=10), fake.random_int(min=1, max=10))
        order = create_fake_order(fake.random_int(min=1, max=10))
        create_fake_payment(booking.id, order.id)
        
        
        
        