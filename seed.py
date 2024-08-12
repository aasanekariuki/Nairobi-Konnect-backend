from datetime import datetime
from faker import Faker
from flask_bcrypt import check_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, app 
from model import (
    User, Driver, Bus, Route, Schedule, Booking, Product, Order, OrderItem,
    Comment, Review, RetailShop, Payment, Seller, Passenger, Stall
)

fake = Faker()
# app = app()

def create_fake_user():
    return User(
        username=fake.user_name(),
        email=fake.email(),
        password_hash=generate_password_hash(fake.password()),
        role='user',
        is_verified=fake.boolean(),
        is_active=fake.boolean(),
        created_at=datetime.utcnow()
    )

def create_fake_driver():
    return Driver(
        name=fake.name(),
        contact_info=fake.phone_number()
    )

def create_fake_bus(driver_id):
    return Bus(
        driver_id=driver_id,
        bus_number=fake.license_plate(),
        seat_capacity=fake.random_int(min=10, max=50),
        current_location=fake.random_int(min=1, max=100)
    )

def create_fake_route():
    return Route(
        origin=fake.city(),
        destination=fake.city(),
        description=fake.text()
    )

def create_fake_schedule(bus_id, route_id):
    departure_time = fake.time_object()
    arrival_time = fake.time_object()
    date = fake.date_object()
    available_seats = fake.random_int(min=1, max=50)
    
    return Schedule(
        bus_id=bus_id,
        route_id=route_id,
        departure_time=departure_time,
        arrival_time=arrival_time,
        date=date,
        available_seats=available_seats
    )

def create_fake_booking(user_id, schedule_id, passenger_id):
    return Booking(
        user_id=user_id,
        schedule_id=schedule_id,
        passenger_id=passenger_id,
        seat_number=fake.random_int(min=1, max=50),
        payment_status=fake.boolean(),
        ticket_number=fake.uuid4()
    )

def create_fake_product(stall_id):
    return Product(
        name=fake.word(),
        description=fake.text(),
        price=fake.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=1.0, max_value=100.0),
        available_quantity=fake.random_int(min=1, max=100),
        image_url=fake.image_url(),
        stall_id=stall_id,
        location=fake.random_int(min=1, max=100),
        shop_name=fake.company()
    )

def create_fake_order(buyer_id):
    return Order(
        buyer_id=buyer_id,
        total_price=fake.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=10.0, max_value=500.0),
        status=fake.random_element(elements=('pending', 'completed', 'cancelled'))
    )

def create_fake_order_item(order_id, product_id):
    return OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=fake.random_int(min=1, max=5),
        unit_price=fake.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=1.0, max_value=100.0)
    )

def create_fake_comment(user_id):
    return Comment(
        user_id=user_id,
        entity_id=fake.random_int(min=1, max=100),
        entity_type=fake.word(),  
        rating=fake.random_int(min=1, max=5),
        comment=fake.text()
    )

def create_fake_review(user_id):
    return Review(
        user_id=user_id,
        bus_id=fake.random_int(min=1, max=100),
        shop_id=fake.random_int(min=1, max=100),
        product_id=fake.random_int(min=1, max=100),
        rating=fake.random_int(min=1, max=5),
        review=fake.text()
    )

def create_fake_retail_shop():
    return RetailShop(
        name=fake.company(),
        location=fake.random_int(min=1, max=100),
        contact_info=fake.phone_number(),
        description=fake.text()
    )

def create_fake_payment(booking_id, order_id):
    return Payment(
        booking_id=booking_id,
        order_id=order_id,
        amount=fake.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=1.0, max_value=500.0),
        status=fake.word(),
        transaction_id=fake.uuid4()
    )

def create_fake_seller(user_id):
    return Seller(
        user_id=user_id,
        shop_name=fake.company(),
        location=fake.random_int(min=1, max=100),
        contact_info=fake.phone_number()
    )

def create_fake_passenger(user_id):
    return Passenger(
        user_id=user_id,
        contact_info=fake.phone_number()
    )

def create_fake_stall(seller_id):
    return Stall(
        seller_id=seller_id,
        stall_name=fake.word(),
        description=fake.text(),
        location=fake.random_int(min=1, max=100)
    )

def seed_db():
    users = [create_fake_user() for _ in range(10)]
    db.session.add_all(users)
    db.session.commit()

    drivers = [create_fake_driver() for _ in range(5)]
    db.session.add_all(drivers)
    db.session.commit()

    buses = [create_fake_bus(driver_id=fake.random_int(min=1, max=5)) for _ in range(20)]
    db.session.add_all(buses)
    db.session.commit()

    routes = [create_fake_route() for _ in range(10)]
    db.session.add_all(routes)
    db.session.commit()

    schedules = [create_fake_schedule(bus_id=fake.random_int(min=1, max=20), route_id=fake.random_int(min=1, max=10)) for _ in range(30)]
    db.session.add_all(schedules)
    db.session.commit()

    bookings = [create_fake_booking(user_id=fake.random_int(min=1, max=10), schedule_id=fake.random_int(min=1, max=30), passenger_id=fake.random_int(min=1, max=10)) for _ in range(50)]
    db.session.add_all(bookings)
    db.session.commit()

    sellers = [create_fake_seller(user_id=fake.random_int(min=1, max=10)) for _ in range(5)]
    db.session.add_all(sellers)
    db.session.commit()
    
    stalls = [create_fake_stall(seller_id=fake.random_int(min=1, max=5)) for _ in range(10)]
    db.session.add_all(stalls)
    db.session.commit()

    products = [create_fake_product(stall_id=fake.random_int(min=1, max=10)) for _ in range(25)]
    db.session.add_all(products)
    db.session.commit()

    orders = [create_fake_order(buyer_id=fake.random_int(min=1, max=10)) for _ in range(20)]
    db.session.add_all(orders)
    db.session.commit()

    order_items = [create_fake_order_item(order_id=fake.random_int(min=1, max=20), product_id=fake.random_int(min=1, max=25)) for _ in range(100)]
    db.session.add_all(order_items)
    db.session.commit()

    comments = [create_fake_comment(user_id=fake.random_int(min=1, max=10)) for _ in range(30)]
    db.session.add_all(comments)
    db.session.commit()

    reviews = [create_fake_review(user_id=fake.random_int(min=1, max=10)) for _ in range(20)]
    db.session.add_all(reviews)
    db.session.commit()

    retail_shops = [create_fake_retail_shop() for _ in range(10)]
    db.session.add_all(retail_shops)
    db.session.commit()

    payments = [create_fake_payment(booking_id=fake.random_int(min=1, max=50), order_id=fake.random_int(min=1, max=20)) for _ in range(30)]
    db.session.add_all(payments)
    db.session.commit()

    passengers = [create_fake_passenger(user_id=fake.random_int(min=1, max=10)) for _ in range(10)]
    db.session.add_all(passengers)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        seed_db()