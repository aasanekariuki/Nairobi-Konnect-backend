from flask import request, jsonify, make_response
from flask_restful import Resource
from model import db, Driver, Route, Ticket
import json

class TicketResource(Resource):
    
    def get(self, driver_id=None, ticket_id=None):
        """
        Get tickets:
        - If `driver_id` is provided, get all tickets for the routes assigned to the specific driver.
        - If `ticket_id` is provided, get details for a specific ticket.
        - If neither is provided, get all tickets.
        """
        try:
            if ticket_id:
                # Fetch a specific ticket
                ticket = Ticket.query.get(ticket_id)
                if not ticket:
                    return make_response(json.dumps({
                        "message": "Ticket not found",
                        "status": "fail"
                    }), 404, {'Content-Type': 'application/json'})

                ticket_data = {
                    "ticket_id": ticket.id,
                    "passenger_id": ticket.passenger_id,
                    "seat_number": ticket.seat_number,
                    "route_id": ticket.route_id,
                }
                return make_response(json.dumps(ticket_data), 200, {'Content-Type': 'application/json'})

            elif driver_id:
                # Fetch all tickets for the routes assigned to a specific driver
                routes = Route.query.filter_by(driver_id=driver_id).all()
                if not routes:
                    return make_response(json.dumps({
                        "message": "No routes found for this driver",
                        "status": "fail"
                    }), 404, {'Content-Type': 'application/json'})

                tickets_data = []
                for route in routes:
                    tickets = Ticket.query.filter_by(route_id=route.id).all()
                    if tickets:
                        tickets_list = [{
                            "ticket_id": ticket.id,
                            "passenger_id": ticket.passenger_id,
                            "seat_number": ticket.seat_number,
                        } for ticket in tickets]

                        tickets_data.append({
                            "route_id": route.id,
                            "start_location": route.start_location,
                            "end_location": route.end_location,
                            "departure_time": route.departure_time,
                            "arrival_time": route.arrival_time,
                            "booked_seats": len(tickets),
                            "tickets": tickets_list,
                        })

                return make_response(json.dumps({"routes": tickets_data}), 200, {'Content-Type': 'application/json'})

            else:
                # Fetch all tickets if no driver_id or ticket_id is provided
                tickets = Ticket.query.all()
                if not tickets:
                    return make_response(json.dumps({
                        "message": "No tickets found",
                        "status": "fail"
                    }), 404, {'Content-Type': 'application/json'})

                tickets_list = [{
                    "ticket_id": ticket.id,
                    "passenger_id": ticket.passenger_id,
                    "seat_number": ticket.seat_number,
                    "route_id": ticket.route_id,
                } for ticket in tickets]

                return make_response(json.dumps({"tickets": tickets_list}), 200, {'Content-Type': 'application/json'})

        except Exception as e:
            return make_response(json.dumps({
                "message": "Error retrieving tickets",
                "status": "fail",
                "error": str(e)
            }), 500, {'Content-Type': 'application/json'})

    def post(self):
        """
        Create a new ticket.
        """
        data = request.get_json()
        try:
            new_ticket = Ticket(
                route_id=data['route_id'],
                passenger_id=data['passenger_id'],
                seat_number=data['seat_number']
            )
            db.session.add(new_ticket)
            db.session.commit()

            return make_response(json.dumps({
                "message": "Ticket created successfully",
                "status": "success",
                "ticket": {
                    "ticket_id": new_ticket.id,
                    "route_id": new_ticket.route_id,
                    "passenger_id": new_ticket.passenger_id,
                    "seat_number": new_ticket.seat_number,
                }
            }), 201, {'Content-Type': 'application/json'})

        except Exception as e:
            db.session.rollback()
            return make_response(json.dumps({
                "message": "Error creating ticket",
                "status": "fail",
                "error": str(e)
            }), 500, {'Content-Type': 'application/json'})

    def delete(self, ticket_id):
        """
        Delete a ticket by ID.
        """
        try:
            ticket = Ticket.query.get(ticket_id)
            if not ticket:
                return make_response(json.dumps({
                    "message": "Ticket not found",
                    "status": "fail"
                }), 404, {'Content-Type': 'application/json'})

            db.session.delete(ticket)
            db.session.commit()

            return make_response(json.dumps({
                "message": "Ticket deleted successfully",
                "status": "success"
            }), 200, {'Content-Type': 'application/json'})

        except Exception as e:
            db.session.rollback()
            return make_response(json.dumps({
                "message": "Error deleting ticket",
                "status": "fail",
                "error": str(e)
            }), 500, {'Content-Type': 'application/json'})
