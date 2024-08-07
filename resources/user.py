from flask import request, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, User, Product, Order, OrderItem, Bus, Route,Driver, Passenger, Seller
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

user_parser = reqparse.RequestParser()
user_parser.add_argument('username', type=str, required=True, help="Username cannot be blank")
user_parser.add_argument('email', type=str, required=True, help="Email cannot be blank")
user_parser.add_argument('password', type=str, required=True, help="Password cannot be blank")
user_parser.add_argument('role', type=str, required=True, help="Role cannot be blank")


class DriverResource(Resource):
    def get(self):
        try:
            drivers = Driver.query.all()
            return [driver.to_dict() for driver in drivers], 200
        except Exception as e:
            return {'message': str(e)}, 500

    def post(self):
        args = user_parser.parse_args()
        try:
            driver = Driver(name=args['username'], contact_info=args['email'])
            db.session.add(driver)
            db.session.commit()
            return driver.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    @jwt_required()
    def post(self):
        """Add a new route for the bus"""
        data = request.get_json()
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'driver':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            bus = Bus.query.filter_by(driver_id=user_id).first()
            if not bus:
                return {"message": "No bus assigned to this driver", "status": "fail"}, 404

            route = Route(
                bus_id=bus.id,
                start_location=data['start_location'],
                end_location=data['end_location'],
                departure_time=data['departure_time'],
                arrival_time=data['arrival_time']
            )
            db.session.add(route)
            db.session.commit()
            return {"message": "Route added successfully", "status": "success"}, 201
        except Exception as e:
            logger.error(f"Error adding route: {e}")
            return {"message": "Error adding route", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def get(self):
        """View booked seats and issued tickets"""
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'driver':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            bus = Bus.query.filter_by(driver_id=user_id).first()
            if not bus:
                return {"message": "No bus assigned to this driver", "status": "fail"}, 404

            routes = Route.query.filter_by(bus_id=bus.id).all()
            tickets_data = []

            for route in routes:
                booked_seats = Ticket.query.filter_by(route_id=route.id).count()
                tickets = Ticket.query.filter_by(route_id=route.id).all()
                tickets_info = [{"passenger_id": ticket.passenger_id, "seat_number": ticket.seat_number} for ticket in tickets]

                tickets_data.append({
                    "route_id": route.id,
                    "start_location": route.start_location,
                    "end_location": route.end_location,
                    "departure_time": route.departure_time,
                    "arrival_time": route.arrival_time,
                    "booked_seats": booked_seats,
                    "tickets": tickets_info
                })

            return {"routes": tickets_data}, 200
        except Exception as e:
            logger.error(f"Error retrieving tickets: {e}")
            return {"message": "Error retrieving tickets", "status": "fail", "error": str(e)}, 500

class PassengerResource(Resource):
    def get(self):
        try:
            passengers = Passenger.query.all()
            return [passenger.to_dict() for passenger in passengers], 200
        except Exception as e:
            return {'message': str(e)}, 500

    def post(self):
        args = user_parser.parse_args()
        try:
            passenger = Passenger(user_id=args['username'], contact_info=args['email'])
            db.session.add(passenger)
            db.session.commit()
            return passenger.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500
    @jwt_required()
    def get(self):
        """View available buses and book tickets"""
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'passenger':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            # Assuming we have a Route model to list available routes
            routes = Route.query.all()
            route_data = []

            for route in routes:
                route_data.append({
                    "route_id": route.id,
                    "start_location": route.start_location,
                    "end_location": route.end_location,
                    "departure_time": route.departure_time,
                    "arrival_time": route.arrival_time
                })

            return {"routes": route_data}, 200
        except Exception as e:
            logger.error(f"Error retrieving routes: {e}")
            return {"message": "Error retrieving routes", "status": "fail", "error": str(e)}, 500

class SellerResource(Resource):
    def get(self):
        try:
            sellers = Seller.query.all()
            return [seller.to_dict() for seller in sellers], 200
        except Exception as e:
            return {'message': str(e)}, 500

    def post(self):
        args = user_parser.parse_args()
        try:
            seller = Seller(user_id=args['username'], shop_name=args['email'], location=args.get('location'), contact_info=args['email'])
            db.session.add(seller)
            db.session.commit()
            return seller.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

    @jwt_required()
    def post(self):
        """Add or update product stock"""
        data = request.get_json()
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'seller':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            product = Product.query.filter_by(name=data['name'], artisan_id=user_id).first()

            if product:
                product.description = data['description']
                product.price = data['price']
                product.available_quantity = data['available_quantity']
                product.shop_name = data['shop_name']
                product.location = data['location']
            else:
                product = Product(
                    name=data['name'],
                    description=data['description'],
                    price=data['price'],
                    available_quantity=data['available_quantity'],
                    artisan_id=user_id,
                    shop_name=data['shop_name'],
                    location=data['location']
                )
                db.session.add(product)

            db.session.commit()
            return {"message": "Stock updated successfully", "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error adding/updating stock: {e}")
            return {"message": "Error adding/updating stock", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def get(self):
        """View orders for the seller's products"""
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'seller':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            products = Product.query.filter_by(artisan_id=user_id).all()
            product_ids = [product.id for product in products]
            order_items = OrderItem.query.filter(OrderItem.product_id.in_(product_ids)).all()
            order_ids = [item.order_id for item in order_items]
            orders = Order.query.filter(Order.id.in_(order_ids)).all()

            order_data = []
            for order in orders:
                total_amount = sum(item.unit_price * item.quantity for item in order_items if item.order_id == order.id)
                order_data.append({
                    "order_id": order.id,
                    "total_amount": total_amount,
                    "status": order.status,
                    "created_at": order.created_at
                })

            return {"orders": order_data}, 200
        except Exception as e:
            logger.error(f"Error retrieving orders: {e}")
            return {"message": "Error retrieving orders", "status": "fail", "error": str(e)}, 500

class BuyerResource(Resource):
    
    def get(self):
        try:
            buyers = User.query.filter_by(role='buyer').all()
            return [buyer.to_dict() for buyer in buyers], 200
        except Exception as e:
            return {'message': str(e)}, 500
    @jwt_required()
    def post(self):
        """Place an order for products"""
        data = request.get_json()
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'buyer':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            product = Product.query.get(data['product_id'])
            if not product or product.available_quantity < data['quantity']:
                return {"message": "Product not available or insufficient quantity", "status": "fail"}, 400

            order = Order(user_id=user_id, total_price=product.price * data['quantity'])
            db.session.add(order)
            db.session.commit()

            order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=data['quantity'], unit_price=product.price)
            db.session.add(order_item)
            product.available_quantity -= data['quantity']
            db.session.commit()

            return {"message": "Order placed successfully", "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {"message": "Error placing order", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def get(self):
        """View the buyer's orders"""
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'buyer':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            orders = Order.query.filter_by(user_id=user_id).all()
            order_data = []
            for order in orders:
                order_items = OrderItem.query.filter_by(order_id=order.id).all()
                items_data = [{"product_id": item.product_id, "quantity": item.quantity, "unit_price": item.unit_price} for item in order_items]
                total_amount = sum(item.unit_price * item.quantity for item in order_items)
                order_data.append({
                    "order_id": order.id,
                    "total_amount": total_amount,
                    "status": order.status,
                    "created_at": order.created_at,
                    "items": items_data
                })

            return {"orders": order_data}, 200
        except Exception as e:
            logger.error(f"Error retrieving orders: {e}")
            return {"message": "Error retrieving orders", "status": "fail", "error": str(e)}, 500
