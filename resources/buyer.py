from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, User, Product, Order, OrderItem
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BuyerResource(Resource):
    @jwt_required()
    def post(self):
        """Place an order for products"""
        data = request.get_json()
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'buyer':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            product = Product.query.get(data['product_id'])
            if not product or product.available_quantity < data['quantity']:
                return {"message": "Product not available or insufficient quantity", "status": "fail"}, 400

            order = Order(user_id=user_id, total_price=product.price * data['quantity'])
            db.session.add(order)
            db.session.commit()

            order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=data['quantity'], unit_price=product.price)
            db.session.add(order_item)
            product.available_quantity -= data['quantity']
            db.session.commit()

            return {"message": "Order placed successfully", "status": "success"}, 200
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {"message": "Error placing order", "status": "fail", "error": str(e)}, 500

    @jwt_required()
    def get(self):
        """View the buyer's orders"""
        user_id = get_jwt_identity()['id']

        try:
            user = User.query.get(user_id)
            if user.role != 'buyer':
                return {"message": "Unauthorized access", "status": "fail"}, 403

            orders = Order.query.filter_by(user_id=user_id).all()
            order_data = []
            for order in orders:
                items = OrderItem.query.filter_by(order_id=order.id).all()
                item_data = [{"product_id": item.product_id, "quantity": item.quantity, "unit_price": item.unit_price} for item in items]
                order_data.append({
                    "order_id": order.id,
                    "total_price": order.total_price,
                    "items": item_data,
                    "status": order.status,
                    "created_at": order.created_at
                })

            return {"orders": order_data}, 200
        except Exception as e:
            logger.error(f"Error retrieving orders: {e}")
            return {"message": "Error retrieving orders", "status": "fail", "error": str(e)}, 500
