import dbm
from flask import jsonify,make_response, request
from flask_restful import Resource
from model import Payment
from flask_jwt_extended import jwt_required

class PaymentStatusResource(Resource):
    @jwt_required()
    def get(self, transaction_id):
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if payment:
            return make_response(jsonify({'status': payment.status}), 200)
        else:
            return make_response(jsonify({'error': 'Payment not found'}), 404)
        
        
    @jwt_required()
    def post(self):
        
        data = request.get_json()
        new_payment = Payment(
        transaction_id=data['transaction_id'],
        amount=data['amount'],
        status=data['status']  # Initially could be 'pending' or similar
        )
        
        db.session.add(new_payment)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Payment created successfully'}), 201)

        
        
    
