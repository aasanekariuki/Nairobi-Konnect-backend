from flask import request
from flask_restful import Resource, reqparse
from model import db, Bus, Booking
# from datetime import datetime, time

class BusResource(Resource):
    def get(self):
        buses = Bus.query.all()
        return [bus.to_dict() for bus in buses], 200
    
    def post(self):
        data = request.get_json()
        driver_id = data.get('driver_id')
        bus_number = data.get('bus_number')
        seat_capacity = data.get('seat_capacity')
        current_location = data.get('current_location')
        
        if not driver_id or not bus_number or not seat_capacity:
            return {"message": "Driver ID, bus number, and seat capacity are required"}, 400
        
        new_bus = Bus(
            driver_id = driver_id,
            bus_number = bus_number,
            seat_capacity = seat_capacity,
            current_location = current_location
        )
        db.session.add(new_bus)
        db.session.commit()
    
    def delete(self, id):
        bus = Bus.query.get_or_404(id)
        db.session.delete(bus)
        db.session.commit()

        return {"message": "Bus deleted successfully"}, 200
    

class BookingResource(Resource):
    def get(self):
        bookings = Booking.query.all()
        return [booking.to_dict() for booking in bookings], 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('bus_id', type=int, required=True, help="Bus ID cannot be blank!")
        parser.add_argument('passenger_name', type=str, required=True, help="Passenger Name cannot be blank!")
        parser.add_argument('seat_number', type=int, required=True, help="Seat Number cannot be blank!")
        args = parser.parse_args()

        new_booking = Booking(
            bus_id=args['bus_id'],
            passenger_name=args['passenger_name'],
            seat_number=args['seat_number']
        )

        db.session.add(new_booking)
        db.session.commit()

        return new_booking.to_dict(), 201
    
    def delete(self, id):
        booking = Booking.query.get_or_404(id)
        db.session.delete(booking)
        db.session.commit()

        return {"message": "Booking deleted successfully"}, 200

# class RouteResource(Resource):
#     def get(self):
#         routes = Route.query.all()
#         return [route.to_dict() for route in routes], 200
    
#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument('origin', type=str, required=True, help="Origin cannot be blank!")
#         parser.add_argument('destination', type=str, required=True, help="Destination cannot be blank!")
#         parser.add_argument('distance', type=float, required=True, help="Distance cannot be blank!")
#         args = parser.parse_args()

#         new_route = Route(
#             origin = args['origin'],
#             destination = args['destination'],
#             distance = args['distance']
#         )

#         db.session.add(new_route)
#         db.session.commit()

#         return new_route.to_dict(), 201
    
#     def delete(self, id):
#         route = Route.query.get_or_404(id)
#         db.session.delete(route)
#         db.session.commit()

#         return {"message": "Route deleted successfully"}, 200