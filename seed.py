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
        {'name': 'Casual Shirt', 'description': 'Comfortable casual shirt', 'price': 29.99, 'available_quantity': 50, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://i.pinimg.com/236x/65/8b/95/658b9511a99127c65c0410a43940850b.jpg'},
        {'name': 'Formal Suit', 'description': 'Stylish formal suit', 'price': 199.99, 'available_quantity': 30, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://i.pinimg.com/236x/d4/c2/be/d4c2be1c665e61e9598fe8cae93e1c66.jpg'},
        {'name': 'Denim Jeans', 'description': 'Trendy denim jeans', 'price': 49.99, 'available_quantity': 60, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://i.pinimg.com/236x/ef/23/83/ef23838bf2e41a4bcffc3b1474bec4b2.jpg'},
        {'name': 'Summer Dress', 'description': 'Light and airy summer dress', 'price': 39.99, 'available_quantity': 40, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://i.pinimg.com/236x/3a/27/6f/3a276fb307fbb45337ca6a5b3c081e26.jpg'},
        {'name': 'Winter Jacket', 'description': 'Warm winter jacket', 'price': 149.99, 'available_quantity': 20, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://i.pinimg.com/236x/52/16/5a/52165a61af64fd3ad1d186bc5c3067af.jpg'},
        {'name': 'Leather Jacket', 'description': 'Stylish leather jacket', 'price': 179.99, 'available_quantity': 15, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://i.pinimg.com/236x/31/a8/2a/31a82a3c0f2ae03053ae200462fe82bf.jpg'},
        {'name': 'Turtleneck Sweater', 'description': 'Warm turtleneck sweater', 'price': 39.99, 'available_quantity': 25, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://i.pinimg.com/236x/2b/87/e1/2b87e14dc1f13703a715def266367221.jpg'},
        {'name': 'Polo Shirt', 'description': 'Classic polo shirt', 'price': 34.99, 'available_quantity': 45, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://i.pinimg.com/236x/c2/68/39/c26839d442276305b897b6148eadb9f3.jpg'},
        {'name': 'Cardigan Sweater', 'description': 'Cozy cardigan sweater', 'price': 44.99, 'available_quantity': 20, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://i.pinimg.com/236x/67/c8/c1/67c8c1339100eace3a1e6ee9535bade2.jpg'},
        {'name': 'Cargo Pants', 'description': 'Durable cargo pants', 'price': 39.99, 'available_quantity': 30, 'stall_id': 1, 'created_at': datetime.utcnow(), 'location': 1, 'shop_name': 'Fashion Hub', 'image_url': 'https://i.pinimg.com/236x/37/74/1f/37741fc0d2455766c778953aaec64f2c.jpg'},

        # Shoe Paradise - Shoes
        {'name': 'Running Shoes', 'description': 'Comfortable running shoes', 'price': 89.99, 'available_quantity': 40, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://i.pinimg.com/236x/2c/9c/ad/2c9cad166f77d3a8394e0c234c865c5a.jpg'},
        {'name': 'Leather Boots', 'description': 'Durable leather boots', 'price': 129.99, 'available_quantity': 20, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://i.pinimg.com/236x/cc/d4/f9/ccd4f9d26ac01b3c7586fc56a4df6d6d.jpg'},
        {'name': 'High Heels', 'description': 'Elegant high heels', 'price': 99.99, 'available_quantity': 35, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://i.pinimg.com/236x/c1/3c/3a/c13c3a2e65cf98a8c3744ce9f5e2cd9c.jpg'},
        {'name': 'Sneakers', 'description': 'Stylish everyday sneakers', 'price': 79.99, 'available_quantity': 50, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://i.pinimg.com/236x/cc/42/b8/cc42b8e76033a7b9d829e99c05e87f13.jpg'},
        {'name': 'Sandals', 'description': 'Comfortable summer sandals', 'price': 49.99, 'available_quantity': 60, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://i.pinimg.com/236x/d3/4b/3b/d34b3bfb392b1b979bc0032585574fa8.jpg'},
        {'name': 'Loafers', 'description': 'Casual leather loafers', 'price': 89.99, 'available_quantity': 25, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://example.com/images/loafers.jpg'},
        {'name': 'Chelsea Boots', 'description': 'Sleek Chelsea boots', 'price': 139.99, 'available_quantity': 15, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://i.pinimg.com/236x/c3/4e/ab/c34eab72703a1bb6127a5347c83c746d.jpg'},
        {'name': 'Flip Flops', 'description': 'Casual flip flops', 'price': 19.99, 'available_quantity': 70, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://i.pinimg.com/236x/e3/af/52/e3af52993146bc07272800dac109b04b.jpg'},
        {'name': 'Oxford Shoes', 'description': 'Classic Oxford shoes', 'price': 109.99, 'available_quantity': 20, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://i.pinimg.com/236x/39/af/f2/39aff2691751ea79a501956858e0775c.jpg'},
        {'name': 'Hiking Boots', 'description': 'Durable hiking boots', 'price': 149.99, 'available_quantity': 15, 'stall_id': 2, 'created_at': datetime.utcnow(), 'location': 2, 'shop_name': 'Shoe Paradise', 'image_url': 'https://i.pinimg.com/236x/75/3d/a4/753da4a64026ec2a74077d49f3f1ba80.jpg'},

        # Perfume Palace - Perfumes
        {'name': 'Chanel No. 5', 'description': 'Classic Chanel fragrance', 'price': 99.99, 'available_quantity': 25, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://i.pinimg.com/236x/25/51/63/255163b135d1e9c837b079828bc1ef94.jpg'},
        {'name': 'Dior Sauvage', 'description': 'Masculine Dior fragrance', 'price': 79.99, 'available_quantity': 35, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://i.pinimg.com/236x/41/db/a4/41dba438abe65e730db76815df2444fd.jpg'},
        {'name': 'Gucci Bloom', 'description': 'Floral Gucci fragrance', 'price': 89.99, 'available_quantity': 30, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://i.pinimg.com/236x/0a/ad/3f/0aad3fbfd965278f88e251459d5e2e4b.jpg'},
        {'name': 'YSL Black Opium', 'description': 'Bold YSL fragrance', 'price': 109.99, 'available_quantity': 20, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://i.pinimg.com/236x/c4/1b/30/c41b309b6e77271bea4696eb24a4ed33.jpg'},
        {'name': 'Versace Eros', 'description': 'Sensual Versace fragrance', 'price': 99.99, 'available_quantity': 25, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://i.pinimg.com/236x/b3/b4/07/b3b407f29b2f666e2b8c151fceabe766.jpg'},
        {'name': 'Tom Ford Oud Wood', 'description': 'Luxurious Tom Ford fragrance', 'price': 149.99, 'available_quantity': 15, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://i.pinimg.com/236x/90/b3/fc/90b3fc94418dbf6c2bbeaf5812c7f39c.jpg'},
        {'name': 'Creed Aventus', 'description': 'Iconic Creed fragrance', 'price': 199.99, 'available_quantity': 10, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://i.pinimg.com/236x/e0/ba/43/e0ba43f5ab9c57954c5a55b713ad7c32.jpg'},
        {'name': 'Marc Jacobs Daisy', 'description': 'Light Marc Jacobs fragrance', 'price': 89.99, 'available_quantity': 30, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://i.pinimg.com/236x/82/21/b3/8221b347a88cedc8d6a1cad5d42094b6.jpg'},
        {'name': 'Jo Malone Lime Basil & Mandarin', 'description': 'Citrus Jo Malone fragrance', 'price': 129.99, 'available_quantity': 15, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://i.pinimg.com/236x/f5/53/e2/f553e29494604ef5f1e7d00687315969.jpg.jpg'},
        {'name': 'Calvin Klein CK One', 'description': 'Fresh Calvin Klein fragrance', 'price': 69.99, 'available_quantity': 40, 'stall_id': 3, 'created_at': datetime.utcnow(), 'location': 3, 'shop_name': 'Perfume Palace', 'image_url': 'https://i.pinimg.com/236x/23/95/28/23952839a10896d9770e56c2acf33d9a.jpg'},
          # Electronics World - Electronics
        {'name': 'Smartphone', 'description': 'Latest model smartphone', 'price': 699.99, 'available_quantity': 25, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://i.pinimg.com/236x/66/c2/3f/66c23f9566266ec63f39b2dac1a56585.jpg'},
        {'name': 'Laptop', 'description': 'High-performance laptop', 'price': 1099.99, 'available_quantity': 15, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://i.pinimg.com/236x/05/71/a1/0571a140c8f2c73d60ad88ffd4a2bbb4.jpg'},
        {'name': 'Smartwatch', 'description': 'Stylish smartwatch', 'price': 199.99, 'available_quantity': 30, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://i.pinimg.com/236x/65/7a/5e/657a5e304359ba0a7078b41106165d7a.jpg'},
        {'name': 'Bluetooth Headphones', 'description': 'Noise-cancelling headphones', 'price': 149.99, 'available_quantity': 40, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://i.pinimg.com/474x/68/9c/9b/689c9b23e5254514197b9b209310e34d.jpg'},
        {'name': 'Gaming Console', 'description': 'Next-gen gaming console', 'price': 499.99, 'available_quantity': 10, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://i.pinimg.com/236x/2c/5b/02/2c5b02812870dfbb3ea99fb7b78f9613.jpg'},
        {'name': '4K TV', 'description': 'Ultra HD 4K television', 'price': 899.99, 'available_quantity': 20, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://i.pinimg.com/236x/3f/15/f0/3f15f028b7e18bd4a0667aba31481705.jpg'},
        {'name': 'Wireless Earbuds', 'description': 'Compact wireless earbuds', 'price': 129.99, 'available_quantity': 50, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://i.pinimg.com/236x/93/1b/f7/931bf73e5f0a90fcc0c68e93927c98e6.jpg'},
        {'name': 'Tablet', 'description': 'Portable high-resolution tablet', 'price': 499.99, 'available_quantity': 30, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://i.pinimg.com/236x/31/05/64/310564954f727378364e446d8012d346.jpg'},
        {'name': 'Digital Camera', 'description': 'High-resolution digital camera', 'price': 749.99, 'available_quantity': 15, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://i.pinimg.com/236x/c8/c2/46/c8c246382350d0f66561a5d4c2b30baa.jpg'},
        {'name': 'Home Theater System', 'description': 'Immersive home theater experience', 'price': 599.99, 'available_quantity': 10, 'stall_id': 4, 'created_at': datetime.utcnow(), 'location': 4, 'shop_name': 'Electronics World', 'image_url': 'https://i.pinimg.com/236x/a0/98/42/a098425deff5334369b35cb52e5c6c07.jpg'},

        # Food Basket - Food
        {'name': 'Organic Apples', 'description': 'Fresh organic apples', 'price': 3.99, 'available_quantity': 100, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://i.pinimg.com/236x/b3/fa/eb/b3faeb903bd3e503b96a9cc08540547e.jpg'},
        {'name': 'Granola Bars', 'description': 'Healthy granola bars', 'price': 5.99, 'available_quantity': 50, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://i.pinimg.com/236x/92/28/10/9228106e7457f9c609650b620a0386e2.jpg'},
        {'name': 'Almond Milk', 'description': 'Vegan almond milk', 'price': 4.99, 'available_quantity': 40, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://i.pinimg.com/236x/20/28/9c/20289c04c9fe6341588a7d33c5457c25.jpg'},
        {'name': 'Quinoa', 'description': 'Healthy quinoa grains', 'price': 6.99, 'available_quantity': 60, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://i.pinimg.com/236x/ed/57/be/ed57beb78569aac634c6978040062348.jpg'},
        {'name': 'Organic Honey', 'description': 'Pure organic honey', 'price': 7.99, 'available_quantity': 35, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://i.pinimg.com/236x/ec/65/bc/ec65bcb0bc2912e015e927d50678217d.jpg'},
        {'name': 'Greek Yogurt', 'description': 'Creamy Greek yogurt', 'price': 3.49, 'available_quantity': 80, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://i.pinimg.com/236x/6c/1e/9a/6c1e9a24ad599212c76b3bd1de0c1fa9.jpg'},
        {'name': 'Avocado', 'description': 'Fresh avocados', 'price': 1.99, 'available_quantity': 120, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://i.pinimg.com/236x/a9/10/f7/a910f76ccc5a6a547078d18eb4a3189d.jpg'},
        {'name': 'Whole Grain Bread', 'description': 'Healthy whole grain bread', 'price': 2.99, 'available_quantity': 50, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://i.pinimg.com/236x/fe/05/a8/fe05a8428596dddcb50e83c90247aaae.jpg'},
        {'name': 'Dark Chocolate', 'description': 'Rich dark chocolate', 'price': 3.99, 'available_quantity': 70, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://i.pinimg.com/236x/93/a8/64/93a864df6dd119e12bc99c07635c99ad.jpg'},
        {'name': 'Kombucha', 'description': 'Refreshing kombucha drink', 'price': 3.49, 'available_quantity': 50, 'stall_id': 5, 'created_at': datetime.utcnow(), 'location': 5, 'shop_name': 'Food Basket', 'image_url': 'https://i.pinimg.com/236x/45/30/39/4530394df6c81be2abf1a99af04a1b8f.jpg'},

        # Jewel Collection - Jewelry
        {'name': 'Gold Necklace', 'description': 'Elegant gold necklace', 'price': 499.99, 'available_quantity': 5, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://i.pinimg.com/236x/92/5d/f4/925df42973535e40357afab9ee52d8dd.jpg'},
        {'name': 'Silver Bracelet', 'description': 'Beautiful silver bracelet', 'price': 199.99, 'available_quantity': 10, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://i.pinimg.com/236x/8c/54/46/8c5446ba4a9a1921aa98550964da16e8.jpg'},
        {'name': 'Diamond Ring', 'description': 'Stunning diamond ring', 'price': 999.99, 'available_quantity': 3, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://i.pinimg.com/236x/e0/5a/0a/e05a0a735a1a568d8fd8cd42a069eb35.jpg'},
        {'name': 'Pearl Earrings', 'description': 'Classic pearl earrings', 'price': 299.99, 'available_quantity': 8, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://i.pinimg.com/236x/c5/61/6b/c5616b91d3b47169e7fc909cc5b8ee26.jpg'},
        {'name': 'Ruby Pendant', 'description': 'Elegant ruby pendant', 'price': 799.99, 'available_quantity': 4, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://i.pinimg.com/236x/15/d7/66/15d766e56aff14864d6dff4e030a631b.jpg'},
        {'name': 'Gold Watch', 'description': 'Luxury gold watch', 'price': 1199.99, 'available_quantity': 2, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://i.pinimg.com/236x/96/e8/7d/96e87d00ffab073cf5888f7ca418bee1.jpg'},
        {'name': 'Emerald Brooch', 'description': 'Vintage emerald brooch', 'price': 699.99, 'available_quantity': 3, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://i.pinimg.com/236x/34/4a/52/344a522a95aadd12c62e7a0cdb77da57.jpg'},
        {'name': 'Sapphire Cufflinks', 'description': 'Sophisticated sapphire cufflinks', 'price': 249.99, 'available_quantity': 6, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://i.pinimg.com/236x/ae/83/13/ae8313d150597c3d55b245733c104f48.jpg'},
        {'name': 'Platinum Band', 'description': 'Sleek platinum band', 'price': 599.99, 'available_quantity': 5, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://i.pinimg.com/236x/6a/d3/8c/6ad38c4faab092676e71d5bfffed7b2a.jpg'},
        {'name': 'Opal Ring', 'description': 'Unique opal ring', 'price': 399.99, 'available_quantity': 4, 'stall_id': 6, 'created_at': datetime.utcnow(), 'location': 6, 'shop_name': 'Jewel Collection', 'image_url': 'https://i.pinimg.com/236x/f4/f0/f0/f4f0f0ac61d7c58c6a02399b55612c99.jpg'},
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
    
