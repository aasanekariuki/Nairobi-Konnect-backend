from flask import request, jsonify
from flask_restful import Resource
from model import db, Review
from flask_jwt_extended import jwt_required


class ReviewResource(Resource):
    @jwt_required()
    def get(self, review_id):
        # Retrieve a single review by ID
        review = Review.query.get(review_id)
        if not review:
            return {'message': 'Review not found'}, 404
        
        return jsonify(review.to_dict())
    

    @jwt_required()
    def post(self):
        data = request.get_json()

        new_review = Review(
            user_id = data['user_id'],
            product_id = data['product_id'],
            rating = data['rating'],
            comment = data.get('comment', '')
        )
        
        
        db.session.add(new_review)
        db.session.commit()
        return new_review.to_dict(), 201
    
    @jwt_required()
    def delete(self):
        # Delete a review by ID
        data = request.get_json()
        review_id = data.get('review_id')
        
        review = Review.query.get(review_id)
        if not review:
            return {'message': 'Review not found'}, 404
        
        db.session.delete(review)
        db.session.commit()
        
        return {'message': 'Review deleted successfully'}, 200


