from flask import request, jsonify
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_mail import Message
from model import db, User
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import logging
from app import mail

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SECRET_KEY = 'Nairobi_konnect_key'
EMAIL_CONFIRM_SALT = 'email-confirm-salt'
FORGOT_PASSWORD_SALT = 'forgot-password-salt'

def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=EMAIL_CONFIRM_SALT)

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=FORGOT_PASSWORD_SALT)

def send_verification_email(user_email, token):
    verify_url = f"http://yourdomain.com/verify/{token}"
    subject = "Please verify your email"
    body = f"Click the following link to verify your email: {verify_url}"

    msg = Message(subject, recipients=[user_email], body=body)
    try:
        mail.send(msg)
        logger.debug(f"Verification email sent to {user_email}: {verify_url}")
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {str(e)}")

def send_reset_email(user_email, token):
    reset_url = f"http://yourdomain.com/reset-password/{token}"
    subject = "Password Reset Request"
    body = f"Click the following link to reset your password: {reset_url}"

    msg = Message(subject, recipients=[user_email], body=body)
    try:
        mail.send(msg)
        logger.debug(f"Password reset email sent to {user_email}: {reset_url}")
    except Exception as e:
        logger.error(f"Failed to send email to {user_email}: {str(e)}")

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
            verification_token = generate_verification_token(data['email'])
            new_user = User(username=data['username'], email=data['email'], password_hash=password_hash, role=data['role'], verification_token=verification_token)
            db.session.add(new_user)
            db.session.commit()

            send_verification_email(data['email'], verification_token)

            return {"message": "User registered successfully. Please verify your email.", "status": "success", "user": {"id": new_user.id, "username": new_user.username, "role": new_user.role}}
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
                if not user.is_verified:
                    return {"message": "Email not verified. Please check your email.", "status": "fail"}, 403
                access_token = create_access_token(identity={'id': user.id, 'role': user.role})
                logger.debug(f"Generated Token: {access_token}")
                return {"message": "Login successful", "status": "success", "access_token": access_token, "user": {"id": user.id, "role": user.role}}
            else:
                return {"message": "Invalid credentials", "status": "fail"}, 401
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return {"message": "Error during login", "status": "fail", "error": str(e)}, 500

class VerifyEmailResource(Resource):
    def get(self, token):
        serializer = URLSafeTimedSerializer(SECRET_KEY)
        try:
            email = serializer.loads(token, salt=EMAIL_CONFIRM_SALT, max_age=3600)
        except SignatureExpired:
            return {"message": "Verification token expired. Please request a new one."}, 400
        except BadSignature:
            return {"message": "Invalid verification token."}, 400

        user = User.query.filter_by(email=email).first_or_404()
        if user.is_verified:
            return {"message": "Email already verified."}, 200

        user.is_verified = True
        db.session.commit()
        return {"message": "Email verified successfully."}, 200 

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

            reset_token = generate_reset_token(data['email'])
            send_reset_email(data['email'], reset_token)

            return {"message": "Password reset email sent.", "status": "success"}
        except Exception as e:
            logger.error(f"Error during password reset request: {e}")
            return {"message": "Error processing password reset request", "status": "fail", "error": str(e)}, 500

class ResetPasswordResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('token', type=str, required=True, help="Reset token is required")
        self.parser.add_argument('new_password', type=str, required=True, help="New password is required")
        super(ResetPasswordResource, self).__init__()

    def post(self):
        data = self.parser.parse_args()
        serializer = URLSafeTimedSerializer(SECRET_KEY)
        try:
            email = serializer.loads(data['token'], salt=FORGOT_PASSWORD_SALT, max_age=3600)
        except SignatureExpired:
            return {"message": "Reset token expired. Please request a new one."}, 400
        except BadSignature:
            return {"message": "Invalid reset token."}, 400

        user = User.query.filter_by(email=email).first_or_404()
        password_hash = generate_password_hash(data['new_password']).decode('utf-8')
        user.password_hash = password_hash
        db.session.commit()
        return {"message": "Password reset successfully."}, 200
