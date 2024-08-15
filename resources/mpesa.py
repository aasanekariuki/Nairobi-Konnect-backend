import os
from dotenv import load_dotenv
from flask import request, jsonify, make_response
from flask_restful import Resource
import base64
import requests
from datetime import datetime, timedelta
from model import db, Payment
from flask_jwt_extended import jwt_required, get_jwt_identity

# Global variable to store the token and its expiration
token_info = {
    'token': None,
    'expires_at': None
}
load_dotenv()
def create_token():
    consumer = os.getenv('CONSUMER_KEY')
    secret = os.getenv('SECRET_KEY')
    auth = base64.b64encode(f"{consumer}:{secret}".encode()).decode()

    headers = {
        'Authorization': f'Basic {auth}'
    }

    response = requests.get('https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials', headers=headers)

    if response.status_code == 200:
        data = response.json()
        token_info['token'] = data['access_token']
        token_info['expires_at'] = datetime.utcnow() + timedelta(minutes=59)
        return True, None
    else:
        return False, response.text
def get_token():
    if token_info['token'] is None or datetime.utcnow() >= token_info['expires_at']:
        success, error = create_token()
        if not success:
            return None
    return token_info['token']

class StkPush(Resource):
    @jwt_required()
    def post(self):
        token = get_token()
        if token is None:
            return jsonify({'error': 'Failed to get token'}), 500

        request_data = request.get_json()
        phone = request_data.get('phone')
        amount = request_data.get('amount')
        user_id = get_jwt_identity()

        if not phone or not amount:
            return jsonify({'error': 'Phone number and amount are required'}), 400

        phone = phone.lstrip('0') 
        short_code = 174379
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

        now = datetime.now()
        timestamp = now.strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f"{short_code}{passkey}{timestamp}".encode()).decode()

        data = {
            'BusinessShortCode': short_code,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': f"254{phone}",
            'PartyB': short_code,
            'PhoneNumber': f"254{phone}",
            'CallBackURL': 'https://mydomain.com/path',
            'AccountReference': 'NairobiKonnect',
            'TransactionDesc': 'Testing stk push'
        }

        headers = {
            'Authorization': f'Bearer {token}'
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # Raise an error for bad responses

            response_data = response.json()
            transaction_id = response_data.get('CheckoutRequestID')

            # Save payment to database
            try:
                new_subscription = Subscription(
                    user_id=user_id,
                    payment_status='Paid',
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=30) 
                )
                db.session.add(new_subscription)
                db.session.commit()  # Commit to get the subscription ID

                new_payment = Payment(
                    user_id=user_id,
                    amount=amount,
                    transaction_id=transaction_id,
                    status='completed',  # Set status to completed
                    subscription_id=new_subscription.id  # Set subscription ID
                )
                db.session.add(new_payment)
                db.session.commit()
                
                return make_response(jsonify({'message': 'Payment completed successfully', 'transaction_id': transaction_id, 'subscription_id': new_subscription.id}), 200)
            except Exception as e:
                db.session.rollback()
                return make_response(jsonify({'error': f'Failed to save payment or subscription to database: {str(e)}'}), 500)
        
        except requests.RequestException as e:
            return make_response(jsonify({'error': f'Error with STK Push request: {str(e)}'}), 500)

   