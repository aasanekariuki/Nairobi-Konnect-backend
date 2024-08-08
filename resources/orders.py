from flask import request
from flask_restful import Resource, reqparse
from model import db, Order, OrderItem

class OrderResource(Resource):
    def get(selfc, order_id = None):
        if order_id:
            order = Order.query.get_or_404(order_id)
            return order.to_dict(), 200
        orders = Order.query.all()
        return [order.to_dict() for order in orders], 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('buyer_id', type=int, required=True, help="Buyer ID is required")
        parser.add_argument('total_price', type=float, required=True, help="Total price is required")
        parser.add_argument('status', type=str, default='pending')
        args = parser.parse_args()

        new_order = Order(
            buyer_id=args['buyer_id'],
            total_price=args['total_price'],
            status=args['status']
        )
        db.session.add(new_order)
        db.session.commit()
        return new_order.to_dict(), 201

    def put(self, order_id):
        order = Order.query.get_or_404(order_id)
        parser = reqparse.RequestParser()
        parser.add_argument('total_price', type=float)
        parser.add_argument('status', type=str)
        args = parser.parse_args()

        if args['total_price']:
            order.total_price = args['total_price']
        if args['status']:
            order.status = args['status']

        db.session.commit()
        return order.to_dict(), 200

    def delete(self, order_id):
        order = Order.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        return {'message': 'Order deleted'}, 200
    

class OrderItemsResource(Resource):
    def get(self, order_item_id=None):
        if order_item_id:
            order_item = OrderItem.query.get_or_404(order_item_id)
            return order_item.to_dict(), 200
        order_items = OrderItem.query.all()
        return [item.to_dict() for item in order_items], 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('order_id', type=int, required=True, help="Order ID is required")
        parser.add_argument('product_id', type=int, required=True, help="Product ID is required")
        parser.add_argument('quantity', type=int, required=True, help="Quantity is required")
        parser.add_argument('unit_price', type=float, required=True, help="Unit price is required")
        data = parser.parse_args()

        order_item = OrderItem(
            order_id=data['order_id'],
            product_id=data['product_id'],
            quantity=data['quantity'],
            unit_price=data['unit_price']
        )
        db.session.add(order_item)
        db.session.commit()
        return order_item.to_dict(), 201

    def put(self, order_item_id):
        order_item = OrderItem.query.get_or_404(order_item_id)
        parser = reqparse.RequestParser()
        parser.add_argument('quantity', type=int)
        parser.add_argument('unit_price', type=float)
        data = parser.parse_args()

        if data['quantity']:
            order_item.quantity = data['quantity']
        if data['unit_price']:
            order_item.unit_price = data['unit_price']

        db.session.commit()
        return order_item.to_dict(), 200

    def delete(self, order_item_id):
        order_item = OrderItem.query.get_or_404(order_item_id)
        db.session.delete(order_item)
        db.session.commit()
        return {'message': 'Order item deleted'}, 200
