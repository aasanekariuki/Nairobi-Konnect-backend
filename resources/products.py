from flask import request
from flask_restful import Resource
from model import Product, db

class ProductResource(Resource):
    only = ('id', 'name', 'description', 'price', 'available_quantity', 'image_url', 'stall_id' , 'created_at', 'location', 'shop_name')
         
    def get(self, product_id = None):
        if product_id:
            product = Product.query.get_or_404(product_id)
            return product.to_dict(only= self.only), 200

        else:
            products = Product.query.all()
            return [product.to_dict(only=self.only) for product in products], 200
        
    
    def post(self):
        data = request.get_json()
        new_product = Product(
            name = data['name'],
            description = data.get('description'),
            price = data['price'],
            available_quantity = data['available_quantity'],
            artisan_id = data['artisan_id'],
            location_point = data.get('location_point'),
            shop_name = data['shop_name']
        )
        db.session.add(new_product)
        db.session.commit()
        return new_product.to_dict(), 201
    
    
    def put(self, product_id):
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        product.name = data['name']
        product.description = data.get('description')
        product.price = data['price']
        product.available_quantity = data['available_quantity']
        product.location_point = data.get('location_point')
        product.shop_name = data['shop_name']
        db.session.commit()
        return product.to_dict(), 200
    
    
    def delete(self, product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return {'message': 'Product deleted'}, 200