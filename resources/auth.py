from flask import request
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from flask_bcrypt import generate_password_hash, check_password_hash
from model import db, User
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SECRET_KEY = 'JWT_SECRET_KEY'

class SignupResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str, required=True, help="Username is required")
        self.parser.add_argument('email', type=str, required=True, help="Email address is required")
        self.parser.add_argument('password', type=str, required=True, help="Password is required")
        self.parser.add_argument('role', type=str, required=True, help="Role is required")
        super(SignupResource, self).__init__()

    def post(self):
        data = self.parser.parse_args()
        try:
            username_exists = User.query.filter_by(username=data['username']).first()
            email_exists = User.query.filter_by(email=data['email']).first()
            if username_exists or email_exists:
                if username_exists:
                    return {"message": "Username already taken", "status": "fail"}, 422
                else:
                    return {"message": "Email address already taken", "status": "fail"}, 422

            password_hash = generate_password_hash(data['password']).decode('utf-8')
            new_user = User(username=data['username'], email=data['email'], password_hash=password_hash, role=data['role'])
            db.session.add(new_user)
            db.session.commit()

            return {"message": "User registered successfully.", "status": "success", "user": {"id": new_user.id, "username": new_user.username, "role": new_user.role}}
        except Exception as e:
            logger.error(f"Error during signup: {e}")
            return {"message": "Error creating user", "status": "fail", "error": str(e)}, 500

class LoginResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email', required=True, help="Email address is required")
    parser.add_argument('password', required=True, help="Password is required")

    def post(self):
        data = self.parser.parse_args()
        try:
            user = User.query.filter_by(email=data['email']).first()
            if user and check_password_hash(user.password_hash, data['password']):
                access_token = create_access_token(identity={'id': user.id, 'role': user.role})
                logger.debug(f"Generated Token: {access_token}")
                return {"message": "Login successful", "status": "success", "access_token": access_token, "user": {"id": user.id, "role": user.role}}
            else:
                return {"message": "Invalid credentials", "status": "fail"}, 401
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return {"message": "Error during login", "status": "fail", "error": str(e)}, 500

class ForgotPasswordResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', type=str, required=True, help="Email address is required")
        super(ForgotPasswordResource, self).__init__()

    def post(self):
        data = self.parser.parse_args()
        try:
            user = User.query.filter_by(email=data['email']).first()
            if not user:
                return {"message": "No account associated with this email address.", "status": "fail"}, 404

            # Normally, you would send a reset email here.
            # For simplicity, we'll skip the email sending part and directly return success.
            return {"message": "If an account with that email exists, you will receive a password reset email.", "status": "success"}
        except Exception as e:
            logger.error(f"Error during password reset request: {e}")
            return {"message": "Error processing password reset request", "status": "fail", "error": str(e)}, 500

class ResetPasswordResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('email', type=str, required=True, help="Email address is required")
        self.parser.add_argument('new_password', type=str, required=True, help="New password is required")
        super(ResetPasswordResource, self).__init__()

    def post(self):
        data = self.parser.parse_args()
        try:
            user = User.query.filter_by(email=data['email']).first()
            if not user:
                return {"message": "No account associated with this email address.", "status": "fail"}, 404

            password_hash = generate_password_hash(data['new_password']).decode('utf-8')
            user.password_hash = password_hash
            db.session.commit()
            return {"message": "Password reset successfully."}, 200
        except Exception as e:
            logger.error(f"Error during password reset: {e}")
            return {"message": "Error during password reset", "status": "fail", "error": str(e)}, 500
