import os 
from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_mail import Mail, Message
from dotenv import load_dotenv

from model import db

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
jwt_manager = JWTManager(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI') 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'

db.init_app(app)
mail = Mail(app)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

migrate = Migrate(app, db, render_as_batch=True)

api = Api(app)


from resources.driver import DriverResource
from resources.passenger import PassengerResource
from resources.seller import SellerResource
from resources.buyer import BuyerResource
from resources.auth import SignupResource, LoginResource, VerifyEmailResource
from resources.profile import ProfileResource
from resources.admin import AdminResource
from resources.user import UserResource
from resources.auth import ForgotPasswordResource, ResetPasswordResource
from resources.orders import OrderResource, OrderItemsResource
from resources.payment import PaymentStatusResource
from resources.stall import StallResource
from resources.products import ProductResource

from resources.mpesa import StkPush

api.add_resource(StkPush, '/stk_push')
api.add_resource(DriverResource, '/drivers')
api.add_resource(PassengerResource, '/passengers')
api.add_resource(SellerResource, '/sellers')
api.add_resource(BuyerResource, '/buyers')
api.add_resource(SignupResource, '/signup')
api.add_resource(LoginResource, '/login')
api.add_resource(VerifyEmailResource, '/verify/<string:token>')
api.add_resource(ProfileResource, '/profile')
api.add_resource(AdminResource, '/admin', '/admin/<int:user_id>')
api.add_resource(UserResource, '/user')
api.add_resource(ForgotPasswordResource, '/forgot-password')
api.add_resource(ResetPasswordResource, '/reset-password')
api.add_resource(OrderResource, '/orders', '/orders/<int:order_id>')
api.add_resource(OrderItemsResource, '/order_items', '/order_items/<int:order_item_id>')
api.add_resource(PaymentStatusResource, '/payment_status/<string:transaction_id>')
api.add_resource(StallResource, '/stalls', '/stalls/<int:stall_id>')
api.add_resource(ProductResource, '/products', '/products/<int:product_id>')




@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5000)
