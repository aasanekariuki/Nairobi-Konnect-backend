import os
from dotenv import load_dotenv
from flask import request, make_response, jsonify
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
        token_info['token'] = data.get('access_token')
        token_info['expires_at'] = datetime.utcnow() + timedelta(seconds=int(data.get('expires_in')))
        return True, None
    else:
        print(f"Failed to create token: {response.text}")
        return False, response.text

def get_token():
    if token_info['token'] is None or datetime.utcnow() >= token_info['expires_at']:
        success, error = create_token()
        if not success:
            print(f"Error obtaining token: {error}")
            return None
    return token_info['token']

class StkPush(Resource):
    @jwt_required()
    def post(self):
        token = get_token()
        if token is None:
            return make_response(jsonify({'error': 'Failed to get token'}), 500)

        request_data = request.get_json()

        # Log the incoming request data for debugging
        print("Received data:", request_data)

        phone = request_data.get('phone')
        amount = request_data.get('amount')
        user_id = get_jwt_identity()

        if not phone or not amount:
            return make_response(jsonify({'error': 'Phone number and amount are required'}), 400)

        # Validate the amount
        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
        except ValueError as e:
            print(f"Amount validation error: {e}")
            return make_response(jsonify({'error': 'Invalid amount provided. Amount must be a positive integer.'}), 400)

        # Format phone number correctly
        phone = phone.lstrip('0')
        phone = f"254{phone}"

        short_code = '174379'
        passkey = os.getenv('PASSKEY')
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
            'PartyA': phone,
            'PartyB': short_code,
            'PhoneNumber': phone,
            'CallBackURL': 'https://mydomain.com/path',
            'AccountReference': 'NairobiKonnect',
            'TransactionDesc': 'Payment for NairobiKonnect services'
        }

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code != 200:
                print(f"STK Push request failed with status code {response.status_code}")
                print(f"Response content: {response.text}")
                return make_response(jsonify({'error': 'Failed to process payment request. Please try again later.'}), 500)

            response_data = response.json()
            transaction_id = response_data.get('CheckoutRequestID')

            # Save payment to the database
            try:
                # Uncomment and modify this block when integrating with your database
                # new_payment = Payment(
                #     user_id=user_id,
                #     amount=amount,
                #     transaction_id=transaction_id,
                #     status='pending'  # Assuming status is pending until callback confirms
                # )
                # db.session.add(new_payment)
                # db.session.commit()

                return make_response(jsonify({'message': 'Payment initiated successfully', 'transaction_id': transaction_id}), 200)

            except Exception as e:
                db.session.rollback()
                print(f"Database Error: {str(e)}")
                return make_response(jsonify({'error': f'Failed to save payment or subscription to database: {str(e)}'}), 500)

        except requests.RequestException as e:
            print(f"RequestException: {str(e)}")
            return make_response(jsonify({'error': f'Error with STK Push request: {str(e)}'}), 500)
