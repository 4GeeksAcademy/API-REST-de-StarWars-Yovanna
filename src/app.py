import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

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

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    return jsonify({"msg": "Hello, this is your GET /user response"}), 200

@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    return jsonify([p.serialize() for p in people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_single_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = 1
    favorites = Favorite.query.filter_by(user_id=current_user_id).all()
    return jsonify([f.serialize() for f in favorites]), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = 1
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"error": "Planet not found"}), 404
    new_fav = Favorite(user_id=current_user_id, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Planet added to favorites"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    current_user_id = 1
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"error": "Person not found"}), 404
    new_fav = Favorite(user_id=current_user_id, people_id=people_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Person added to favorites"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user_id = 1
    fav = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if fav is None:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Planet favorite deleted"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    current_user_id = 1
    fav = Favorite.query.filter_by(user_id=current_user_id, people_id=people_id).first()
    if fav is None:
        return jsonify({"error": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "People favorite deleted"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
