from flask import request
from flask_restful import Resource
from model import Stall, db

class StallResource(Resource):
    def get(self, stall_id=None):
        if stall_id:
            stall = Stall.query.get_or_404(stall_id)
            return stall.to_dict(), 200
        else:
            stalls = Stall.query.all()
            return [stall.to_dict() for stall in stalls], 200

    def post(self):
        data = request.get_json()
        new_stall = Stall(
            seller_id=data['seller_id'],
            stall_name=data['stall_name'],
            description=data.get('description'),
            location=data['location'],
            image_url=data['image_url']
        )
        db.session.add(new_stall)
        db.session.commit()
        return new_stall.to_dict(), 201

    def put(self, stall_id):
        stall = Stall.query.get_or_404(stall_id)
        data = request.get_json()
        stall.stall_name = data['stall_name']
        stall.description = data.get('description')
        stall.location = data['location']
        stall.image_url = data['image_url']
        db.session.commit()
        return stall.to_dict(), 200

    def delete(self, stall_id):
        stall = Stall.query.get_or_404(stall_id)
        db.session.delete(stall)
        db.session.commit()
        return {'message': 'Stall deleted'}, 200
