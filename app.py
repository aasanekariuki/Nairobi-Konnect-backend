import os 
from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager
from  datetime import timedelta
from flask_mail import Mail
from flask_mpesa import MpesaAPI


from model import db 
from resources.user import  DriverResource, PassengerResource, SellerResource, BuyerResource
from resources.auth import  SignupResource, LoginResource, VerifyEmailResource
from resources.buses import BusResource, BookingResource, RouteResource, ScheduleResource
from resources.reviews import ReviewRescource
from resources.products import ProductResource


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'Nairobi_konnect_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
jwt_manager = JWTManager(app)
mpesa_api=MpesaAPI(app)



#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI') 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your-email@example.com'
app.config['MAIL_PASSWORD'] = 'your-email-password'
app.config['MAIL_DEFAULT_SENDER'] = 'your-email@example.com'
app.config["API_ENVIRONMENT"] = "sandbox" #sandbox or production
app.config["APP_KEY"] = "..." # App_key from developers portal
app.config["APP_SECRET"] = "..." #App_Secret from developers portal


db.init_app(app)
mail = Mail(app)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

migrate = Migrate(app, db, render_as_batch=True)

api = Api(app)


api.add_resource(DriverResource, '/drivers')
api.add_resource(PassengerResource, '/passengers')
api.add_resource(SellerResource, '/sellers')
api.add_resource(BuyerResource, '/buyers')
api.add_resource(SignupResource, '/signup')
api.add_resource(LoginResource, '/login')
api.add_resource(VerifyEmailResource, '/verify/<string:token>')
api.add_resource(BusResource, '/buses', '/buses/<int:id>')
api.add_resource(BookingResource, '/bookings', '/bookings/<int:id>')
api.add_resource(RouteResource, '/routes', '/routes/<int:id>')
api.add_resource(ScheduleResource, '/schedules', '/schedules/<int:id>')
api.add_resource(ReviewRescource, '/reviews', '/reviews/<int:id>')
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