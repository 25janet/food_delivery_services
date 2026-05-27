from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = \
    'postgresql://admin:password@postgres:5432/food_delivery'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -------------------------
# DRIVER MODEL
# -------------------------
class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    vehicle = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='available')


# -------------------------
# CREATE DRIVER
# -------------------------
@app.route('/drivers', methods=['POST'])
def create_driver():
    data = request.get_json()

    driver = Driver(
        name=data['name'],
        vehicle=data['vehicle'],
        status='available'
    )

    db.session.add(driver)
    db.session.commit()

    return jsonify({
        'id': driver.id,
        'name': driver.name,
        'vehicle': driver.vehicle,
        'status': driver.status
    }), 201


# -------------------------
# GET DRIVERS
# -------------------------
@app.route('/drivers', methods=['GET'])
def get_drivers():
    drivers = Driver.query.all()

    result = []

    for d in drivers:
        result.append({
            'id': d.id,
            'name': d.name,
            'vehicle': d.vehicle,
            'status': d.status
        })

    return jsonify(result)


# -------------------------
# CREATE TABLES
# -------------------------
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)