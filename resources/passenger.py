from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from model import db, User, Route, Booking
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PassengerResource(Resource):
    @jwt_required()
    def get(self):
        """View available buses and book tickets"""
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'passenger':
                return {"message": "Unauthorized access", "status": "fail"}, 403

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

    @jwt_required()
    def post(self):
        """Book a ticket for a route"""
        data = request.get_json()
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'passenger':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            route = Route.query.get(data['route_id'])
            if not route:
                return {"message": "Route not found", "status": "fail"}, 404

            if route.available_seats < data['number_of_tickets']:
                return {"message": "Not enough seats available", "status": "fail"}, 400

            # Deduct the number of available seats
            route.available_seats -= data['number_of_tickets']

            booking = Booking(
                passenger_id=user_id,
                route_id=route.id,
                number_of_tickets=data['number_of_tickets'],
                total_price=route.price_per_ticket * data['number_of_tickets'],
                status='booked'
            )

            db.session.add(booking)
            db.session.commit()

            return {"message": "Booking successful", "status": "success"}, 201
        except Exception as e:
            logger.error(f"Error booking ticket: {e}")
            return {"message": "Error booking ticket", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def delete(self):
        """Cancel a booking"""
        data = request.get_json()
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'passenger':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            booking = Booking.query.filter_by(id=data['booking_id'], passenger_id=user_id).first()

            if not booking:
                return {"message": "Booking not found", "status": "fail"}, 404

            if booking.status != 'booked':
                return {"message": "Cannot cancel a non-active booking", "status": "fail"}, 400

            route = Route.query.get(booking.route_id)
            route.available_seats += booking.number_of_tickets

            db.session.delete(booking)
            db.session.commit()

            return {"message": "Booking canceled successfully", "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error canceling booking: {e}")
            return {"message": "Error canceling booking", "status": "fail", "error": str(e)}, 500
