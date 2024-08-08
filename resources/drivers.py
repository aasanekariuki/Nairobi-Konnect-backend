from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, User, Bus, Route
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DriverResource(Resource):
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
