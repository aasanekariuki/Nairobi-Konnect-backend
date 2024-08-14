from datetime import datetime, time, date
import random
import string
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from app import db, app
from faker import Faker
from model import (
    User, Driver, Bus, Route, Schedule, Booking, Product, Order, OrderItem,
    Comment, Review, Payment, Seller, Passenger, Stall
)
from resources import user

faker = Faker()

# Helper function to generate a random ticket number
def generate_ticket_number(length=8):
    letters_and_digits = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

# Seed Users
def seed_users():
    users = [
        User(
            username='john_doe',
            email='john.doe@example.com',
            password_hash=generate_password_hash('password123'),
            role='admin',
            profile_picture='profile_john_doe.jpg',
            is_verified=True,
            is_active=True
        ),
        User(
            username='jane_smith',
            email='jane.smith@example.com',
            password_hash=generate_password_hash('securepassword'),
            role='seller',
            profile_picture='profile_jane_smith.jpg',
            is_verified=True,
            is_active=True
        ),
        User(
            username='michael_brown',
            email='michael.brown@example.com',
            password_hash=generate_password_hash('mypass456'),
            role='customer',
            profile_picture='profile_michael_brown.jpg',
            is_verified=False,
            is_active=True
        ),
        User(
            username='emily_white',
            email='emily.white@example.com',
            password_hash=generate_password_hash('emilypass789'),
            role='customer',
            profile_picture='profile_emily_white.jpg',
            is_verified=True,
            is_active=True
        ),
        User(
            username='alice_green',
            email='alice.green@example.com',
            password_hash=generate_password_hash('alicepass101'),
            role='seller',
            profile_picture='profile_alice_green.jpg',
            is_verified=True,
            is_active=False
        )
    ]

    with app.app_context():
        for user in users:
            if not User.query.filter_by(email=user.email).first():
                db.session.add(user)
        
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()  # Rollback the session if there was an IntegrityError

# Call the function to seed the data
seed_users()

# Seed Drivers
def seed_drivers():
    drivers = [
        Driver(name="John Doe", email="john.doe@example.com", contact_info="+254700000001"),
        Driver(name="Jane Smith", email="jane.smith@example.com", contact_info="+254700000002"),
        Driver(name="Alex Johnson", email="alex.johnson@example.com", contact_info="+254700000003"),
    ]
    db.session.add_all(drivers)
    db.session.commit()
# Seed Buses
def seed_buses():
    # Clear existing buses
    db.session.query(Bus).delete()
    db.session.commit()

    bus_numbers = set()
    for _ in range(10):  # Adjust the range as needed
        while True:
            # Generate a bus number in the format "NBI-XXX" where XXX is a random 3-digit number
            bus_number = f"NBI-{faker.random_int(min=1, max=999):03}"
            if bus_number not in bus_numbers:
                bus_numbers.add(bus_number)
                break

        new_bus = Bus(
            driver_id=faker.random_int(min=1, max=10),
            bus_number=bus_number,
            seat_capacity=faker.random_int(min=30, max=50),
            current_location=faker.city()
        )
        db.session.add(new_bus)
    
    db.session.commit()

# Seed Routes
def seed_routes():
    routes_data = [
        {"origin": "CBD", "destination": "Westlands", "description": "Route from Nairobi Central Business District to Westlands"},
        {"origin": "CBD", "destination": "Kilimani", "description": "Route from Nairobi Central Business District to Kilimani"},
        {"origin": "CBD", "destination": "Kibera", "description": "Route from Nairobi Central Business District to Kibera"},
        {"origin": "CBD", "destination": "Lang'ata", "description": "Route from Nairobi Central Business District to Lang'ata"},
        {"origin": "CBD", "destination": "Karen", "description": "Route from Nairobi Central Business District to Karen"},
        {"origin": "CBD", "destination": "Ngong", "description": "Route from Nairobi Central Business District to Ngong"},
        {"origin": "CBD", "destination": "Rongai", "description": "Route from Nairobi Central Business District to Rongai"},
        {"origin": "CBD", "destination": "Embakasi", "description": "Route from Nairobi Central Business District to Embakasi"},
        {"origin": "CBD", "destination": "Thika", "description": "Route from Nairobi Central Business District to Thika"},
        {"origin": "CBD", "destination": "Gikambura", "description": "Route from Nairobi Central Business District to Gikambura in Kikuyu"},
    ]
    routes = [Route(**route_data, created_at=datetime.now(), updated_at=datetime.now()) for route_data in routes_data]
    db.session.add_all(routes)
    db.session.commit()

# Seed Schedules
def seed_schedules():
    buses = Bus.query.all()
    routes = Route.query.all()
    schedules_data = [
        {"bus_id": buses[0].id, "route_id": routes[0].id, "departure_time": time(7, 30), "arrival_time": time(8, 15), "date": date(2024, 8, 15), "available_seats": 40},
        {"bus_id": buses[1].id, "route_id": routes[1].id, "departure_time": time(8, 00), "arrival_time": time(8, 45), "date": date(2024, 8, 15), "available_seats": 35},
        {"bus_id": buses[2].id, "route_id": routes[2].id, "departure_time": time(8, 30), "arrival_time": time(9, 15), "date": date(2024, 8, 15), "available_seats": 30},
        {"bus_id": buses[3].id, "route_id": routes[3].id, "departure_time": time(9, 00), "arrival_time": time(9, 45), "date": date(2024, 8, 15), "available_seats": 50},
        {"bus_id": buses[4].id, "route_id": routes[4].id, "departure_time": time(9, 00), "arrival_time": time(9, 50), "date": date(2024, 8, 15), "available_seats": 40},
        
    ]
    schedules = [Schedule(**schedule_data, created_at=datetime.now(), updated_at=datetime.now()) for schedule_data in schedules_data]
    db.session.add_all(schedules)
    db.session.commit()

# Seed Bookings
def seed_bookings():
    users = User.query.all()
    schedules = Schedule.query.all()
    bookings_data = [
        {"user_id": users[0].id, "schedule_id": schedules[0].id, "passenger_id": 1, "seat_number": 1, "payment_status": True, "ticket_number": generate_ticket_number()},
        {"user_id": users[1].id, "schedule_id": schedules[1].id, "passenger_id": 2, "seat_number": 2, "payment_status": False, "ticket_number": generate_ticket_number()},
        {"user_id": users[2].id, "schedule_id": schedules[2].id, "passenger_id": 3, "seat_number": 3, "payment_status": True, "ticket_number": generate_ticket_number()},
    ]
    bookings = [Booking(**booking_data, created_at=datetime.now()) for booking_data in bookings_data]
    db.session.add_all(bookings)
    db.session.commit()

# Seed Products
from datetime import datetime

def seed_products():
    products = [
        # Fashion Hub - Clothes
        {'name': 'Casual Shirt', 'description': 'Comfortable casual shirt', 'price': 29.99, 'available_quantity': 50, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://example.com/images/casual_shirt.jpg'},
        {'name': 'Formal Suit', 'description': 'Stylish formal suit', 'price': 199.99, 'available_quantity': 30, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://example.com/images/formal_suit.jpg'},
        {'name': 'Denim Jeans', 'description': 'Trendy denim jeans', 'price': 49.99, 'available_quantity': 60, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://example.com/images/denim_jeans.jpg'},
        {'name': 'Summer Dress', 'description': 'Light and airy summer dress', 'price': 39.99, 'available_quantity': 40, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://example.com/images/summer_dress.jpg'},
        {'name': 'Winter Jacket', 'description': 'Warm winter jacket', 'price': 149.99, 'available_quantity': 20, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://example.com/images/winter_jacket.jpg'},
        {'name': 'Leather Jacket', 'description': 'Stylish leather jacket', 'price': 179.99, 'available_quantity': 15, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://example.com/images/leather_jacket.jpg'},
        {'name': 'Turtleneck Sweater', 'description': 'Warm turtleneck sweater', 'price': 39.99, 'available_quantity': 25, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://example.com/images/turtleneck_sweater.jpg'},
        {'name': 'Polo Shirt', 'description': 'Classic polo shirt', 'price': 34.99, 'available_quantity': 45, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://example.com/images/polo_shirt.jpg'},
        {'name': 'Cardigan Sweater', 'description': 'Cozy cardigan sweater', 'price': 44.99, 'available_quantity': 20, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://example.com/images/cardigan_sweater.jpg'},
        {'name': 'Cargo Pants', 'description': 'Durable cargo pants', 'price': 39.99, 'available_quantity': 30, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://example.com/images/cargo_pants.jpg'},

        # Shoe Paradise - Shoes
        {'name': 'Running Shoes', 'description': 'Comfortable running shoes', 'price': 89.99, 'available_quantity': 40, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://example.com/images/running_shoes.jpg'},
        {'name': 'Leather Boots', 'description': 'Durable leather boots', 'price': 129.99, 'available_quantity': 20, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://example.com/images/leather_boots.jpg'},
        {'name': 'High Heels', 'description': 'Elegant high heels', 'price': 99.99, 'available_quantity': 35, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://example.com/images/high_heels.jpg'},
        {'name': 'Sneakers', 'description': 'Stylish everyday sneakers', 'price': 79.99, 'available_quantity': 50, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://example.com/images/sneakers.jpg'},
        {'name': 'Sandals', 'description': 'Comfortable summer sandals', 'price': 49.99, 'available_quantity': 60, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://example.com/images/sandals.jpg'},
        {'name': 'Loafers', 'description': 'Casual leather loafers', 'price': 89.99, 'available_quantity': 25, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://example.com/images/loafers.jpg'},
        {'name': 'Chelsea Boots', 'description': 'Sleek Chelsea boots', 'price': 139.99, 'available_quantity': 15, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://example.com/images/chelsea_boots.jpg'},
        {'name': 'Flip Flops', 'description': 'Casual flip flops', 'price': 19.99, 'available_quantity': 70, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://example.com/images/flip_flops.jpg'},
        {'name': 'Oxford Shoes', 'description': 'Classic Oxford shoes', 'price': 109.99, 'available_quantity': 20, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://example.com/images/oxford_shoes.jpg'},
        {'name': 'Hiking Boots', 'description': 'Durable hiking boots', 'price': 149.99, 'available_quantity': 15, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://example.com/images/hiking_boots.jpg'},

        # Perfume Palace - Perfumes
        {'name': 'Chanel No. 5', 'description': 'Classic Chanel fragrance', 'price': 99.99, 'available_quantity': 25, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://example.com/images/chanel_no5.jpg'},
        {'name': 'Dior Sauvage', 'description': 'Masculine Dior fragrance', 'price': 79.99, 'available_quantity': 35, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://example.com/images/dior_sauvage.jpg'},
        {'name': 'Gucci Bloom', 'description': 'Floral Gucci fragrance', 'price': 89.99, 'available_quantity': 30, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://example.com/images/gucci_bloom.jpg'},
        {'name': 'YSL Black Opium', 'description': 'Bold YSL fragrance', 'price': 109.99, 'available_quantity': 20, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://example.com/images/ysl_black_opium.jpg'},
        {'name': 'Versace Eros', 'description': 'Sensual Versace fragrance', 'price': 99.99, 'available_quantity': 25, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://example.com/images/versace_eros.jpg'},
        {'name': 'Tom Ford Oud Wood', 'description': 'Luxurious Tom Ford fragrance', 'price': 149.99, 'available_quantity': 15, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://example.com/images/tom_ford_oud_wood.jpg'},
        {'name': 'Creed Aventus', 'description': 'Iconic Creed fragrance', 'price': 199.99, 'available_quantity': 10, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://example.com/images/creed_aventus.jpg'},
        {'name': 'Marc Jacobs Daisy', 'description': 'Light Marc Jacobs fragrance', 'price': 89.99, 'available_quantity': 30, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://example.com/images/marc_jacobs_daisy.jpg'},
        {'name': 'Jo Malone Lime Basil & Mandarin', 'description': 'Citrus Jo Malone fragrance', 'price': 129.99, 'available_quantity': 15, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://example.com/images/jo_malone_lime_basil.jpg'},
        {'name': 'Calvin Klein CK One', 'description': 'Fresh Calvin Klein fragrance', 'price': 69.99, 'available_quantity': 40, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://example.com/images/ck_one.jpg'},
          # Electronics World - Electronics
        {'name': 'Smartphone', 'description': 'Latest model smartphone', 'price': 699.99, 'available_quantity': 25, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://example.com/images/smartphone.jpg'},
        {'name': 'Laptop', 'description': 'High-performance laptop', 'price': 1099.99, 'available_quantity': 15, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://example.com/images/laptop.jpg'},
        {'name': 'Smartwatch', 'description': 'Stylish smartwatch', 'price': 199.99, 'available_quantity': 30, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://example.com/images/smartwatch.jpg'},
        {'name': 'Bluetooth Headphones', 'description': 'Noise-cancelling headphones', 'price': 149.99, 'available_quantity': 40, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://example.com/images/bluetooth_headphones.jpg'},
        {'name': 'Gaming Console', 'description': 'Next-gen gaming console', 'price': 499.99, 'available_quantity': 10, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://example.com/images/gaming_console.jpg'},
        {'name': '4K TV', 'description': 'Ultra HD 4K television', 'price': 899.99, 'available_quantity': 20, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://example.com/images/4k_tv.jpg'},
        {'name': 'Wireless Earbuds', 'description': 'Compact wireless earbuds', 'price': 129.99, 'available_quantity': 50, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://example.com/images/wireless_earbuds.jpg'},
        {'name': 'Tablet', 'description': 'Portable high-resolution tablet', 'price': 499.99, 'available_quantity': 30, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://example.com/images/tablet.jpg'},
        {'name': 'Digital Camera', 'description': 'High-resolution digital camera', 'price': 749.99, 'available_quantity': 15, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://example.com/images/digital_camera.jpg'},
        {'name': 'Home Theater System', 'description': 'Immersive home theater experience', 'price': 599.99, 'available_quantity': 10, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://example.com/images/home_theater.jpg'},

        # Food Basket - Food
        {'name': 'Organic Apples', 'description': 'Fresh organic apples', 'price': 3.99, 'available_quantity': 100, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://example.com/images/organic_apples.jpg'},
        {'name': 'Granola Bars', 'description': 'Healthy granola bars', 'price': 5.99, 'available_quantity': 50, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://example.com/images/granola_bars.jpg'},
        {'name': 'Almond Milk', 'description': 'Vegan almond milk', 'price': 4.99, 'available_quantity': 40, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://example.com/images/almond_milk.jpg'},
        {'name': 'Quinoa', 'description': 'Healthy quinoa grains', 'price': 6.99, 'available_quantity': 60, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://example.com/images/quinoa.jpg'},
        {'name': 'Organic Honey', 'description': 'Pure organic honey', 'price': 7.99, 'available_quantity': 35, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://example.com/images/organic_honey.jpg'},
        {'name': 'Greek Yogurt', 'description': 'Creamy Greek yogurt', 'price': 3.49, 'available_quantity': 80, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://example.com/images/greek_yogurt.jpg'},
        {'name': 'Avocado', 'description': 'Fresh avocados', 'price': 1.99, 'available_quantity': 120, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://example.com/images/avocado.jpg'},
        {'name': 'Whole Grain Bread', 'description': 'Healthy whole grain bread', 'price': 2.99, 'available_quantity': 50, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://example.com/images/whole_grain_bread.jpg'},
        {'name': 'Dark Chocolate', 'description': 'Rich dark chocolate', 'price': 3.99, 'available_quantity': 70, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://example.com/images/dark_chocolate.jpg'},
        {'name': 'Kombucha', 'description': 'Refreshing kombucha drink', 'price': 3.49, 'available_quantity': 50, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://example.com/images/kombucha.jpg'},

        # Jewel Collection - Jewelry
        {'name': 'Gold Necklace', 'description': 'Elegant gold necklace', 'price': 499.99, 'available_quantity': 5, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://example.com/images/gold_necklace.jpg'},
        {'name': 'Silver Bracelet', 'description': 'Beautiful silver bracelet', 'price': 199.99, 'available_quantity': 10, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://example.com/images/silver_bracelet.jpg'},
        {'name': 'Diamond Ring', 'description': 'Stunning diamond ring', 'price': 999.99, 'available_quantity': 3, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://example.com/images/diamond_ring.jpg'},
        {'name': 'Pearl Earrings', 'description': 'Classic pearl earrings', 'price': 299.99, 'available_quantity': 8, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://example.com/images/pearl_earrings.jpg'},
        {'name': 'Ruby Pendant', 'description': 'Elegant ruby pendant', 'price': 799.99, 'available_quantity': 4, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://example.com/images/ruby_pendant.jpg'},
        {'name': 'Gold Watch', 'description': 'Luxury gold watch', 'price': 1199.99, 'available_quantity': 2, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://example.com/images/gold_watch.jpg'},
        {'name': 'Emerald Brooch', 'description': 'Vintage emerald brooch', 'price': 699.99, 'available_quantity': 3, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://example.com/images/emerald_brooch.jpg'},
        {'name': 'Sapphire Cufflinks', 'description': 'Sophisticated sapphire cufflinks', 'price': 249.99, 'available_quantity': 6, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://example.com/images/sapphire_cufflinks.jpg'},
        {'name': 'Platinum Band', 'description': 'Sleek platinum band', 'price': 599.99, 'available_quantity': 5, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://example.com/images/platinum_band.jpg'},
        {'name': 'Opal Ring', 'description': 'Unique opal ring', 'price': 399.99, 'available_quantity': 4, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://example.com/images/opal_ring.jpg'},
    ]

    db.session.add_all([Product(**product) for product in products])
    db.session.commit()


# Seed Orders
def seed_orders():
    users = User.query.all()
    orders_data = [
        {"user_id": users[0].id, "total_price": 299.97, "status": "completed", "payment_status": "paid"},
        {"user_id": users[1].id, "total_price": 129.99, "status": "pending", "payment_status": "unpaid"},
    ]
    orders = [Order(**order_data, created_at=datetime.now(), updated_at=datetime.now()) for order_data in orders_data]
    db.session.add_all(orders)
    db.session.commit()

# Seed Order Items
def seed_order_items():
    orders = Order.query.all()
    products = Product.query.all()
    order_items_data = [
        {"order_id": orders[0].id, "product_id": products[0].id, "quantity": 1, "price": 29.99},
        {"order_id": orders[0].id, "product_id": products[2].id, "quantity": 2, "price": 89.99},
        {"order_id": orders[1].id, "product_id": products[3].id, "quantity": 1, "price": 129.99},
    ]
    order_items = [OrderItem(**item_data) for item_data in order_items_data]
    db.session.add_all(order_items)
    db.session.commit()

# Seed Payments
def seed_payments():
    orders = Order.query.all()
    payments_data = [
        {"order_id": orders[0].id, "payment_method": "M-Pesa", "amount_paid": 299.97, "payment_date": datetime.now()},
        {"order_id": orders[1].id, "payment_method": "Credit Card", "amount_paid": 129.99, "payment_date": datetime.now()},
    ]
    payments = [Payment(**payment_data) for payment_data in payments_data]
    db.session.add_all(payments)
    db.session.commit()

# Seed Comments
def seed_comments():
    users = User.query.all()
    products = Product.query.all()
    comments_data = [
        {"user_id": users[0].id, "entity_id": products[0].id, "entity_type": "Product", "rating": 5, "comment": "Excellent product! Highly recommend."},
        {"user_id": users[1].id, "entity_id": products[1].id, "entity_type": "Product", "rating": 4, "comment": "Very good, but could use some improvements."},
        {"user_id": users[2].id, "entity_id": products[2].id, "entity_type": "Product", "rating": 3, "comment": "Average quality, not as expected."},
        {"user_id": users[0].id, "entity_id": products[3].id, "entity_type": "Product", "rating": 4, "comment": "Good value for the price."},
        {"user_id": users[1].id, "entity_id": products[4].id, "entity_type": "Product", "rating": 2, "comment": "Not worth the price."},
    ]
    comments = [Comment(**comment_data, created_at=datetime.now(), updated_at=datetime.now()) for comment_data in comments_data]
    db.session.add_all(comments)
    db.session.commit()

# Seed Reviews
def seed_reviews():
    users = User.query.all()
    products = Product.query.all()
    reviews_data = [
        {"user_id": users[0].id, "entity_id": products[0].id, "entity_type": "Product", "rating": 4, "comment": "Nice product, but delivery was slow."},
        {"user_id": users[1].id, "entity_id": products[1].id, "entity_type": "Product", "rating": 5, "comment": "Loved it! Highly recommend."},
        {"user_id": users[2].id, "entity_id": products[2].id, "entity_type": "Product", "rating": 3, "comment": "It's okay, nothing special."},
        {"user_id": users[0].id, "entity_id": products[3].id, "entity_type": "Product", "rating": 2, "comment": "Not satisfied with the quality."},
        {"user_id": users[1].id, "entity_id": products[4].id, "entity_type": "Product", "rating": 4, "comment": "Good product, but a bit expensive."},
    ]
    reviews = [Review(**review_data, created_at=datetime.now(), updated_at=datetime.now()) for review_data in reviews_data]
    db.session.add_all(reviews)
    db.session.commit()
    
from datetime import datetime

def seed_payment():
    booking_ids = [booking.id for booking in Booking.query.all()]
    order_ids = [order.id for order in Order.query.all()]
    
    payments = [
        Payment(booking_id=booking_ids[0], order_id=None, amount=150.75, status='completed', transaction_id='TXN123456'),
        Payment(booking_id=booking_ids[1], order_id=None, amount=200.00, status='pending', transaction_id='TXN123457'),
        Payment(booking_id=booking_ids[2], order_id=None, amount=320.40, status='cancelled', transaction_id='TXN123458'),
        
        Payment(booking_id=None, order_id=order_ids[0], amount=500.00, status='completed', transaction_id='TXN123459'),
        Payment(booking_id=None, order_id=order_ids[1], amount=750.25, status='completed', transaction_id='TXN123460'),
        Payment(booking_id=None, order_id=order_ids[2], amount=1000.00, status='pending', transaction_id='TXN123461'),
    ]

    # Add payments to the database
    db.session.add_all(payments)
    db.session.commit()
    
def seed_sellers():
    users = User.query.all()
    
    if not users:
        raise ValueError("No users found. Please seed the users first.")

    sellers = [
        Seller(
            user_id=users[0].id,  
            shop_name='Trendy Apparel',
            location='Sarit Center',  
            contact_info='contact@trendyapparel.com, +254712345678',
            created_at=datetime.utcnow()
        ),
        Seller(
            user_id=users[1].id,  
            shop_name='Gadget Corner',
            location='Two Rivers Mall',  
            contact_info='contact@gadgetcorner.com, +254723456789',
            created_at=datetime.utcnow()
        ),
        Seller(
            user_id=users[2].id,  
            shop_name='Fragrance World',
            location='Yaya Center',  
            contact_info='contact@fragranceworld.com, +254734567890',
            created_at=datetime.utcnow()
        ),
        Seller(
            user_id=users[3].id,  
            shop_name='Footwear Haven',
            location='Westlands Mall',  
            contact_info='contact@footwearhaven.com, +254745678901',
            created_at=datetime.utcnow()
        ),
        Seller(
            user_id=users[4].id,  
            shop_name='Gourmet Delights',
            location='Village Market', 
            contact_info='contact@gourmetdelights.com, +254756789012',
            created_at=datetime.utcnow()
        ),
        
    ]

    # Add sellers to the database
    db.session.add_all(sellers)
    db.session.commit()

    
    
# Seed Stalls
   
def seed_stalls():
    
    seller_ids = [seller.id for seller in Seller.query.all()]

    if not seller_ids:
        raise ValueError("No sellers found. Please seed the sellers first.")

    stalls = [
        Stall(
            seller_id=seller_ids[0],  # Replace with appropriate seller_id
            stall_name='Trendy Apparel',
            description='A stall offering the latest in fashion and accessories.',
            location='Sarit Center',
            image_url='https://example.com/images/stall1.jpg'
        ),
        Stall(
            seller_id=seller_ids[1],  # Replace with appropriate seller_id
            stall_name='Gadget Corner',
            description='Your go-to place for the latest electronics and gadgets.',
            location='Two Rivers Mall',
            image_url='https://example.com/images/stall2.jpg'
        ),
        Stall(
            seller_id=seller_ids[2],  # Replace with appropriate seller_id
            stall_name='Fragrance World',
            description='A stall specializing in perfumes and colognes from top brands.',
            location='Yaya Center',
            image_url='https://example.com/images/stall3.jpg'
        ),
        Stall(
            seller_id=seller_ids[3],  # Replace with appropriate seller_id
            stall_name='Footwear Haven',
            description='A wide selection of shoes for every occasion.',
            location='Westlands Mall',
            image_url='https://example.com/images/stall4.jpg'
        ),
        Stall(
            seller_id=seller_ids[4],  # Replace with appropriate seller_id
            stall_name='Gourmet Delights',
            description='Delicious food products and gourmet ingredients.',
            location='Village Market',
            image_url='https://example.com/images/stall5.jpg'
        ),
       
    ]

    # Add stalls to the database
    db.session.add_all(stalls)
    db.session.commit()
    
def seed_passengers():
    users = User.query.all()
    
    if not users:
        raise ValueError("No users found. Please seed the users first.")

    passengers = [
        Passenger(
            user_id=users[0].id,  
            contact_info='1234 Elm Street, Nairobi, +254712345678',
            created_at=datetime.utcnow()
        ),
        Passenger(
            user_id=users[1].id,  
            contact_info='5678 Maple Avenue, Nairobi, +254723456789',
            created_at=datetime.utcnow()
        ),
        Passenger(
            user_id=users[2].id,  
            contact_info='9101 Oak Drive, Nairobi, +254734567890',
            created_at=datetime.utcnow()
        ),
        Passenger(
            user_id=users[3].id,  
            contact_info='1213 Pine Road, Nairobi, +254745678901',
            created_at=datetime.utcnow()
        ),
        Passenger(
            user_id=users[4].id,  
            contact_info='1415 Cedar Lane, Nairobi, +254756789012',
            created_at=datetime.utcnow()
        ),
    ]

    # Add passengers to the database
    db.session.add_all(passengers)
    db.session.commit()
    

# Run all seed functions
def  seed_db():
    seed_users()
    seed_sellers()
    seed_stalls()
    seed_drivers()
    seed_buses()
    seed_routes()
    seed_schedules()
    seed_bookings()
    seed_products()
    seed_orders()
    seed_order_items()
    seed_payments()
    seed_comments()
    seed_reviews()
    seed_passengers()
    
    
    
    
if __name__ == '__main__':
    with app.app_context():
        seed_db()
    
