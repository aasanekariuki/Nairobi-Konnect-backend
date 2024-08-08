from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import User, Route
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
