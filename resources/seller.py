from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from model import db, User, Product, OrderItem, Order
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SellerResource(Resource):
    @jwt_required()
    def post(self):
        """Add or update product stock"""
        data = request.get_json()
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'seller':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            product = Product.query.filter_by(name=data['name'], artisan_id=user_id).first()

            if product:
                product.description = data['description']
                product.price = data['price']
                product.available_quantity = data['available_quantity']
                product.shop_name = data['shop_name']
                product.location = data['location']
            else:
                product = Product(
                    name=data['name'],
                    description=data['description'],
                    price=data['price'],
                    available_quantity=data['available_quantity'],
                    artisan_id=user_id,
                    shop_name=data['shop_name'],
                    location=data['location']
                )
                db.session.add(product)

            db.session.commit()
            return {"message": "Stock updated successfully", "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error adding/updating stock: {e}")
            return {"message": "Error adding/updating stock", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def get(self):
        """View orders for the seller's products"""
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'seller':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            products = Product.query.filter_by(artisan_id=user_id).all()
            product_ids = [product.id for product in products]
            order_items = OrderItem.query.filter(OrderItem.product_id.in_(product_ids)).all()
            order_ids = [item.order_id for item in order_items]
            orders = Order.query.filter(Order.id.in_(order_ids)).all()

            order_data = []
            for order in orders:
                total_amount = sum(item.unit_price * item.quantity for item in order_items if item.order_id == order.id)
                order_data.append({
                    "order_id": order.id,
                    "total_amount": total_amount,
                    "status": order.status,
                    "created_at": order.created_at
                })

            return {"orders": order_data}, 200
        except Exception as e:
            logger.error(f"Error retrieving orders: {e}")
            return {"message": "Error retrieving orders", "status": "fail", "error": str(e)}, 500
