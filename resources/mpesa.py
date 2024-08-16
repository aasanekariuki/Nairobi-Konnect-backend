import os
from dotenv import load_dotenv
from flask import request, Response
from flask_restful import Resource
import base64
import requests
from datetime import datetime, timedelta
from model import db, Payment
from flask_jwt_extended import jwt_required, get_jwt_identity
import json

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
            response_body = json.dumps({'error': 'Failed to get token'})
            return Response(response=response_body, status=500, mimetype='application/json')

        request_data = request.get_json()
        phone = request_data.get('phone')
        amount = request_data.get('amount')
        user_id = get_jwt_identity()

        if not phone or not amount:
            response_body = json.dumps({'error': 'Phone number and amount are required'})
            return Response(response=response_body, status=400, mimetype='application/json')

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
                new_payment = Payment(
                    user_id=user_id,
                    amount=amount,
                    transaction_id=transaction_id,
                    status='completed'  # Set status to completed
                )
                db.session.add(new_payment)
                db.session.commit()
                
                response_body = json.dumps({'message': 'Payment completed successfully', 'transaction_id': transaction_id})
                return Response(response=response_body, status=200, mimetype='application/json')
            except Exception as e:
                db.session.rollback()
                response_body = json.dumps({'error': f'Failed to save payment to database: {str(e)}'})
                return Response(response=response_body, status=500, mimetype='application/json')
        
        except requests.RequestException as e:
            response_body = json.dumps({'error': f'Error with STK Push request: {str(e)}'})
            return Response(response=response_body, status=500, mimetype='application/json')
