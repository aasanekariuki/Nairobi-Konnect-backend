from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, User
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AdminResource(Resource):
    @jwt_required()
    def post(self):
        """Add a new user (driver, seller, buyer, passenger)"""
        data = request.get_json()
        admin_id = get_jwt_identity()['id']

        try:
            admin = User.query.get(admin_id)
            if admin.role != 'admin':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            new_user = User(
                username=data['username'],
                email=data['email'],
                role=data['role'],
                password=data['password']  
            )
            db.session.add(new_user)
            db.session.commit()

            return {"message": "User added successfully", "status": "success"}, 201
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return {"message": "Error adding user", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def delete(self, user_id):
        """Delete a user"""
        admin_id = get_jwt_identity()['id']

        try:
            admin = User.query.get(admin_id)
            if admin.role != 'admin':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found", "status": "fail"}, 404

            db.session.delete(user)
            db.session.commit()

            return {"message": "User deleted successfully", "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return {"message": "Error deleting user", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def get(self):
        """View all users and activities"""
        admin_id = get_jwt_identity()['id']

        try:
            admin = User.query.get(admin_id)
            if admin.role != 'admin':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            users = User.query.all()
            user_data = [user.to_dict() for user in users]

            return {"users": user_data, "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error retrieving users: {e}")
            return {"message": "Error retrieving users", "status": "fail", "error": str(e)}, 500
