import os 
from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api
from flask_jwt_extended import JWTManager
from  datetime import timedelta
from models import db 
from resources.user import  DriverResource, PassengerResource, SellerResource, BuyerResource



app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
jwt_manager = JWTManager(app)


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

migrate = Migrate(app, db, render_as_batch=True)

api = Api(app)


api.add_resource(DriverResource, '/drivers')
api.add_resource(PassengerResource, '/passengers')
api.add_resource(SellerResource, '/sellers')
api.add_resource(BuyerResource, '/buyers')


