from flask import request, Response
from flask_restful import Resource
import json
from model import Product, Stall, db

class ProductResource(Resource):
    only = ('id', 'name', 'description', 'price', 'available_quantity', 'image_url', 'stall_id', 'created_at', 'location')

    def get(self, stall_name=None):
        if stall_name:
            # Fetch the stall by its name
            stall = Stall.query.filter_by(stall_name=stall_name).first()
            if not stall:
                return Response(json.dumps({'message': f"No stall found with the name '{stall_name}'."}), status=404, mimetype='application/json')
            
            # Fetch products by stall_id
            products = Product.query.filter_by(stall_id=stall.id).all()
            products_list = [product.to_dict(only=self.only) for product in products]
            
            # Convert to JSON and return response
            return Response(json.dumps(products_list), status=200, mimetype='application/json')
        else:
            # Fetch all products if no stall_name is provided
            products = Product.query.all()
            products_list = [product.to_dict(only=self.only) for product in products]
            
            # Convert to JSON and return response
            return Response(json.dumps(products_list), status=200, mimetype='application/json')

    def post(self):
        data = request.get_json()
        stall = Stall.query.filter_by(stall_name=data['shop_name']).first()
        if not stall:
            return Response(json.dumps({'message': f"No stall found with the name '{data['shop_name']}'."}), status=404, mimetype='application/json')
        
        new_product = Product(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            available_quantity=data['available_quantity'],
            stall_id=stall.id,
            location_point=data.get('location_point'),
        )
        db.session.add(new_product)
        db.session.commit()
        return Response(json.dumps(new_product.to_dict()), status=201, mimetype='application/json')

    def put(self, product_id):
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        product.name = data['name']
        product.description = data.get('description')
        product.price = data['price']
        product.available_quantity = data['available_quantity']
        product.location_point = data.get('location_point')

        stall = Stall.query.filter_by(stall_name=data['stall_name']).first()
        if stall:
            product.stall_id = stall.id
        
        db.session.commit()
        return Response(json.dumps(product.to_dict()), status=200, mimetype='application/json')

    def delete(self, product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return Response(json.dumps({'message': 'Product deleted'}), status=200, mimetype='application/json')
