from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import logging
import os
from werkzeug.utils import secure_filename

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

UPLOADS_DEFAULT_DEST = 'uploads'

class ProfileResource(Resource):
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
            
            db.session.commit()
            return {"message": "Profile updated successfully", "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            return {"message": "Error updating profile", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def post(self):
        """Change password"""
        user_id = get_jwt_identity()['id']
        data = request.get_json()

        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found", "status": "fail"}, 404

            if not check_password_hash(user.password_hash, data.get('current_password')):
                return {"message": "Current password is incorrect", "status": "fail"}, 400

            user.password_hash = generate_password_hash(data.get('new_password'))
            db.session.commit()
            return {"message": "Password changed successfully", "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return {"message": "Error changing password", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def post(self, file=None):
        """Upload profile picture"""
        user_id = get_jwt_identity()['id']
        
        if 'file' not in request.files:
            return {"message": "No file provided", "status": "fail"}, 400
        
        file = request.files['file']
        if file.filename == '':
            return {"message": "No selected file", "status": "fail"}, 400
        
        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOADS_DEFAULT_DEST, filename))
            
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found", "status": "fail"}, 404
            
            user.profile_picture = filename
            db.session.commit()
            
            return {"message": "Profile picture updated successfully", "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error uploading profile picture: {e}")
            return {"message": "Error uploading profile picture", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def delete(self):
        """Delete user profile"""
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found", "status": "fail"}, 404

            # Optionally, delete associated profile picture if needed
            if user.profile_picture and os.path.exists(os.path.join(UPLOADS_DEFAULT_DEST, user.profile_picture)):
                os.remove(os.path.join(UPLOADS_DEFAULT_DEST, user.profile_picture))

            db.session.delete(user)
            db.session.commit()
            
            return {"message": "Profile deleted successfully", "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error deleting profile: {e}")
            return {"message": "Error deleting profile", "status": "fail", "error": str(e)}, 500
