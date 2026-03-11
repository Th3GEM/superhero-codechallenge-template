from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from models import db, Hero, Power, HeroPower

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)


# GET /heroes
@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([{
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name
    } for hero in heroes])


# GET /heroes/:id
@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({"error": "Hero not found"}), 404

    return jsonify({
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "hero_powers": [{
            "id": hp.id,
            "strength": hp.strength,
            "power": {
                "id": hp.power.id,
                "name": hp.power.name,
                "description": hp.power.description
            }
        } for hp in hero.hero_powers]
    })


# GET /powers
@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([{
        "id": power.id,
        "name": power.name,
        "description": power.description
    } for power in powers])


# GET /powers/:id
@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    return jsonify({
        "id": power.id,
        "name": power.name,
        "description": power.description
    })


# PATCH /powers/:id
@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    try:
        power.description = data['description']
        db.session.commit()
    except Exception:
        return jsonify({"errors": ["validation errors"]}), 400

    return jsonify({
        "id": power.id,
        "name": power.name,
        "description": power.description
    })


# POST /hero_powers
@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    try:
        hero_power = HeroPower(
            strength=data['strength'],
            hero_id=data['hero_id'],
            power_id=data['power_id']
        )
        db.session.add(hero_power)
        db.session.commit()
    except Exception:
        return jsonify({"errors": ["validation errors"]}), 400

    return jsonify({
        "id": hero_power.id,
        "hero_id": hero_power.hero_id,
        "power_id": hero_power.power_id,
        "strength": hero_power.strength,
        "hero": {
            "id": hero_power.hero.id,
            "name": hero_power.hero.name,
            "super_name": hero_power.hero.super_name
        },
        "power": {
            "id": hero_power.power.id,
            "name": hero_power.power.name,
            "description": hero_power.power.description
        }
    }), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)