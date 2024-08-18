from flask import request, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from model import db, Driver
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DriverResource(Resource):
    
    only = ('id', 'name', 'email', 'contact_info')

    def post(self):
        """
        Create a new driver.
        """
        data = request.get_json()

        # Input validation
        required_fields = ['name', 'email', 'contact_info']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return make_response(json.dumps({
                "message": "Missing required fields",
                "status": "fail",
                "missing_fields": missing_fields
            }), 400, {'Content-Type': 'application/json'})

        # Check if the contact_info already exists
        existing_driver = Driver.query.filter_by(contact_info=data.get('contact_info')).first()
        if existing_driver:
            return make_response(json.dumps({
                "message": "Driver with this contact info already exists.",
                "status": "fail"
            }), 400, {'Content-Type': 'application/json'})

        new_driver = Driver(
            name=data.get('name').strip(),
            email=data.get('email').strip().lower(),
            contact_info=data.get('contact_info').strip()
        )

        try:
            db.session.add(new_driver)
            db.session.commit()

            # Log successful creation
            logger.info(f"New driver created: {new_driver.to_dict()}")

            return make_response(json.dumps({
                "message": "Driver created successfully",
                "status": "success",
                "driver": new_driver.to_dict()
            }), 201, {'Content-Type': 'application/json'})

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"IntegrityError: {e}")
            return make_response(json.dumps({
                "message": "Error creating driver, contact info must be unique.",
                "status": "fail",
                "error": str(e)
            }), 400, {'Content-Type': 'application/json'})

        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error creating driver: {e}")
            return make_response(json.dumps({
                "message": "Unexpected error occurred while creating driver.",
                "status": "fail",
                "error": str(e)
            }), 500, {'Content-Type': 'application/json'})

    def get(self, driver_id=None):
        
        
        """
        Retrieve a specific driver by ID or all drivers if no ID is provided.
        """
        try:
            if driver_id:
                driver = Driver.query.get(driver_id)
                if not driver:
                    return make_response(json.dumps({
                        "message": "Driver not found",
                        "status": "fail"
                    }), 404, {'Content-Type': 'application/json'})

                return make_response(json.dumps(driver.to_dict(only=self.only)), 200, {'Content-Type': 'application/json'})
            
            # Retrieve all drivers
            drivers = Driver.query.all()
            return make_response(json.dumps([driver.to_dict(only=self.only) for driver in drivers]), 200, {'Content-Type': 'application/json'})

        except Exception as e:
            logger.error(f"Error retrieving driver(s): {e}")
            return make_response(json.dumps({
                "message": "Error retrieving driver(s)",
                "status": "fail",
                "error": str(e)
            }), 500, {'Content-Type': 'application/json'})

    def put(self, driver_id):
        """
        Update an existing driver's details.
        """
        data = request.get_json()

        try:
            driver = Driver.query.get(driver_id)
            if not driver:
                return make_response(json.dumps({
                    "message": "Driver not found",
                    "status": "fail"
                }), 404, {'Content-Type': 'application/json'})

            # Update fields if provided
            driver.name = data.get('name', driver.name).strip()
            driver.email = data.get('email', driver.email).strip().lower()
            driver.contact_info = data.get('contact_info', driver.contact_info).strip()

            db.session.commit()

            logger.info(f"Driver updated: {driver.to_dict()}")

            return make_response(json.dumps({
                "message": "Driver updated successfully",
                "status": "success",
                "driver": driver.to_dict()
            }), 200, {'Content-Type': 'application/json'})

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"IntegrityError during update: {e}")
            return make_response(json.dumps({
                "message": "Error updating driver, contact info must be unique.",
                "status": "fail",
                "error": str(e)
            }), 400, {'Content-Type': 'application/json'})

        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error updating driver: {e}")
            return make_response(json.dumps({
                "message": "Unexpected error occurred while updating driver.",
                "status": "fail",
                "error": str(e)
            }), 500, {'Content-Type': 'application/json'})

    def delete(self, driver_id):
        """
        Delete a driver by ID.
        """
        try:
            driver = Driver.query.get(driver_id)
            if not driver:
                return make_response(json.dumps({
                    "message": "Driver not found",
                    "status": "fail"
                }), 404, {'Content-Type': 'application/json'})

            db.session.delete(driver)
            db.session.commit()

            logger.info(f"Driver deleted: {driver.to_dict()}")

            return make_response(json.dumps({
                "message": "Driver deleted successfully",
                "status": "success"
            }), 200, {'Content-Type': 'application/json'})

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting driver: {e}")
            return make_response(json.dumps({
                "message": "Unexpected error occurred while deleting driver.",
                "status": "fail",
                "error": str(e)
            }), 500, {'Content-Type': 'application/json'})
