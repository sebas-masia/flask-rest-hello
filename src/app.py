"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    users = User.query.all()
    all_user = list(map(lambda x: x.serialize(), users))

    return jsonify(all_user), 200

@app.route('/user/favorites', methods=['GET'])
def handle_favorites():
    user = User.query.get(1)
    if not user:
        raise APIException("User not found", status_code=404)
    
    favorite_people = list(map(lambda x: x.serialize(), user.favorite_people))
    favorite_planets = list(map(lambda x: x.serialize(), user.favorite_planets))

    favorites = {
        "favorite_people": favorite_people,
        "favorite_planets": favorite_planets
    }

    return jsonify(favorites), 200

@app.route('/favorite/planet/<int:id>', methods=['POST'])
def handle_favorite_planet(id):
    user = User.query.get(1)
    if not user:
        raise APIException("User not found", status_code=404)

    planet = Planets.query.get(id)
    if not planet:
        raise APIException("Planet not found", status_code=404)

    user.favorite_planets.append(planet)
    db.session.commit()

    return jsonify("success"), 200

@app.route('/favorite/people/<int:id>', methods=['POST'])
def handle_favorite_people(id):
    user = User.query.get(1)
    if not user:
        raise APIException("User not found", status_code=404)

    people = People.query.get(id)
    if not people:
        raise APIException("People not found", status_code=404)

    user.favorite_people.append(people)
    db.session.commit()

    return jsonify("success"), 200

@app.route('/favorite/planet/<int:id>', methods=['DELETE'])
def handle_delete_favorite_planet(id):
    user = User.query.get(1)
    if not user:
        raise APIException("User not found", status_code=404)

    planet = Planets.query.get(id)
    if not planet:
        raise APIException("Planet not found", status_code=404)

    user.favorite_planets.remove(planet)
    db.session.commit()

    return jsonify("success"), 200

@app.route('/favorite/people/<int:id>', methods=['DELETE'])
def handle_delete_favorite_people(id):
    user = User.query.get(1)
    if not user:
        raise APIException("User not found", status_code=404)

    people = People.query.get(id)
    if not people:
        raise APIException("People not found", status_code=404)

    user.favorite_people.remove(people)
    db.session.commit()

    return jsonify("success"), 200

@app.route('/people', methods=['GET'])
def handle_people():

    people = People.query.all()
    people = list(map(lambda x: x.serialize(), people))

    return jsonify(people), 200

@app.route('/people/<int:id>', methods=['GET'])
def handle_people_id(id):

    people = People.query.get(id)

    return jsonify(people.serialize()), 200

@app.route('/planets', methods=['GET'])
def handle_planets():

    planets = Planets.query.all()
    planets = list(map(lambda x: x.serialize(), planets))

    return jsonify(planets), 200

@app.route('/planets/<int:id>', methods=['GET'])
def handle_planets_id(id):

    planets = Planets.query.get(id)

    return jsonify(planets.serialize()), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
