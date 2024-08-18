from flask import request, jsonify, make_response
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import logging
import uuid
import json
import logging

from model import db, Booking, User

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BookingResource(Resource):
    
    # only = ('id', 'user_id', 'schedule_id', 'passenger_id', 'seat_number', 'payment_status', 'ticket_number', 'created_at' )



    @jwt_required()
    def get(self, booking_id=None):
        """
        Retrieve a specific booking or all bookings for the authenticated passenger.
        If `booking_id` is provided, it returns details of that specific booking.
        Otherwise, it returns all bookings associated with the authenticated user.
        """
        try:
            # Extract the user_id from the dictionary returned by get_jwt_identity()
            identity = get_jwt_identity()
            user_id = identity['id']  # Extracting the 'id' part of the dictionary

            logger.debug(f"get_jwt_identity() returned: {identity}")

            user = User.query.get(user_id)  # Correct usage of user_id

            if not user:
                return make_response(json.dumps({"message": "User not found", "status": "fail"}), 404, {'Content-Type': 'application/json'})

            if booking_id:
                booking = Booking.query.filter_by(id=booking_id, passenger_id=user_id).first()
                if not booking:
                    return make_response(json.dumps({"message": "Booking not found", "status": "fail"}), 404, {'Content-Type': 'application/json'})
                return make_response(json.dumps(booking.to_dict()), 200, {'Content-Type': 'application/json'})

            # If no booking_id is provided, return all bookings for the user
            bookings = Booking.query.filter_by(passenger_id=user_id).all()
            bookings_list = [booking.to_dict() for booking in bookings]
            return make_response(json.dumps(bookings_list), 200, {'Content-Type': 'application/json'})

        except Exception as e:
            logger.error(f"Error retrieving bookings: {e}")
            return make_response(json.dumps({"message": "Error retrieving bookings", "status": "fail", "error": str(e)}), 500, {'Content-Type': 'application/json'})

    @jwt_required()
    def post(self):
        """
        Create a new booking.
        Requires the following data: schedule_id, passenger_id, seat_number, payment_status.
        """
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return {"message": "User not found", "status": "fail"}, 404

            new_booking = Booking(
                user_id=user_id,  # Automatically link to the authenticated user
                schedule_id=data.get('schedule_id'),
                passenger_id=data.get('passenger_id'),
                seat_number=data.get('seat_number'),
                ticket_number=str(uuid.uuid4()),  # Generate a unique ticket number
                payment_status=data.get('payment_status', False),
                created_at=datetime.now(),
            )
            
            db.session.add(new_booking)
            db.session.commit()
            return make_response(jsonify(new_booking.to_dict()), 201)

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Integrity error creating booking: {e}")
            return make_response(jsonify({"message": "Error creating booking", "error": str(e)}), 400)

        except Exception as e:
            logger.error(f"Error creating booking: {e}")
            db.session.rollback()
            return make_response(jsonify({"message": "Error creating booking", "status": "fail", "error": str(e)})), 500

    @jwt_required()
    def put(self, booking_id):
        """
        Update an existing booking.
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return {"message": "User not found", "status": "fail"}, 404

            booking = Booking.query.filter_by(id=booking_id, passenger_id=user_id).first()
            if not booking:
                return {"message": "Booking not found", "status": "fail"}, 404

            data = request.get_json()
            booking.schedule_id = data.get('schedule_id', booking.schedule_id)
            booking.seat_number = data.get('seat_number', booking.seat_number)
            booking.payment_status = data.get('payment_status', booking.payment_status)
            booking.ticket_number = data.get('ticket_number', booking.ticket_number)  # Optional
            
            db.session.commit()
            return jsonify(booking.to_dict()), 200

        except Exception as e:
            logger.error(f"Error updating booking: {e}")
            db.session.rollback()
            return {"message": "Error updating booking", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def delete(self, booking_id):
        """
        Delete a booking.
        """
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return {"message": "User not found", "status": "fail"}, 404

            booking = Booking.query.filter_by(id=booking_id, passenger_id=user_id).first()
            if not booking:
                return {"message": "Booking not found", "status": "fail"}, 404

            db.session.delete(booking)
            db.session.commit()
            return make_response(jsonify({"message": "Booking deleted successfully", "status": "success"}), 200)

        except Exception as e:
            logger.error(f"Error deleting booking: {e}")
            db.session.rollback()
            return make_response(jsonify({"message": "Error deleting booking", "status": "fail", "error": str(e)}), 500)

        
        
        
        
