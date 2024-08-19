#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/scientists', methods=['GET'])
def get_scientists():
    scientists = Scientist.query.all()
    scientists_list = [scientist.to_dict(only=('id', 'name', 'field_of_study')) for scientist in scientists]
    return jsonify(scientists_list), 200

@app.route('/scientists/<int:id>', methods=['GET'])
def get_scientist_by_id(id):
    scientist = Scientist.query.get(id)
    if scientist:
        return jsonify(scientist.to_dict(only=('id', 'name', 'field_of_study', 'missions', 'missions.name', 'missions.planet', 'missions.planet.id', 'missions.planet.name', 'missions.planet.distance_from_earth', 'missions.planet.nearest_star'))), 200
    else:
        return jsonify({"error": "Scientist not found"}), 404

@app.route('/scientists/<int:id>', methods=['DELETE'])
def delete_scientist(id):
    scientist = Scientist.query.get(id)
    if scientist:
        db.session.delete(scientist)
        db.session.commit()
        return jsonify({}), 204  # Return an empty JSON object with 204 status
    else:
        return jsonify({"error": "Scientist not found"}), 404


@app.route('/scientists', methods=['POST'])
def create_scientist():
    data = request.get_json()

    # Validate the data
    if 'name' not in data or 'field_of_study' not in data:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        # Create a new Scientist instance
        scientist = Scientist(name=data['name'], field_of_study=data['field_of_study'])
        
        # Add the scientist to the database
        db.session.add(scientist)
        db.session.commit()

        # Return the newly created scientist
        return jsonify(scientist.to_dict(only=('id', 'name', 'field_of_study', 'missions'))), 201

    except Exception as e:
        # If there's any error, return a validation error response
        return jsonify({"errors": ["validation errors"]}), 400

@app.route('/scientists/<int:id>', methods=['PATCH'])
def update_scientist(id):
    scientist = Scientist.query.get(id)
    if not scientist:
        return jsonify({"error": "Scientist not found"}), 404

    data = request.get_json()

    try:
        # Update the scientist fields if they are provided in the request
        if 'name' in data:
            scientist.name = data['name']
        if 'field_of_study' in data:
            scientist.field_of_study = data['field_of_study']

        # Save changes to the database
        db.session.commit()

        # Return the updated scientist with a 202 Accepted status
        return jsonify(scientist.to_dict(only=('id', 'name', 'field_of_study', 'missions'))), 202
    
    except ValueError:
        # Return a generic validation error message as expected by the test
        return jsonify({"errors": ["validation errors"]}), 400

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets_list = [planet.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star')) for planet in planets]
    return jsonify(planets_list), 200

@app.route('/missions', methods=['POST'])
def create_mission():
    data = request.get_json()

    # Validate the required fields
    if not all(key in data for key in ['name', 'scientist_id', 'planet_id']):
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        # Create a new Mission instance
        mission = Mission(
            name=data['name'],
            scientist_id=data['scientist_id'],
            planet_id=data['planet_id']
        )

        # Add the mission to the database
        db.session.add(mission)
        db.session.commit()

        # Return the newly created mission with the associated scientist and planet
        return jsonify(mission.to_dict(only=(
            'id', 'name', 'scientist_id', 'planet_id',
            'scientist', 'planet',
            'planet.id', 'planet.name', 'planet.distance_from_earth', 'planet.nearest_star',
            'scientist.id', 'scientist.name', 'scientist.field_of_study'
        ))), 201

    except Exception as e:
        # If there's any error, return a validation error response
        return jsonify({"errors": ["validation errors"]}), 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
