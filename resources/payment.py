from flask import jsonify, make_response, request
from flask_restful import Resource
from model import Payment, db  # Ensure db is imported from your model or elsewhere
from flask_jwt_extended import jwt_required

class PaymentStatusResource(Resource):
    @jwt_required()
    def get(self, transaction_id):
        # Fetch the payment record by transaction_id
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if payment:
            # If payment is found, return its status
            return make_response(jsonify({'status': payment.status}), 200)
        else:
            # If payment is not found, return a 404 error
            return make_response(jsonify({'error': 'Payment not found'}), 404)
        
    @jwt_required()
    def post(self):
        # Parse the JSON request data
        data = request.get_json()

        if not data or not all(key in data for key in ('transaction_id', 'amount', 'status')):
            # Validate that all required fields are present
            return make_response(jsonify({'error': 'Invalid data'}), 400)

        # Create a new Payment record
        new_payment = Payment(
            transaction_id=data['transaction_id'],
            amount=data['amount'],
            status=data['status']  # Initially could be 'pending' or similar
        )
        
        try:
            # Add the new payment record to the session and commit it to the database
            db.session.add(new_payment)
            db.session.commit()
            return make_response(jsonify({'message': 'Payment created successfully'}), 201)
        except Exception as e:
            # If there's an error, rollback the session
            db.session.rollback()
            return make_response(jsonify({'error': str(e)}), 500)

