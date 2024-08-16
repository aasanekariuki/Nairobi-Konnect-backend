from flask import request
from flask_restful import Resource
from model import Route, db

class RouteResource(Resource):
    only = ('id', 'origin', 'description', 'created_at', 'updated_at',)
    def get(self, route_id=None):
        if route_id:
            route = Route.query.get_or_404(route_id)
            return route.to_dict(), 200
        else:
            routes = Route.query.all()
            return [route.to_dict(only=self.only) for route in routes], 200

    def post(self):
        data = request.get_json()
        new_route = Route(
            origin=data['origin'],
            destination=data['destination'],
            description=data.get('description')
        )
        db.session.add(new_route)
        db.session.commit()
        return new_route.to_dict(), 201

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
