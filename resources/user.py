from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, User
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class UserResource(Resource):
    @jwt_required()
    def get(self):
        """View user profile"""
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found", "status": "fail"}, 404

            return {"profile": user.to_dict(), "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error retrieving profile: {e}")
            return {"message": "Error retrieving profile", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def put(self):
        """Update user profile"""
        user_id = get_jwt_identity()['id']
        data = request.get_json()

        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found", "status": "fail"}, 404

            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            # Ensure password is hashed if updated
            if 'password' in data:
                user.password = data['password']  # Ensure you hash the password

            db.session.commit()

            return {"message": "Profile updated successfully", "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            return {"message": "Error updating profile", "status": "fail", "error": str(e)}, 500
