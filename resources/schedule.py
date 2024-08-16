from flask import request
from flask_restful import Resource
from model import Schedule, db

class ScheduleResource(Resource):
    only = ('id', 'bus_id', 'route_id', 'departure_time', 'arrival_time', 'date', 'available_seats', 'created_at', 'updated_at')
    def get(self, schedule_id=None):
        if schedule_id:
            schedule = Schedule.query.get_or_404(schedule_id)
            return schedule.to_dict(), 200
        else:
            schedules = Schedule.query.all()
            return [schedule.to_dict(only=self.only) for schedule in schedules], 200

    def post(self):
        data = request.get_json()
        new_schedule = Schedule(
            bus_id=data['bus_id'],
            route_id=data['route_id'],
            departure_time=data['departure_time'],
            arrival_time=data['arrival_time'],
            date=data['date'],
            available_seats=data['available_seats']
        )
        db.session.add(new_schedule)
        db.session.commit()
        return new_schedule.to_dict(), 201

    def put(self, schedule_id):
        schedule = Schedule.query.get_or_404(schedule_id)
        data = request.get_json()
        schedule.bus_id = data['bus_id']
        schedule.route_id = data['route_id']
        schedule.departure_time = data['departure_time']
        schedule.arrival_time = data['arrival_time']
        schedule.date = data['date']
        schedule.available_seats = data['available_seats']
        db.session.commit()
        return schedule.to_dict(), 200

    def delete(self, schedule_id):
        schedule = Schedule.query.get_or_404(schedule_id)
        db.session.delete(schedule)
        db.session.commit()
        return {'message': 'Schedule deleted'}, 200
