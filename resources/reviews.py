from flask import request
from flask_restful import Resource
from model import db, Review

class ReviewRescource(Resource):
    def get(self):
        reviews = Review.query.all()
        return [review.to_dict() for review in reviews], 200
    
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
    
    def delete(self, id):
        review = Review.query.get_or_404(id)
        db.session.delete(review)
        db.session.commit()
        return {"message": "Review deleted successfully"}, 200
    

