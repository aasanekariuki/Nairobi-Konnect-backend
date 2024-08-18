from flask import request, jsonify
from flask_restful import Resource
from model import Route, db

class RouteResource(Resource):
    only = ('id', 'origin', 'destination','description', 'created_at', 'updated_at',)
    def get(self, route_id=None):
        if route_id:
            route = Route.query.get_or_404(route_id)
            return route.to_dict(), 200
        else:
            routes = Route.query.all()
            return [route.to_dict(only=self.only) for route in routes], 200

    def post(self):
        data = request.get_json()

        # Check for missing required fields
        required_fields = ['origin', 'destination']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'message': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400

        new_route = Route(
            origin=data['origin'],
            destination=data['destination'],
            description=data.get('description')  # Optional field, so using get()
        )
        
        db.session.add(new_route)
        db.session.commit()
        
        return jsonify(new_route.to_dict()), 201


    def put(self, route_id):
        route = Route.query.get_or_404(route_id)
        data = request.get_json()
        route.origin = data['origin']
        route.destination = data['destination']
        route.description = data.get('description')
        db.session.commit()
        return route.to_dict(), 200

    def delete(self, route_id):
        route = Route.query.get_or_404(route_id)
        db.session.delete(route)
        db.session.commit()
        return {'message': 'Route deleted'}, 200